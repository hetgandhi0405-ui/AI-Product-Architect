# Automated Integration Tests for Smart Home Dashboard
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert "Welcome" in res.json()["message"]

def test_auth_flow():
    res = client.post("/api/auth/login", json={"email": "test@enterprise.io", "password": "SecretPassword123"})
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_list_devices():
    res = client.get("/api/devices/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_create_device():
    payload = {"title": "Automated Test Device", "name": "Automated Test Device", "description": "Verification Record", "priority": "high"}
    res = client.post("/api/devices/", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data.get("title") == "Automated Test Device" or data.get("name") == "Automated Test Device"

def test_ingest_telemetry():
    res = client.post("/api/devices/1/telemetry", json={"metric": "temperature", "value": 24.5})
    assert res.status_code == 200
    assert res.json()["status"] == "ingested"
