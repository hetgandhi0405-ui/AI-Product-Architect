import os
import shutil
from pathlib import Path

from backend.agents.api_contract_testing_agent import api_contract_testing_agent
from backend.agents.database_integration_testing_agent import database_integration_testing_agent
from backend.agents.docker_runtime_testing_agent import docker_runtime_testing_agent
from backend.agents.file_assembler_agent import file_assembler_agent
from backend.agents.file_manifest_agent import file_manifest_agent
from backend.agents.generated_code_validator_agent import generated_code_validator_agent
from backend.agents.project_build_agent import project_build_agent
from backend.agents.project_export_agent import project_export_agent
from backend.agents.release_gate_agent import release_gate_agent


FILES = {
    "frontend/package.json": '{"scripts":{"build":"echo smoke-build"},"dependencies":{}}',
    "frontend/index.html": "<!doctype html><html><body><div id='root'></div></body></html>",
    "frontend/src/App.jsx": "export default function App(){return <div>AI Product Architect</div>}\nfetch('/health');\n",
    "frontend/src/api.js": "export async function health(){return fetch('/health');}\n",
    "frontend/src/components/Loading.jsx": "export default function Loading(){return <span>Loading...</span>}\n",
    "backend/requirements.txt": "fastapi\nuvicorn\n",
    "backend/routes/__init__.py": "",
    "backend/routes/api.py": "# Smoke-test route module.\n",
    "backend/models.py": "class User:\n    pass\n",
    "backend/schemas.py": "class UserSchema:\n    pass\n",
    "backend/services.py": "def list_users():\n    return []\n",
    "backend/main.py": (
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n"
        "@app.get('/health')\n"
        "def health():\n"
        "    return {'status': 'ok'}\n"
        "def load_users():\n"
        "    return 'SELECT * FROM users'\n"
    ),
    "database/schema.sql": (
        "CREATE TABLE users (\n"
        "  id INTEGER PRIMARY KEY,\n"
        "  name VARCHAR(100) NOT NULL\n"
        ");\n"
    ),
    "tests/test_generated_project.py": "def test_smoke():\n    assert True\n",
    "tests/test_api.py": "def test_api_contract_placeholder():\n    assert True\n",
    "Dockerfile": "FROM python:3.12-slim\nCOPY backend /app/backend\n",
    "docker-compose.yml": "services:\n  backend:\n    build: .\n",
    ".env.example": "APP_ENV=development\n",
    "infrastructure/main.tf": 'provider "aws" {}\n',
    "infrastructure/variables.tf": 'variable "environment" { type = string }\n',
    "infrastructure/outputs.tf": 'output "environment" { value = var.environment }\n',
    "README.md": "# Generated AI Product Architect Smoke Test\n",
}


def run():
    root = Path(os.getenv("AI_PRODUCT_ARCHITECT_SMOKE_ROOT", "generated_projects"))
    output_dir = root / "delivery-smoke-test"
    export_dir = root / "exports"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    os.environ["AI_PRODUCT_ARCHITECT_OUTPUT_DIR"] = str(root)
    os.environ["AI_PRODUCT_ARCHITECT_EXPORT_DIR"] = str(export_dir)
    os.environ["AI_PRODUCT_ARCHITECT_RUN_GENERATED_BUILDS"] = "0"
    os.environ["AI_PRODUCT_ARCHITECT_RUN_DOCKER_TESTS"] = "0"

    state = {
        "project_id": "delivery-smoke-test",
        "project_name": "Delivery Smoke Test",
        "requirements": "Create a simple health-check web application with a users database.",
        "code_generation_contract": {
            "project": {"name": "Delivery Smoke Test"},
            "generation_targets": {
                "frontend": True, "backend": True, "database": True,
                "tests": True, "docker": True, "terraform": True,
                "documentation": True,
            },
        },
        "api_specification": {
            "base_path": "",
            "endpoints": [{"method": "GET", "endpoint": "/health"}],
        },
        "database_specification": {
            "tables": [{"name": "users"}],
        },
        "generated_files": FILES,
        }

    state = file_manifest_agent(state)
    state = file_assembler_agent(state)
    state = generated_code_validator_agent(state)
    if state["generated_code_validation"]["status"] != "VALID":
        raise RuntimeError(state["generated_code_validation"])

    state = project_build_agent(state)
    state = api_contract_testing_agent(state)
    state = database_integration_testing_agent(state)
    state = docker_runtime_testing_agent(state)
    state = release_gate_agent(state)

    if state["release_gate"]["status"] != "APPROVED":
        raise RuntimeError(state["release_gate"])

    state = project_export_agent(state)

    project = Path(state["generated_project_path"])
    zip_path = Path(state["project_export"]["zip_path"])

    print("STATUS: PASS")
    print(f"PROJECT: {project}")
    print(f"ZIP: {zip_path}")
    print(f"FILES: {state['file_manifest']['file_count']}")
    for path in sorted(
            p.relative_to(project).as_posix()
            for p in project.rglob("*") if p.is_file()
        ):
            print(f"DELIVERABLE: {path}")
    print(f"GENERATED_CODE: {state['generated_code_validation']['status']}")
    print(f"BUILD: {state['project_build']['status']}")
    print(f"API: {state['api_contract_validation']['status']}")
    print(f"DATABASE: {state['database_integration_validation']['status']}")
    print(f"DOCKER: {state['docker_runtime_validation']['status']}")
    print(f"RELEASE_GATE: {state['release_gate']['status']}")
    print(f"EXPORT: {state['project_export']['status']}")


if __name__ == "__main__":
    run()
