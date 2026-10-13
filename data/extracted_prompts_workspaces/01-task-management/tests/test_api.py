from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_primary_create_and_list():
    created = client.post('/projects', json={"name": "test record", "description": "test"})
    assert created.status_code == 201
    assert created.json()["name"] == "test record"
    assert client.get('/projects').status_code == 200
