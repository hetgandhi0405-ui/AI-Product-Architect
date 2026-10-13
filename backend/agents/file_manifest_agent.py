from typing import Dict, Any, List
from backend.agents.state import AgentState


def file_manifest_agent(state: AgentState) -> AgentState:
    """
    Generate a complete project file manifest based on the code generation contract,
    specifications, and architecture. The manifest is the single source of truth
    for full-stack code generation and validation.
    """
    contract = state.get("code_generation_contract", {})
    api_spec = state.get("api_specification", {})
    db_spec = state.get("database_specification", {})
    ui_spec = state.get("ui_specification", {})
    project_name = state.get("project_name", "Generated Product")

    # Base manifest files required by the specification
    required_files: List[Dict[str, Any]] = [
        # Frontend
        {
            "path": "frontend/package.json",
            "language": "json",
            "purpose": "Frontend React application dependencies, scripts, and build metadata",
            "required": True,
        },
        {
            "path": "frontend/index.html",
            "language": "html",
            "purpose": "Single-page application entry HTML template",
            "required": True,
        },
        {
            "path": "frontend/src/App.jsx",
            "language": "javascript",
            "purpose": "Root application UI component implementing navigation, forms, and pages",
            "required": True,
        },
        {
            "path": "frontend/src/api.js",
            "language": "javascript",
            "purpose": "Frontend API client interfacing with backend REST endpoints",
            "required": True,
        },
        {
            "path": "frontend/src/components/Loading.jsx",
            "language": "javascript",
            "purpose": "Reusable loading spinner and status feedback UI component",
            "required": True,
        },
        # Backend
        {
            "path": "backend/__init__.py",
            "language": "python",
            "purpose": "Backend package initializer",
            "required": True,
        },
        {
            "path": "backend/requirements.txt",
            "language": "text",
            "purpose": "Python package dependencies for FastAPI backend and database ORM",
            "required": True,
        },
        {
            "path": "backend/main.py",
            "language": "python",
            "purpose": "FastAPI application entry point, CORS middleware, and router registration",
            "required": True,
        },
        {
            "path": "backend/routes/__init__.py",
            "language": "python",
            "purpose": "Backend routes package initializer",
            "required": True,
        },
        {
            "path": "backend/routes/api.py",
            "language": "python",
            "purpose": "API route handlers matching the API contract specification",
            "required": True,
        },
        {
            "path": "backend/models.py",
            "language": "python",
            "purpose": "Data models / ORM entities matching database schema specification",
            "required": True,
        },
        {
            "path": "backend/schemas.py",
            "language": "python",
            "purpose": "Pydantic request and response schemas for validation",
            "required": True,
        },
        {
            "path": "backend/services.py",
            "language": "python",
            "purpose": "Business logic and database persistence services",
            "required": True,
        },
        # Database
        {
            "path": "database/schema.sql",
            "language": "sql",
            "purpose": "Relational database DDL schema matching database specification",
            "required": True,
        },
        # Tests
        {
            "path": "tests/test_generated_project.py",
            "language": "python",
            "purpose": "Unit and integration tests for generated application components",
            "required": True,
        },
        {
            "path": "tests/test_api.py",
            "language": "python",
            "purpose": "API endpoint tests verifying contract compliance",
            "required": True,
        },
        # Docker & Runtime
        {
            "path": "Dockerfile",
            "language": "dockerfile",
            "purpose": "Container build definition for the application",
            "required": True,
        },
        {
            "path": "docker-compose.yml",
            "language": "yaml",
            "purpose": "Multi-container orchestration for frontend, backend, and database",
            "required": True,
        },
        {
            "path": ".env.example",
            "language": "env",
            "purpose": "Sample environment configuration variables",
            "required": True,
        },
        # Infrastructure / Terraform
        {
            "path": "infrastructure/main.tf",
            "language": "hcl",
            "purpose": "Terraform infrastructure resources and cloud provider configuration",
            "required": True,
        },
        {
            "path": "infrastructure/variables.tf",
            "language": "hcl",
            "purpose": "Terraform input variables and default settings",
            "required": True,
        },
        {
            "path": "infrastructure/outputs.tf",
            "language": "hcl",
            "purpose": "Terraform output attributes and connection strings",
            "required": True,
        },
        # Documentation
        {
            "path": "README.md",
            "language": "markdown",
            "purpose": "Project documentation, architecture overview, setup and run instructions",
            "required": True,
        },
    ]

    manifest = {
        "project_name": project_name,
        "total_files": len(required_files),
        "files": required_files,
        "file_paths": [f["path"] for f in required_files],
        "categories": {
            "frontend": [f["path"] for f in required_files if f["path"].startswith("frontend/")],
            "backend": [f["path"] for f in required_files if f["path"].startswith("backend/")],
            "database": [f["path"] for f in required_files if f["path"].startswith("database/")],
            "tests": [f["path"] for f in required_files if f["path"].startswith("tests/")],
            "infrastructure": [f["path"] for f in required_files if f["path"].startswith("infrastructure/")],
            "docker": ["Dockerfile", "docker-compose.yml"],
            "config": [".env.example", "README.md"],
        }
    }

    state["file_manifest"] = manifest

    architecture = state.get("architecture", {})
    architecture["file_manifest"] = manifest
    state["architecture"] = architecture

    return state
