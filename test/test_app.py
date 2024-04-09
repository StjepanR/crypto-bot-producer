from fastapi.testclient import TestClient
from app import get_app

client = TestClient(get_app())

def test_should_status_code_ok():
    response = client.get('/')
    assert response.status_code == 200