# Automated Integration Tests for Employee Attendance Management
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

def test_list_employees():
    res = client.get("/api/employees/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_create_employee():
    payload = {"title": "Automated Test Employee", "name": "Automated Test Employee", "description": "Verification Record", "priority": "high"}
    res = client.post("/api/employees/", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data.get("title") == "Automated Test Employee" or data.get("name") == "Automated Test Employee"

def test_clock_in():
    res = client.post("/api/employees/clock-in?employee_id=1")
    assert res.status_code == 200
    assert res.json()["status"] == "present"
