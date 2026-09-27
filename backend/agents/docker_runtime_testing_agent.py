import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from backend.agents.state import AgentState


def _run_compose_config(root: Path, timeout: int = 30) -> Dict[str, Any]:
    try:
        completed = subprocess.run(
            ["docker", "compose", "config"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "command": ["docker", "compose", "config"],
            "returncode": completed.returncode,
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-4000:],
            "passed": completed.returncode == 0,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "command": ["docker", "compose", "config"],
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "passed": False,
        }


def docker_runtime_testing_agent(state: AgentState) -> AgentState:
    """Validate Docker/Compose configuration; container startup is opt-in."""
    root = Path(state.get("generated_project_path", ""))
    issues: List[str] = []
    checks: List[str] = []
    results: List[Dict[str, Any]] = []

    if not root.exists():
        issues.append("Generated project directory does not exist.")
    else:
        compose = root / "docker-compose.yml"
        dockerfile = root / "Dockerfile"

        if compose.exists():
            text = compose.read_text(encoding="utf-8")
            if "services:" not in text:
                issues.append("docker-compose.yml is missing services:.")
            else:
                checks.append("docker-compose.yml contains services.")
        else:
            issues.append("Generated project has no docker-compose.yml.")

        if dockerfile.exists():
            text = dockerfile.read_text(encoding="utf-8").upper()
            if "FROM " not in text:
                issues.append("Dockerfile is missing a FROM instruction.")
            else:
                checks.append("Dockerfile contains a FROM instruction.")

        if os.getenv("AI_PRODUCT_ARCHITECT_RUN_DOCKER_TESTS", "0") == "1" and compose.exists():
            result = _run_compose_config(root)
            results.append(result)
            if not result["passed"]:
                issues.append("docker compose config failed.")

    state["docker_runtime_validation"] = {
        "status": "VALID" if not issues else "INVALID",
        "is_valid": not issues,
        "checks": checks,
        "issues": issues,
        "results": results,
        "executed_docker_command": os.getenv("AI_PRODUCT_ARCHITECT_RUN_DOCKER_TESTS", "0") == "1",
        "summary": (
            "Docker runtime configuration checks passed."
            if not issues
            else f"Docker runtime checks found {len(issues)} issue(s)."
        ),
    }
    return state
