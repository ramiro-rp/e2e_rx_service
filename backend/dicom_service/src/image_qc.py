from __future__ import annotations

from typing import List

import numpy as np
from PIL import Image

from dicom_service.src.schemas import QCResult
from shared.config import settings


def evaluate_image_qc(img: Image.Image, arr: np.ndarray | None) -> QCResult:
    reject_reasons: List[str] = []
    warnings: List[str] = []

    if arr is None or arr.size == 0:
        reject_reasons.append('empty_image')
    else:
        if float(arr.std()) < settings.near_constant_std_threshold:
            reject_reasons.append('near_constant_image')
        if min(arr.shape[:2]) < settings.min_image_size:
            warnings.append('low_resolution')

    width, height = img.size
    if width < settings.min_image_size or height < settings.min_image_size:
        if 'low_resolution' not in warnings:
            warnings.append('low_resolution')

    if reject_reasons:
        summary = '; '.join(reject_reasons)
        return QCResult(status='REJECT', reject_reasons=reject_reasons, warnings=warnings, summary=summary)

    status = 'ACCEPT_WITH_WARNINGS' if warnings else 'ACCEPT'
    summary = 'accepted_standard_image_with_warnings' if warnings else 'accepted_standard_image'
    return QCResult(status=status, reject_reasons=[], warnings=warnings, summary=summary)
