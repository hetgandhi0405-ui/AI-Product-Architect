# Automated Integration Tests for Student Learning Management System
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

def test_list_courses():
    res = client.get("/api/courses/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_create_course():
    payload = {"title": "Automated Test Course", "name": "Automated Test Course", "description": "Verification Record", "priority": "high"}
    res = client.post("/api/courses/", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data.get("title") == "Automated Test Course" or data.get("name") == "Automated Test Course"

def test_enroll_course():
    res = client.post("/api/courses/1/enroll")
    assert res.status_code == 200
    assert res.json()["status"] == "enrolled"
