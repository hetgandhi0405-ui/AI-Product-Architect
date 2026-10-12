# Automated Integration Tests for Customer Support Ticket System
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

def test_list_tickets():
    res = client.get("/api/tickets/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_create_ticket():
    payload = {"title": "Automated Test Ticket", "name": "Automated Test Ticket", "description": "Verification Record", "priority": "high"}
    res = client.post("/api/tickets/", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data.get("title") == "Automated Test Ticket" or data.get("name") == "Automated Test Ticket"

def test_assign_ticket():
    res = client.patch("/api/tickets/1/assign?agent_id=3")
    assert res.status_code == 200
    assert res.json()["assigned_agent_id"] == 3
