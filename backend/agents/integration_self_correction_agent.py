from typing import Dict, Any, List
from backend.agents.state import AgentState
from backend.agents.file_assembler_agent import file_assembler_agent
from backend.agents.api_contract_testing_agent import api_contract_testing_agent
from backend.agents.database_integration_testing_agent import database_integration_testing_agent
from backend.agents.docker_runtime_testing_agent import docker_runtime_testing_agent
from backend.agents.code_generation_agent import _generate_file_deterministic


def integration_self_correction_agent(state: AgentState) -> AgentState:
    """
    Automatically repair integration-level mismatches:
    - Missing API routes or methods
    - Missing database schema tables or ORM models
    - Missing Dockerfile / docker-compose directives
    Reassembles and re-tests contracts up to max_integration_correction_attempts.
    """
    api_val = state.get("api_validation", {})
    db_val = state.get("database_validation", {})
    docker_val = state.get("docker_validation", {})

    all_passed = (
        api_val.get("status") in ("PASS", "WARN") and
        db_val.get("status") in ("PASS", "WARN") and
        docker_val.get("status") == "PASS"
    )

    if all_passed:
        return state

    attempts = state.get("integration_correction_attempts", 0)
    max_attempts = state.get("max_integration_correction_attempts", 2)

    if attempts >= max_attempts:
        return state

    state["integration_correction_attempts"] = attempts + 1
    manifest = state.get("file_manifest", {})
    manifest_files_by_path = {f["path"]: f for f in manifest.get("files", [])}
    generated_files = state.get("generated_files", {})
    files_to_rebuild = set()

    # If API contract failed, regenerate routes/api.py and frontend/src/api.js
    if api_val.get("status") == "FAIL":
        files_to_rebuild.add("backend/routes/api.py")
        files_to_rebuild.add("frontend/src/api.js")

    # If database validation failed, regenerate database/schema.sql and backend/models.py
    if db_val.get("status") == "FAIL":
        files_to_rebuild.add("database/schema.sql")
        files_to_rebuild.add("backend/models.py")

    # If docker validation failed, regenerate Dockerfile and docker-compose.yml
    if docker_val.get("status") == "FAIL":
        files_to_rebuild.add("Dockerfile")
        files_to_rebuild.add("docker-compose.yml")

    for fpath in files_to_rebuild:
        file_info = manifest_files_by_path.get(fpath, {"path": fpath, "language": "text", "purpose": "Repaired integration file"})
        generated_files[fpath] = _generate_file_deterministic(fpath, file_info, state)

    state["generated_files"] = generated_files

    # Re-assemble
    state = file_assembler_agent(state)

    # Re-test integrations
    state = api_contract_testing_agent(state)
    state = database_integration_testing_agent(state)
    state = docker_runtime_testing_agent(state)

    architecture = state.get("architecture", {})
    history = architecture.setdefault("integration_correction_history", [])
    history.append({
        "attempt": state["integration_correction_attempts"],
        "files_rebuilt": list(files_to_rebuild),
        "api_status_after": state.get("api_validation", {}).get("status"),
        "db_status_after": state.get("database_validation", {}).get("status"),
        "docker_status_after": state.get("docker_validation", {}).get("status"),
    })
    state["architecture"] = architecture

    return state
