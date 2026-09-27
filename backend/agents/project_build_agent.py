import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from backend.agents.state import AgentState


def _run(command: List[str], cwd: Path, timeout: int) -> Dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-4000:],
            "passed": completed.returncode == 0,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "command": command,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "passed": False,
        }


def project_build_agent(state: AgentState) -> AgentState:
    """Validate the generated project build surface without executing generated code by default.

    Set AI_PRODUCT_ARCHITECT_RUN_GENERATED_BUILDS=1 to opt into running
    explicitly supported build commands in the generated project.
    """
    root = Path(state.get("generated_project_path", ""))
    results: List[Dict[str, Any]] = []
    issues: List[str] = []

    if not root.exists():
        issues.append("Generated project directory does not exist.")
    else:
        manifest = state.get("file_manifest", {}).get("files", [])
        paths = {item.get("path") for item in manifest}

        if "backend/main.py" in paths:
            backend_main = root / "backend" / "main.py"
            if not backend_main.exists():
                issues.append("Manifest contains backend/main.py but the file is missing.")

        if "frontend/package.json" in paths:
            package_json = root / "frontend" / "package.json"
            if not package_json.exists():
                issues.append("Manifest contains frontend/package.json but the file is missing.")

        if "docker-compose.yml" in paths and not (root / "docker-compose.yml").exists():
            issues.append("Manifest contains docker-compose.yml but the file is missing.")

        if "infrastructure/main.tf" in paths and not (root / "infrastructure" / "main.tf").exists():
            issues.append("Manifest contains infrastructure/main.tf but the file is missing.")

        # Always perform Python compilation without importing or executing generated modules.
        python_files = list(root.rglob("*.py"))
        for path in python_files:
            result = _run(
                ["python", "-m", "py_compile", str(path)],
                cwd=root,
                timeout=10,
            )
            results.append(result)
            if not result["passed"]:
                issues.append(f"Python build check failed: {path.relative_to(root)}")

        # Full package/container builds are opt-in because generated code is untrusted.
        if os.getenv("AI_PRODUCT_ARCHITECT_RUN_GENERATED_BUILDS", "0") == "1":
            if (root / "frontend" / "package.json").exists():
                results.append(
                    _run(["npm", "run", "build"], cwd=root / "frontend", timeout=120)
                )
            if (root / "docker-compose.yml").exists():
                results.append(
                    _run(["docker", "compose", "config"], cwd=root, timeout=30)
                )

    passed = not issues and all(result["passed"] for result in results)
    state["project_build"] = {
        "status": "PASSED" if passed else "FAILED",
        "is_valid": passed,
        "executed_generated_builds": os.getenv(
            "AI_PRODUCT_ARCHITECT_RUN_GENERATED_BUILDS", "0"
        ) == "1",
        "results": results,
        "issues": issues,
        "summary": (
            "Generated project passed the build gate."
            if passed
            else f"Generated project build gate found {len(issues)} issue(s)."
        ),
    }
    return state
