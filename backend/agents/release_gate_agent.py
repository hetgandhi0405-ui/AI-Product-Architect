from backend.agents.state import AgentState


def release_gate_agent(state: AgentState) -> AgentState:
    validations = {
        "generated_code": state.get("generated_code_validation", {}),
        "project_build": state.get("project_build", {}),
        "api_contract": state.get("api_contract_validation", {}),
        "database_integration": state.get("database_integration_validation", {}),
        "docker_runtime": state.get("docker_runtime_validation", {}),
    }

    failures = []
    for name, result in validations.items():
        status = result.get("status")
        if status not in ("VALID", "PASSED"):
            failures.append({
                "stage": name,
                "status": status or "UNKNOWN",
                "summary": result.get("summary", ""),
                "issues": result.get("issues", []),
            })

    state["release_gate"] = {
        "status": "APPROVED" if not failures else "BLOCKED",
        "is_releasable": not failures,
        "failures": failures,
        "summary": (
            "All generated-project validation gates passed."
            if not failures
            else f"Release blocked by {len(failures)} validation stage(s)."
        ),
    }
    return state
