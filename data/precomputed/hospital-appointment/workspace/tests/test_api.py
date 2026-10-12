# Automated Integration Tests for Hospital Appointment System
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

def test_list_doctors():
    res = client.get("/api/doctors/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_create_doctor():
    payload = {"title": "Automated Test Doctor", "name": "Automated Test Doctor", "description": "Verification Record", "priority": "high"}
    res = client.post("/api/doctors/", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data.get("title") == "Automated Test Doctor" or data.get("name") == "Automated Test Doctor"

def test_cancel_appointment():
    res = client.patch("/api/doctors/1/cancel")
    assert res.status_code == 200
    assert res.json()["status"] == "cancelled"
