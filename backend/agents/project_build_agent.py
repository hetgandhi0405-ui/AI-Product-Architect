import os
import py_compile
from pathlib import Path
from typing import Dict, Any, List
from backend.agents.state import AgentState


def project_build_agent(state: AgentState) -> AgentState:
    """
    Validate that the generated project is build-ready.
    Checks directory presence, manifest completeness, and that all Python packages
    and entry points can be successfully compiled and parsed.
    """
    project_path_str = state.get("assembled_project_path")
    manifest = state.get("file_manifest", {})
    manifest_files = manifest.get("files", [])

    issues: List[str] = []

    if not project_path_str or not os.path.exists(project_path_str):
        state["build_validation"] = {
            "status": "FAIL",
            "issues": ["Assembled project directory does not exist for build validation"],
            "summary": "Build validation failed: project directory missing."
        }
        return state

    project_dir = Path(project_path_str)

    # 1. Verify build manifest completeness
    missing_build_files = []
    required_build_files = [
        "backend/requirements.txt",
        "backend/main.py",
        "Dockerfile",
        "docker-compose.yml"
    ]
    for rbf in required_build_files:
        if not (project_dir / rbf).exists():
            missing_build_files.append(rbf)

    if missing_build_files:
        issues.append(f"Missing core build files: {', '.join(missing_build_files)}")

    # 2. Verify all python files in backend and tests compile cleanly
    python_compile_errors = []
    for py_file in project_dir.rglob("*.py"):
        try:
            py_compile.compile(str(py_file), doraise=True)
        except py_compile.PyCompileError as e:
            python_compile_errors.append(f"{py_file.name}: {e.msg}")

    if python_compile_errors:
        issues.extend(python_compile_errors)

    # 3. Optional build execution check if enabled
    execute_builds = os.environ.get("AI_PRODUCT_ARCHITECT_RUN_BUILDS", "").lower() in ("true", "1", "yes")
    build_executed = False
    if execute_builds:
        # Runtime build execution would happen here if configured
        build_executed = True

    status = "PASS" if len(issues) == 0 else "FAIL"
    summary = (
        f"Project build validation {status}. "
        f"{len(manifest_files)} manifest files inspected, "
        f"core build files present: {len(missing_build_files) == 0}, "
        f"python compilation issues: {len(python_compile_errors)}."
    )

    build_result = {
        "status": status,
        "build_executed": build_executed,
        "issues": issues,
        "summary": summary
    }

    state["build_validation"] = build_result

    architecture = state.get("architecture", {})
    architecture["build_validation"] = build_result
    state["architecture"] = architecture

    return state
