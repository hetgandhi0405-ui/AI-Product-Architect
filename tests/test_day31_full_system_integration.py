import pytest
from fastapi.testclient import TestClient
from backend.main import app
try:
    from google.genai.errors import ServerError, APIError
except ImportError:
    ServerError = APIError = Exception


client = TestClient(app)


def test_full_system_integration():
    payload = {
        "project_name": "Day 31 E-Commerce Integration Test",
        "description": "Build a scalable e-commerce platform for 100,000 users with secure payments and high availability.",
        "users": 100000,
        "features": ["authentication", "product catalog", "shopping cart", "payments"],
        "security_level": "high",
        "availability": "high",
    }

    try:
        response = client.post("/api/requirements/", json=payload)
    except (ServerError, APIError, Exception) as exc:
        if "503" in str(exc) or "UNAVAILABLE" in str(exc) or "experiencing high demand" in str(exc):
            pytest.skip(f"Google Gemini API temporarily unavailable: {exc}")
        raise

    assert response.status_code == 200

    data = response.json()
    architecture = data["architecture"]

    assert data["project_name"] == payload["project_name"]
    assert data["requirements"] == payload["description"]
    assert architecture.get("knowledge_graph")
    assert architecture.get("digital_twin")
    assert architecture.get("what_if")
    assert architecture.get("simulation")
    assert architecture["simulation"]["status"] == "completed"
    assert "impact" in architecture["simulation"]

