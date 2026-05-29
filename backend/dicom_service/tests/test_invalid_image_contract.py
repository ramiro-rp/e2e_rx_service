from fastapi.testclient import TestClient

from dicom_service.src.api import app


client = TestClient(app)


def test_invalid_standard_image_returns_structured_reject() -> None:
    response = client.post(
        '/infer',
        files={'file': ('broken.png', b'not-a-real-image', 'image/png')},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'REJECT'
    assert payload['qc']['reject_reasons'] == ['invalid_standard_image']
    assert payload['qc']['dicom_meta']['source_type'] == 'image'
    assert payload['artifacts']['derived_dicom_url'] is None
