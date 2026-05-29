from types import SimpleNamespace

import numpy as np

from dicom_service.src.qc import evaluate_qc


def _base_dataset(modality='DX'):
    return SimpleNamespace(
        Modality=modality,
        Rows=256,
        Columns=256,
        PhotometricInterpretation='MONOCHROME2',
        PixelData=b'1',
    )


def test_qc_accepts_valid_image():
    ds = _base_dataset()
    arr = np.random.rand(256, 256).astype(np.float32)
    result = evaluate_qc(ds, arr)
    assert result.status == 'ACCEPT'


def test_qc_rejects_missing_pixeldata():
    ds = SimpleNamespace(Modality='DX')
    arr = np.random.rand(256, 256).astype(np.float32)
    result = evaluate_qc(ds, arr)
    assert result.status == 'REJECT'
    assert 'missing_pixeldata' in result.reject_reasons


def test_qc_rejects_unsupported_modality():
    ds = _base_dataset(modality='MR')
    arr = np.random.rand(256, 256).astype(np.float32)
    result = evaluate_qc(ds, arr)
    assert result.status == 'REJECT'
    assert any(reason.startswith('unsupported_modality') for reason in result.reject_reasons)


def test_qc_warns_on_low_resolution():
    ds = _base_dataset()
    arr = np.random.rand(64, 64).astype(np.float32)
    result = evaluate_qc(ds, arr)
    assert result.status == 'ACCEPT_WITH_WARNINGS'
    assert 'low_resolution' in result.warnings
