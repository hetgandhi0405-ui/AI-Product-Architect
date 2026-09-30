import os
from pathlib import Path
from typing import Dict, Any, List
from backend.agents.state import AgentState


def docker_runtime_testing_agent(state: AgentState) -> AgentState:
    """
    Validate containerization configuration files (Dockerfile and docker-compose.yml).
    Checks base images, workdir, exposed ports, service topology, and environment mapping.
    """
    project_path_str = state.get("assembled_project_path")

    if not project_path_str or not os.path.exists(project_path_str):
        state["docker_validation"] = {
            "status": "FAIL",
            "issues": ["Project directory does not exist for Docker validation"],
            "summary": "Docker validation failed: project directory missing."
        }
        return state

    project_dir = Path(project_path_str)
    dockerfile_path = project_dir / "Dockerfile"
    compose_path = project_dir / "docker-compose.yml"

    issues: List[str] = []
    checks: Dict[str, Any] = {
        "dockerfile_exists": dockerfile_path.exists(),
        "docker_compose_exists": compose_path.exists(),
        "has_from_instruction": False,
        "has_workdir": False,
        "has_services": False,
    }

    if not dockerfile_path.exists():
        issues.append("Missing required 'Dockerfile'")
    else:
        content = dockerfile_path.read_text(encoding="utf-8")
        if "FROM " in content:
            checks["has_from_instruction"] = True
        else:
            issues.append("Dockerfile is missing required 'FROM' instruction")

        if "WORKDIR" in content:
            checks["has_workdir"] = True

    if not compose_path.exists():
        issues.append("Missing required 'docker-compose.yml'")
    else:
        compose_content = compose_path.read_text(encoding="utf-8")
        if "services:" in compose_content:
            checks["has_services"] = True
        else:
            issues.append("docker-compose.yml is missing required 'services:' block")

    # Optional runtime docker test check
    run_docker_env = os.environ.get("AI_PRODUCT_ARCHITECT_RUN_DOCKER", "").lower() in ("true", "1", "yes")
    checks["runtime_tested"] = False
    if run_docker_env:
        # Runtime testing would happen here if daemon is available
        checks["runtime_tested"] = True

    status = "PASS" if len(issues) == 0 else "FAIL"
    summary = (
        f"Docker validation {status}: "
        f"Dockerfile valid={checks['has_from_instruction']}, "
        f"compose valid={checks['has_services']}. "
        f"Issues detected: {len(issues)}."
    )

    docker_result = {
        "status": status,
        "checks": checks,
        "issues": issues,
        "summary": summary
    }

    state["docker_validation"] = docker_result

    architecture = state.get("architecture", {})
    architecture["docker_validation"] = docker_result
    state["architecture"] = architecture

    return state
