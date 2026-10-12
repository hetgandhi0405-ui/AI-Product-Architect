# Automated Integration Tests for Real-Time Analytics Dashboard
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

def test_list_events():
    res = client.get("/api/events/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_create_event():
    payload = {"title": "Automated Test Event", "name": "Automated Test Event", "description": "Verification Record", "priority": "high"}
    res = client.post("/api/events/", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data.get("title") == "Automated Test Event" or data.get("name") == "Automated Test Event"

def test_realtime_metrics():
    res = client.get("/api/events/realtime")
    assert res.status_code == 200
    assert "events_per_sec" in res.json()
