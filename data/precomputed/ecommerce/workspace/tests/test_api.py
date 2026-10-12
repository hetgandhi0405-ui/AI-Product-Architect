# Automated Integration Tests for E-Commerce Platform
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

def test_list_products():
    res = client.get("/api/products/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_create_product():
    payload = {"title": "Automated Test Product", "name": "Automated Test Product", "description": "Verification Record", "priority": "high"}
    res = client.post("/api/products/", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data.get("title") == "Automated Test Product" or data.get("name") == "Automated Test Product"

def test_order_checkout():
    res = client.post("/api/products/1/checkout")
    assert res.status_code == 200
    assert res.json()["status"] == "paid"
