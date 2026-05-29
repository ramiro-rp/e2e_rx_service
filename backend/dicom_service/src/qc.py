from __future__ import annotations

from typing import Any, List

import numpy as np

from dicom_service.src.schemas import QCResult
from shared.config import settings


def evaluate_qc(dcm: Any, arr: np.ndarray | None) -> QCResult:
    reject_reasons: List[str] = []
    warnings: List[str] = []

    if not hasattr(dcm, 'PixelData'):
        reject_reasons.append('missing_pixeldata')

    if arr is None or arr.size == 0:
        reject_reasons.append('empty_image')
    else:
        if float(arr.std()) < settings.near_constant_std_threshold:
            reject_reasons.append('near_constant_image')
        if min(arr.shape[:2]) < settings.min_image_size:
            warnings.append('low_resolution')

    modality = getattr(dcm, 'Modality', None)
    if modality is None:
        warnings.append('missing_modality')
    elif modality not in settings.allowed_modalities:
        reject_reasons.append(f'unsupported_modality:{modality}')

    if reject_reasons:
        summary = '; '.join(reject_reasons)
        return QCResult(status='REJECT', reject_reasons=reject_reasons, warnings=warnings, summary=summary)

    status = 'ACCEPT_WITH_WARNINGS' if warnings else 'ACCEPT'
    summary = 'accepted_with_warnings' if warnings else 'accepted'
    return QCResult(status=status, reject_reasons=[], warnings=warnings, summary=summary)
