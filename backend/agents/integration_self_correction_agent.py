from backend.agents.code_generation_agent import generate_file_content
from backend.agents.state import AgentState


def _failure_files(state: AgentState):
    paths = set()
    build = state.get("project_build", {})
    for result in build.get("results", []):
        path = result.get("path")
        if path:
            paths.add(path)

    api = state.get("api_contract_validation", {})
    if api.get("status") == "INVALID":
        paths.update({"backend/main.py", "frontend/src/App.jsx"})

    database = state.get("database_integration_validation", {})
    if database.get("status") == "INVALID":
        paths.update({"database/schema.sql", "backend/main.py"})

    docker = state.get("docker_runtime_validation", {})
    if docker.get("status") == "INVALID":
        paths.update({"Dockerfile", "docker-compose.yml"})

    return paths


def integration_self_correction_agent(state: AgentState) -> AgentState:
    attempts = state.get("integration_correction_attempts", 0) + 1
    max_attempts = state.get("max_integration_correction_attempts", 2)
    generated = dict(state.get("generated_files", {}))
    manifest = {
        item["path"]: item
        for item in state.get("file_manifest", {}).get("files", [])
        if isinstance(item, dict) and item.get("path")
    }

    feedback_parts = []
    for key in (
        "project_build",
        "api_contract_validation",
        "database_integration_validation",
        "docker_runtime_validation",
    ):
        result = state.get(key, {})
        if result.get("status") == "INVALID":
            feedback_parts.append(f"{key}: {result.get('summary', '')}")
            feedback_parts.extend(str(item) for item in result.get("issues", []))

    feedback = "\n".join(feedback_parts)
    for path in _failure_files(state):
        item = manifest.get(path, {})
        generated[path] = generate_file_content(
            state,
            path,
            item.get("kind", "source"),
            feedback or "Integration validation failed. Regenerate this file so the generated project is internally consistent.",
        )

    state["generated_files"] = generated
    state["integration_correction_attempts"] = attempts
    state["max_integration_correction_attempts"] = max_attempts
    state["integration_correction_files"] = sorted(_failure_files(state))
    return state
