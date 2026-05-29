from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn

from shared.config import settings


class InferenceModel:
    def __init__(self) -> None:
        self.device = self._resolve_device()
        self.model = self._build_model().to(self.device)
        self.calibration_temperature = self._load_scalar(
            settings.calibration_temperature_path,
            "temperature",
            settings.calibration_temperature_default,
        )
        self.threshold = self._load_scalar(settings.threshold_path, "threshold", settings.threshold_default)
        self.ready = False
        self._load_weights()

    def _resolve_device(self) -> str:
        if settings.device == "cuda" and torch.cuda.is_available():
            return "cuda"
        return "cpu"

    @staticmethod
    def _build_model() -> nn.Module:
        from torchvision import models
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, 1)
        return model

    @staticmethod
    def _load_scalar(path: Path, key: str, default: float) -> float:
        if not path.exists():
            return float(default)
        payload = json.loads(path.read_text(encoding="utf-8"))
        return float(payload.get(key, default))

    def _load_weights(self) -> None:
        if not settings.model_path.exists():
            self.ready = False
            return
        state = torch.load(settings.model_path, map_location=self.device)
        if isinstance(state, dict) and "model_state_dict" in state:
            state = state["model_state_dict"]
        self.model.load_state_dict(state, strict=False)
        self.model.eval()
        self.ready = True

    @torch.no_grad()
    def predict_proba(self, x: torch.Tensor) -> Tuple[float, float]:
        if not self.ready:
            raise RuntimeError(f"Model weights not found at {settings.model_path}")
        x = x.to(self.device)
        logits = self.model(x).squeeze(1)
        calibrated_logits = logits / self.calibration_temperature
        prob = torch.sigmoid(calibrated_logits).item()
        confidence = max(prob, 1.0 - prob)
        return float(prob), float(confidence)
