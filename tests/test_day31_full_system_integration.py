import json
from types import SimpleNamespace

from fastapi.testclient import TestClient
from google.genai.models import Models

from backend.core import llm_cache
from backend.main import app


client = TestClient(app)


def test_full_system_integration(monkeypatch, tmp_path):
    generated_requests = []

    local_model_response = {
        "tools": [],
        "categories": [],
        "selection_summary": (
            "No external tools are required for the deterministic "
            "integration test."
        ),
        "security_notes": [],
        "implementation_notes": [],
        "knowledge_graph": {
            "nodes": [],
            "edges": [],
        },
        "digital_twin": {
            "status": "ready",
            "components": [],
        },
        "what_if": {
            "scenarios": [],
        },
        "simulation": {
            "status": "completed",
            "impact": {
                "estimate": 0,
            },
        },
        "impact": {
            "estimate": 0,
        },
    }

    def fake_generate_content(self, **kwargs):
        generated_requests.append(kwargs)

        return SimpleNamespace(
            text=json.dumps(local_model_response)
        )

    monkeypatch.setattr(
        Models,
        "generate_content",
        fake_generate_content,
    )

    monkeypatch.setattr(
        llm_cache,
        "CACHE_DIR",
        tmp_path,
    )

    payload = {
        "project_name": "Day 31 E-Commerce Integration Test",
        "description": (
            "Build a scalable e-commerce platform for 100,000 users "
            "with secure payments and high availability."
        ),
        "users": 100000,
        "features": [
            "authentication",
            "product catalog",
            "shopping cart",
            "payments",
        ],
        "security_level": "high",
        "availability": "high",
    }

    response = client.post(
        "/api/requirements/",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["project_name"] == payload["project_name"]
    assert data["requirements"] == payload["description"]

    architecture = data["architecture"]

    assert architecture.get("knowledge_graph")
    assert architecture.get("digital_twin")
    assert architecture.get("what_if")
    assert architecture.get("simulation")

    assert (
        architecture["simulation"]["status"]
        == "completed"
    )

    assert "impact" in architecture["simulation"]

    assert generated_requests, (
        "The deterministic local model seam was not used."
    )
