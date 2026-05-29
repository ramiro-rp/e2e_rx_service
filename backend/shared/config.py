from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / '.env')


def _split_csv(value: str, default: Tuple[str, ...]) -> Tuple[str, ...]:
    if not value:
        return default
    return tuple(part.strip() for part in value.split(',') if part.strip()) or default


def _as_bool(name: str, default: str = 'false') -> bool:
    return os.getenv(name, default).lower() in {'1', 'true', 'yes', 'on'}


@dataclass(frozen=True)
class ServiceSettings:
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[1])
    artifacts_dir: Path = field(default_factory=lambda: Path(os.getenv('SERVICE_ARTIFACTS_DIR', Path(__file__).resolve().parents[1] / 'artifacts')))
    outputs_dir: Path = field(default_factory=lambda: Path(os.getenv('SERVICE_OUTPUTS_DIR', Path(__file__).resolve().parents[1] / 'outputs')))
    model_path: Path = field(default_factory=lambda: Path(os.getenv('SERVICE_MODEL_PATH', Path(__file__).resolve().parents[1] / 'artifacts' / 'checkpoints' / 'best_model.pt')))
    calibration_temperature_path: Path = field(default_factory=lambda: Path(os.getenv('SERVICE_CALIBRATION_TEMPERATURE_PATH', Path(__file__).resolve().parents[1] / 'artifacts' / 'temperature.json')))
    threshold_path: Path = field(default_factory=lambda: Path(os.getenv('SERVICE_THRESHOLD_PATH', Path(__file__).resolve().parents[1] / 'artifacts' / 'threshold.json')))
    device: str = os.getenv('SERVICE_DEVICE', 'cuda')
    image_size: int = int(os.getenv('SERVICE_IMAGE_SIZE', '224'))
    min_image_size: int = int(os.getenv('SERVICE_MIN_IMAGE_SIZE', '128'))
    near_constant_std_threshold: float = float(os.getenv('SERVICE_NEAR_CONSTANT_STD', '1e-6'))
    allowed_modalities: Tuple[str, ...] = field(default_factory=lambda: _split_csv(os.getenv('SERVICE_ALLOWED_MODALITIES', 'CR,DX'), ('CR', 'DX')))
    save_uploaded_dicom: bool = _as_bool('SERVICE_SAVE_UPLOADED_DICOM', 'false')
    save_report_json: bool = _as_bool('SERVICE_SAVE_REPORT_JSON', 'true')
    save_image_outputs: bool = _as_bool('SERVICE_SAVE_IMAGE_OUTPUTS', 'true')
    max_saved_runs: int = int(os.getenv('SERVICE_MAX_SAVED_RUNS', '30'))
    calibration_temperature_default: float = float(os.getenv('SERVICE_CALIBRATION_TEMPERATURE_DEFAULT', '1.0'))
    threshold_default: float = float(os.getenv('SERVICE_THRESHOLD_DEFAULT', '0.5'))
    service_name: str = os.getenv('SERVICE_NAME', 'RSNA DICOM Service MVP')
    service_version: str = os.getenv('SERVICE_VERSION', '0.5.0')
    label_positive: str = os.getenv('SERVICE_LABEL_POSITIVE', 'positive')
    label_negative: str = os.getenv('SERVICE_LABEL_NEGATIVE', 'negative')
    task_name: str = os.getenv('SERVICE_TASK_NAME', 'chest_xray_pneumonia_opacity')
    target_class: str = os.getenv('SERVICE_TARGET_CLASS', 'pneumonia_or_lung_opacity')
    model_name: str = os.getenv('SERVICE_MODEL_NAME', 'resnet18_rsna')
    model_version: str = os.getenv('SERVICE_MODEL_VERSION', 'v1')

    orthanc_enabled: bool = _as_bool('ORTHANC_ENABLED', 'false')
    orthanc_base_url: str = os.getenv('ORTHANC_BASE_URL', 'http://127.0.0.1:8042')
    orthanc_username: str = os.getenv('ORTHANC_USERNAME', 'orthanc')
    orthanc_password: str = os.getenv('ORTHANC_PASSWORD', 'orthanc')
    orthanc_timeout: int = int(os.getenv('ORTHANC_TIMEOUT', '60'))
    orthanc_verify_ssl: bool = _as_bool('ORTHANC_VERIFY_SSL', 'false')
    orthanc_study_list_limit: int = int(os.getenv('ORTHANC_STUDY_LIST_LIMIT', '20'))

    ai_series_description: str = os.getenv('AI_SERIES_DESCRIPTION', 'AI Analysis - RSNA DICOM Service MVP')
    ai_manufacturer: str = os.getenv('AI_MANUFACTURER', 'RSNA DICOM Service MVP')
    ai_model_label: str = os.getenv('AI_MODEL_LABEL', 'Resnet18')


settings = ServiceSettings()
