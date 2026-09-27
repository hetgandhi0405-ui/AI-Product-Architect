from typing import Any, Dict, List

from backend.agents.state import AgentState


def file_manifest_agent(state: AgentState) -> AgentState:
    """Convert the code-generation contract into an explicit file manifest."""
    contract = state.get("code_generation_contract", {})
    targets = contract.get("generation_targets", {})
    manifest: List[Dict[str, Any]] = []

    def add(path: str, kind: str, required: bool = True) -> None:
        manifest.append({"path": path, "kind": kind, "required": required})

    if targets.get("frontend", True):
        add("frontend/package.json", "frontend_config")
        add("frontend/index.html", "frontend_entry")
        add("frontend/src/App.jsx", "frontend_source")
    if targets.get("backend", True):
        add("backend/requirements.txt", "backend_config")
        add("backend/main.py", "backend_source")
    if targets.get("database", True):
        add("database/schema.sql", "database_schema")
    if targets.get("tests", True):
        add("tests/test_generated_project.py", "test_source")
    if targets.get("docker", True):
        add("Dockerfile", "dockerfile")
        add("docker-compose.yml", "docker_compose")
        add(".env.example", "environment")
    if targets.get("terraform", True):
        add("infrastructure/main.tf", "terraform")
        add("infrastructure/variables.tf", "terraform")
        add("infrastructure/outputs.tf", "terraform")
    if targets.get("documentation", True):
        add("README.md", "documentation")

    state["file_manifest"] = {
        "version": "1.0",
        "project_name": contract.get("project", {}).get("name", "Generated Product"),
        "files": manifest,
        "file_count": len(manifest),
    }
    return state
