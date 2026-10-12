# Automated Integration Tests for Personal Finance Tracker
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

def test_list_transactions():
    res = client.get("/api/transactions/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_create_transaction():
    payload = {"title": "Automated Test Transaction", "name": "Automated Test Transaction", "description": "Verification Record", "priority": "high"}
    res = client.post("/api/transactions/", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data.get("title") == "Automated Test Transaction" or data.get("name") == "Automated Test Transaction"

def test_export_csv():
    res = client.get("/api/transactions/export-csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
