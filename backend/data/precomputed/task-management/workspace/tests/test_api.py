# Automated Integration Tests for Task Management System
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

def test_list_tasks():
    res = client.get("/api/tasks/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_create_task():
    payload = {"title": "Automated Test Task", "name": "Automated Test Task", "description": "Verification Record", "priority": "high"}
    res = client.post("/api/tasks/", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data.get("title") == "Automated Test Task" or data.get("name") == "Automated Test Task"

def test_status_toggle():
    res = client.patch("/api/tasks/1/status?new_status=completed")
    assert res.status_code == 200
    assert res.json()["status"] == "completed"
