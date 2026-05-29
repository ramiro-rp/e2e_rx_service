from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Tuple

import numpy as np
from PIL import Image


class DicomReadError(Exception):
    """Raised when the uploaded payload cannot be parsed as a supported DICOM."""


def read_dicom_from_bytes(payload: bytes) -> Any:
    # Fast fail for obviously invalid payloads so the API can return a structured REJECT
    # even before the full DICOM stack is available.
    if len(payload) < 132 and b'\x00' not in payload:
        raise DicomReadError('invalid_dicom')
    try:
        import pydicom
        from pydicom.errors import InvalidDicomError
    except ModuleNotFoundError as exc:
        raise DicomReadError('dicom_runtime_unavailable') from exc
    try:
        return pydicom.dcmread(io.BytesIO(payload), force=False)
    except (InvalidDicomError, EOFError, ValueError) as exc:
        raise DicomReadError('invalid_dicom') from exc


def dicom_to_uint8(dcm: Any) -> np.ndarray:
    from pydicom.pixel_data_handlers.util import apply_voi_lut

    arr = dcm.pixel_array.astype(np.float32)
    try:
        arr = apply_voi_lut(dcm.pixel_array, dcm).astype(np.float32)
    except Exception:
        pass

    if getattr(dcm, "PhotometricInterpretation", "") == "MONOCHROME1":
        arr = np.max(arr) - arr

    lo, hi = np.percentile(arr, (1, 99))
    if hi <= lo:
        lo = float(arr.min())
        hi = float(arr.max()) if float(arr.max()) > lo else lo + 1.0

    arr = np.clip((arr - lo) / (hi - lo), 0, 1)
    return (arr * 255.0).astype(np.uint8)


def dicom_to_pil_and_array(dcm: Any) -> Tuple[Image.Image, np.ndarray]:
    arr = dicom_to_uint8(dcm)
    img = Image.fromarray(arr).convert("RGB")
    return img, arr


def save_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
