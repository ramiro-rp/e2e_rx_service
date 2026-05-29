from fastapi.testclient import TestClient

from dicom_service.src.api import app


client = TestClient(app)


def test_invalid_dicom_returns_structured_reject() -> None:
    response = client.post(
        '/infer',
        files={'file': ('not_a_dicom.dcm', b'plain-text-not-dicom', 'application/dicom')},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'REJECT'
    assert payload['qc']['reject_reasons'] == ['invalid_dicom']
    assert payload['prediction']['label'] is None
    assert payload['prediction']['probability'] is None
    assert payload['outputs'] == {
        'image_analyzed_url': None,
        'heatmap_url': None,
        'overlay_url': None,
        'original_image_url': None,
        'transparent_heatmap_url': None,
    }
    assert payload['artifacts']['run_id'].startswith('run_')
    assert payload['artifacts']['report_url'] in (None, f"/outputs/{payload['request_id']}/report.json")
    serialized = str(payload)
    assert 'model_path' not in serialized
    assert 'uploaded_dicom_path' not in serialized
    assert 'report_json_path' not in serialized
