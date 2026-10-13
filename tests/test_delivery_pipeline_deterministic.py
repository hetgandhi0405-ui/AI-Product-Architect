import os
import zipfile
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from backend.main import app
from backend.agents.state import AgentState
from backend.agents.file_manifest_agent import file_manifest_agent
from backend.agents.code_generation_agent import code_generation_agent
from backend.agents.file_assembler_agent import file_assembler_agent
from backend.agents.generated_code_validator_agent import generated_code_validator_agent
from backend.agents.project_build_agent import project_build_agent
from backend.agents.api_contract_testing_agent import api_contract_testing_agent
from backend.agents.database_integration_testing_agent import database_integration_testing_agent
from backend.agents.docker_runtime_testing_agent import docker_runtime_testing_agent
from backend.agents.generated_code_self_correction_agent import generated_code_self_correction_agent
from backend.agents.integration_self_correction_agent import integration_self_correction_agent
from backend.agents.release_gate_agent import release_gate_agent
from backend.agents.project_export_agent import project_export_agent
from backend.agents.graph import build_agent_graph


client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_gemini_key(monkeypatch):
    """Force deterministic mock mode for all unit tests in this module."""
    monkeypatch.setenv("GEMINI_API_KEY", "mock")


def test_file_manifest_agent_generates_standard_structure():
    """Verify that file_manifest_agent produces all mandatory files."""
    state = {
        "project_id": "test-manifest-01",
        "project_name": "Task Manager",
        "requirements": "Task management system with users and tasks"
    }

    result = file_manifest_agent(state)
    manifest = result.get("file_manifest", {})

    assert manifest["total_files"] >= 20
    file_paths = manifest["file_paths"]

    # Verify key mandatory files
    assert "frontend/package.json" in file_paths
    assert "frontend/src/App.jsx" in file_paths
    assert "frontend/src/api.js" in file_paths
    assert "backend/requirements.txt" in file_paths
    assert "backend/main.py" in file_paths
    assert "backend/routes/api.py" in file_paths
    assert "backend/models.py" in file_paths
    assert "database/schema.sql" in file_paths
    assert "Dockerfile" in file_paths
    assert "docker-compose.yml" in file_paths
    assert "infrastructure/main.tf" in file_paths
    assert "README.md" in file_paths


def test_code_generation_and_assembly_pipeline(tmp_path):
    """Verify code synthesis and physical disk assembly with security checks."""
    project_id = "test-assembly-01"
    os.environ["AI_PRODUCT_ARCHITECT_PROJECTS_DIR"] = str(tmp_path)

    state = {
        "project_id": project_id,
        "project_name": "Task Manager",
        "requirements": "Create a task management app with user registration and tasks.",
        "api_specification": {
            "endpoints": [
                {"method": "GET", "endpoint": "/tasks", "purpose": "List tasks"},
                {"method": "POST", "endpoint": "/tasks", "purpose": "Create task"}
            ]
        },
        "database_specification": {
            "tables": [{"name": "users"}, {"name": "tasks"}]
        }
    }

    state = file_manifest_agent(state)
    state = code_generation_agent(state)

    # All manifest files must have generated code
    assert len(state["generated_files"]) == len(state["file_manifest"]["files"])

    state = file_assembler_agent(state)
    project_dir = Path(state["assembled_project_path"])

    assert project_dir.exists()
    assert (project_dir / "backend" / "main.py").exists()
    assert (project_dir / "Dockerfile").exists()
    assert (project_dir / "docker-compose.yml").exists()
    assert (project_dir / "database" / "schema.sql").exists()


def test_validation_agents_pass_for_synthesized_project(tmp_path):
    """Verify code, build, api, db, and docker validation gates on clean generated code."""
    project_id = "test-validation-01"
    os.environ["AI_PRODUCT_ARCHITECT_PROJECTS_DIR"] = str(tmp_path)
    os.environ["AI_PRODUCT_ARCHITECT_EXPORT_DIR"] = str(tmp_path / "exports")

    state = {
        "project_id": project_id,
        "project_name": "Task Manager",
        "requirements": "Create a task management app with user registration and tasks.",
        "execution_mode": "QUICK",
        "api_specification": {
            "endpoints": [
                {"method": "GET", "endpoint": "/tasks", "purpose": "List tasks"},
                {"method": "POST", "endpoint": "/tasks", "purpose": "Create task"},
                {"method": "POST", "endpoint": "/auth/register", "purpose": "Register user"},
                {"method": "POST", "endpoint": "/auth/login", "purpose": "Login user"}
            ]
        },
        "database_specification": {
            "tables": [{"name": "users"}, {"name": "tasks"}]
        }
    }

    state = file_manifest_agent(state)
    state = code_generation_agent(state)
    state = file_assembler_agent(state)

    # 1. Code Validation
    state = generated_code_validator_agent(state)
    assert state["code_validation"]["status"] == "PASS"
    assert state["code_validation"]["is_valid"] is True

    # 2. Build Validation
    state = project_build_agent(state)
    assert state["build_validation"]["status"] == "PASS"

    # 3. API Contract Validation
    state = api_contract_testing_agent(state)
    assert state["api_validation"]["status"] in ("PASS", "WARN")

    # 4. Database Validation
    state = database_integration_testing_agent(state)
    assert state["database_validation"]["status"] in ("PASS", "WARN")

    # 5. Docker Validation
    state = docker_runtime_testing_agent(state)
    assert state["docker_validation"]["status"] == "PASS"

    # 6. Release Gate
    state = release_gate_agent(state)
    assert state["release_gate"]["status"] == "APPROVED"
    assert state["release_gate"]["approved"] is True

    # 7. Project Export ZIP
    state = project_export_agent(state)
    assert state["export"]["status"] == "SUCCESS"
    zip_path = Path(state["export"]["zip_path"])
    assert zip_path.exists()
    assert zipfile.is_zipfile(zip_path)

    # Inspect zip contents
    with zipfile.ZipFile(zip_path, "r") as zf:
        namelist = zf.namelist()
        assert any("backend/main.py" in n for n in namelist)
        assert any("Dockerfile" in n for n in namelist)
        assert any("database/schema.sql" in n for n in namelist)


def test_release_gate_blocks_on_syntax_error(tmp_path):
    """Verify that release gate strictly BLOCKS export if code has syntax errors."""
    project_id = "test-blocked-01"
    os.environ["AI_PRODUCT_ARCHITECT_PROJECTS_DIR"] = str(tmp_path)
    os.environ["AI_PRODUCT_ARCHITECT_EXPORT_DIR"] = str(tmp_path / "exports")

    state = {
        "project_id": project_id,
        "project_name": "Broken App",
        "requirements": "Broken app"
    }

    state = file_manifest_agent(state)
    state = code_generation_agent(state)

    # Inject intentional syntax error
    state["generated_files"]["backend/main.py"] = "def broken_syntax(:\n    pass\n"

    state = file_assembler_agent(state)
    state = generated_code_validator_agent(state)
    state = project_build_agent(state)
    state = api_contract_testing_agent(state)
    state = database_integration_testing_agent(state)
    state = docker_runtime_testing_agent(state)

    # Release gate MUST block
    state = release_gate_agent(state)
    assert state["release_gate"]["status"] == "BLOCKED"
    assert state["release_gate"]["approved"] is False

    # Export must be blocked
    state = project_export_agent(state)
    assert state["export"]["status"] == "BLOCKED"
    assert state["export"]["zip_path"] is None


def test_fastapi_end_to_end_delivery():
    """Verify full end-to-end POST /api/requirements/ and GET /api/requirements/export/{id}."""
    payload = {
        "description": "Create a task management application where users can register, login, create tasks, update tasks, delete tasks and mark tasks as completed."
    }

    try:
        from google.genai.errors import ServerError, APIError
    except ImportError:
        ServerError = APIError = Exception

    try:
        response = client.post("/api/requirements/", json=payload)
    except Exception as exc:
        err_msg = str(exc)
        if any(k in err_msg for k in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "Quota", "quota", "high demand", "failed after 3 attempts"]):
            pytest.skip(f"Google Gemini API temporarily unavailable: {exc}")
        raise
    assert response.status_code == 200

    data = response.json()
    project_id = data["project_id"]
    assert project_id is not None
    assert data["project_name"] is not None
    assert data["generated_files_count"] >= 20
    assert data["code_validation"]["status"] == "PASS"
    assert data["build_validation"]["status"] == "PASS"
    assert data["release_gate"]["status"] == "APPROVED"
    assert data["download_url"] == f"/api/requirements/export/{project_id}"

    # Verify download endpoint
    dl_response = client.get(data["download_url"])
    assert dl_response.status_code == 200
    assert dl_response.headers["content-type"] == "application/zip"
    assert len(dl_response.content) > 1000
