
from __future__ import annotations

import io
from types import SimpleNamespace

import numpy as np
from PIL import Image

from dicom_service.src import pipeline as pipeline_module
from dicom_service.src.pipeline import InferencePipeline


class _FakeRuntime:
    def __init__(self) -> None:
        self.threshold = 0.4
        self.calibration_temperature = 0.9
        self.device = 'cpu'
        self.model = SimpleNamespace(layer4=[SimpleNamespace(conv2=object())])

    def predict_proba(self, x):
        return 0.8, 0.8


class _FakeGradCAM:
    def __init__(self, model, target_layer) -> None:
        pass

    def __call__(self, x):
        return np.ones((224, 224), dtype=np.float32) * 0.5

    def close(self) -> None:
        pass


def test_positive_standard_image_generates_transparent_heatmap(monkeypatch):
    monkeypatch.setattr(pipeline_module, 'GradCAM', _FakeGradCAM)

    pipe = InferencePipeline()
    pipe.runtime = _FakeRuntime()

    img = Image.new('RGB', (512, 512), color=(0, 0, 0))
    for i in range(0, 512, 16):
        img.putpixel((i, i), (255, 255, 255))
        img.putpixel((511 - i, i), (255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format='PNG')

    response = pipe.run(buf.getvalue(), filename='positive_like.png')

    assert response.status in {'ACCEPT', 'ACCEPT_WITH_WARNINGS'}
    assert response.prediction.label == 'positive'
    assert response.outputs.original_image_url is not None
    assert response.outputs.transparent_heatmap_url is not None
    assert response.outputs.heatmap_url is not None
    assert response.outputs.overlay_url is not None
    assert response.artifacts.derived_dicom_url is None
