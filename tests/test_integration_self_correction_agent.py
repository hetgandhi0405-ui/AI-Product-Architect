from backend.agents.integration_self_correction_agent import integration_self_correction_agent


def test_integration_correction_regenerates_affected_files(monkeypatch):
    calls = []

    def fake_generate(state, path, kind, feedback):
        calls.append((path, kind, feedback))
        return f"fixed:{path}"

    monkeypatch.setattr(
        "backend.agents.integration_self_correction_agent.generate_file_content",
        fake_generate,
    )

    state = {
        "generated_files": {},
        "file_manifest": {
            "files": [
                {"path": "backend/main.py", "kind": "python"},
                {"path": "database/schema.sql", "kind": "sql"},
                {"path": "Dockerfile", "kind": "dockerfile"},
                {"path": "docker-compose.yml", "kind": "yaml"},
            ]
        },
        "project_build": {"status": "PASSED", "results": []},
        "api_contract_validation": {"status": "VALID", "issues": []},
        "database_integration_validation": {
            "status": "INVALID",
            "issues": ["database table is missing from schema"],
        },
        "docker_runtime_validation": {"status": "INVALID", "issues": ["missing services"]},
        "integration_correction_attempts": 0,
        "max_integration_correction_attempts": 2,
    }

    result = integration_self_correction_agent(state)

    assert result["integration_correction_attempts"] == 1
    assert set(result["integration_correction_files"]) == {
        "backend/main.py",
        "database/schema.sql",
        "Dockerfile",
        "docker-compose.yml",
    }
    assert len(calls) == 4


def test_integration_correction_does_not_change_unaffected_files(monkeypatch):
    monkeypatch.setattr(
        "backend.agents.integration_self_correction_agent.generate_file_content",
        lambda state, path, kind, feedback: f"fixed:{path}",
    )

    state = {
        "generated_files": {
            "frontend/src/App.jsx": "keep-me",
        },
        "file_manifest": [
            {"path": "frontend/src/App.jsx", "kind": "jsx"},
        ],
        "project_build": {"status": "PASSED", "results": []},
        "api_contract_validation": {"status": "VALID", "issues": []},
        "database_integration_validation": {"status": "VALID", "issues": []},
        "docker_runtime_validation": {"status": "VALID", "issues": []},
        "integration_correction_attempts": 0,
        "max_integration_correction_attempts": 2,
    }

    result = integration_self_correction_agent(state)
    assert result["generated_files"]["frontend/src/App.jsx"] == "keep-me"
    assert result["integration_correction_files"] == []
