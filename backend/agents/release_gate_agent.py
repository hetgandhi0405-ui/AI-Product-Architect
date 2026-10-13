from typing import Dict, Any, List
from backend.agents.state import AgentState


def release_gate_agent(state: AgentState) -> AgentState:
    """
    Final decision point before packaging and export.
    Evaluates all validation gates: code syntax, build readiness, API contract,
    database integration, and container specifications.
    Decides APPROVED vs. BLOCKED. Never allows a failing build through.
    """
    code_val = state.get("code_validation", {})
    build_val = state.get("build_validation", {})
    api_val = state.get("api_validation", {})
    db_val = state.get("database_validation", {})
    docker_val = state.get("docker_validation", {})

    code_pass = code_val.get("status") == "PASS" and code_val.get("is_valid", False) is True
    build_pass = build_val.get("status") == "PASS"
    api_pass = api_val.get("status") in ("PASS", "WARN")
    db_pass = db_val.get("status") in ("PASS", "WARN")
    docker_pass = docker_val.get("status") == "PASS"

    checks = {
        "generated_code_validation": {
            "status": code_val.get("status", "FAIL"),
            "passed": code_pass
        },
        "project_build_validation": {
            "status": build_val.get("status", "FAIL"),
            "passed": build_pass
        },
        "api_contract_validation": {
            "status": api_val.get("status", "FAIL"),
            "passed": api_pass
        },
        "database_validation": {
            "status": db_val.get("status", "FAIL"),
            "passed": db_pass
        },
        "docker_validation": {
            "status": docker_val.get("status", "FAIL"),
            "passed": docker_pass
        }
    }

    blocking_issues: List[str] = []
    if not code_pass:
        blocking_issues.extend([f"[Code Validation] {iss}" for iss in code_val.get("issues", ["Code validation failed"])])
    if not build_pass:
        blocking_issues.extend([f"[Build Validation] {iss}" for iss in build_val.get("issues", ["Build validation failed"])])
    if not api_pass:
        blocking_issues.extend([f"[API Contract] {iss}" for iss in api_val.get("issues", ["API contract failed"])])
    if not db_pass:
        blocking_issues.extend([f"[Database] {iss}" for iss in db_val.get("issues", ["Database validation failed"])])
    if not docker_pass:
        blocking_issues.extend([f"[Docker] {iss}" for iss in docker_val.get("issues", ["Docker validation failed"])])

    approved = code_pass and build_pass and api_pass and db_pass and docker_pass
    status = "APPROVED" if approved else "BLOCKED"

    summary = (
        f"Release Gate {status}: "
        f"{sum(1 for c in checks.values() if c['passed'])}/{len(checks)} quality gates passed. "
        f"Total blocking issues: {len(blocking_issues)}."
    )

    release_result = {
        "status": status,
        "approved": approved,
        "checks": checks,
        "blocking_issues": blocking_issues,
        "issues": blocking_issues,
        "summary": summary
    }

    state["release_gate"] = release_result

    architecture = state.get("architecture", {})
    architecture["release_gate"] = release_result
    state["architecture"] = architecture

    return state
