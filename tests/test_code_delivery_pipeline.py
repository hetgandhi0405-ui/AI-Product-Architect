from pathlib import Path
import zipfile

from backend.agents.file_manifest_agent import file_manifest_agent
from backend.agents.file_assembler_agent import file_assembler_agent
from backend.agents.generated_code_validator_agent import generated_code_validator_agent
from backend.agents.project_export_agent import project_export_agent


def test_file_manifest_contains_docker_and_terraform():
    state = {
        "code_generation_contract": {
            "project": {"name": "Demo"},
            "generation_targets": {
                "frontend": True,
                "backend": True,
                "database": True,
                "tests": True,
                "docker": True,
                "terraform": True,
                "documentation": True,
            },
        }
    }
    result = file_manifest_agent(state)
    paths = {item["path"] for item in result["file_manifest"]["files"]}
    assert "Dockerfile" in paths
    assert "docker-compose.yml" in paths
    assert "infrastructure/main.tf" in paths
    assert "infrastructure/variables.tf" in paths
    assert "infrastructure/outputs.tf" in paths


def test_assembly_validation_and_export(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_PRODUCT_ARCHITECT_OUTPUT_DIR", str(tmp_path))
    monkeypatch.setenv("AI_PRODUCT_ARCHITECT_EXPORT_DIR", str(tmp_path))
    state = {
        "project_id": "demo-1",
        "file_manifest": {
            "files": [
                {"path": "backend/main.py", "kind": "backend_source"},
                {"path": "frontend/package.json", "kind": "frontend_config"},
                {"path": "Dockerfile", "kind": "dockerfile"},
                {"path": "docker-compose.yml", "kind": "docker_compose"},
                {"path": "infrastructure/main.tf", "kind": "terraform"},
                {"path": "infrastructure/variables.tf", "kind": "terraform"},
                {"path": "infrastructure/outputs.tf", "kind": "terraform"},
            ]
        },
        "generated_files": {
            "backend/main.py": "print('ok')",
            "frontend/package.json": '{"name":"demo"}',
            "Dockerfile": "FROM python:3.12-slim",
            "docker-compose.yml": "services:\n  app:\n    build: .",
            "infrastructure/main.tf": 'terraform {}\nprovider "aws" {}',
            "infrastructure/variables.tf": 'variable "region" {}',
            "infrastructure/outputs.tf": 'output "name" {}',
        },
    }
    state = file_assembler_agent(state)
    state = generated_code_validator_agent(state)
    assert state["generated_code_validation"]["status"] == "VALID"
    state = project_export_agent(state)
    assert state["export_status"] == "EXPORTED"
    with zipfile.ZipFile(state["project_export"]["zip_path"]) as archive:
        names = set(archive.namelist())
    assert "backend/main.py" in names
    assert "infrastructure/main.tf" in names
