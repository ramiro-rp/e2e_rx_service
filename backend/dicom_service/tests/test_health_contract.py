from dicom_service.src.api import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_health_endpoint_returns_expected_keys() -> None:
    response = client.get('/health')
    assert response.status_code == 200
    payload = response.json()
    assert payload['service']
    assert payload['task']
    assert payload['input_size']
    assert payload['outputs_base_url'] == '/outputs'
    assert 'model_path' not in payload
    assert 'calibration_temperature_path' not in payload
    assert 'threshold_path' not in payload
