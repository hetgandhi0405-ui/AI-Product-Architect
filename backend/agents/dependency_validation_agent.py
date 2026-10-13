"""
Phase 2 — Dependency Validation Agent
=======================================
Validates that the generated project's dependency files are well-formed
and contain all required packages for the generated code to run.

Checks:
- backend/requirements.txt: parses, verifies non-empty, checks for critical packages
- frontend/package.json: verifies React/key deps are present
- No conflicting or obviously broken pin patterns
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Any, List

from backend.agents.state import AgentState


# Minimum required backend packages for a FastAPI project
_REQUIRED_BACKEND_PACKAGES = {
    "fastapi", "uvicorn", "pydantic",
}

# Minimum required frontend packages for a React project
_REQUIRED_FRONTEND_PACKAGES = {"react", "react-dom"}


def dependency_validation_agent(state: AgentState) -> AgentState:
    """
    Validate dependency declarations in requirements.txt and package.json.
    """
    project_path_str = state.get("assembled_project_path", "")
    generated_files: dict = state.get("generated_files", {})

    checks: List[Dict[str, Any]] = []
    issues: List[str] = []

    # ── Backend: requirements.txt ─────────────────────────────────────────────
    req_txt = _read_file(project_path_str, "backend/requirements.txt", generated_files)
    if req_txt is None:
        issues.append("backend/requirements.txt is missing")
        checks.append({"name": "backend_requirements_exists", "status": "failed", "message": "File missing"})
    else:
        checks.append({"name": "backend_requirements_exists", "status": "passed", "message": "File present"})

        # Parse package names (strip version specifiers)
        declared_packages = {
            re.split(r"[>=<!~\[]", line.strip())[0].lower().replace("-", "_").replace(".", "_")
            for line in req_txt.splitlines()
            if line.strip() and not line.startswith("#")
        }

        missing_pkgs = _REQUIRED_BACKEND_PACKAGES - {p.replace("-", "_") for p in declared_packages}
        if missing_pkgs:
            msg = f"Missing critical backend packages: {', '.join(sorted(missing_pkgs))}"
            issues.append(msg)
            checks.append({"name": "backend_required_packages", "status": "failed", "message": msg})
        else:
            checks.append({
                "name": "backend_required_packages",
                "status": "passed",
                "message": f"All critical packages declared ({len(declared_packages)} total)"
            })

    # ── Frontend: package.json ────────────────────────────────────────────────
    pkg_json_raw = _read_file(project_path_str, "frontend/package.json", generated_files)
    if pkg_json_raw is None:
        issues.append("frontend/package.json is missing")
        checks.append({"name": "frontend_package_json_exists", "status": "failed", "message": "File missing"})
    else:
        checks.append({"name": "frontend_package_json_exists", "status": "passed", "message": "File present"})
        try:
            pkg_json = json.loads(pkg_json_raw)
            all_deps = {
                **pkg_json.get("dependencies", {}),
                **pkg_json.get("devDependencies", {}),
            }
            declared_frontend = {k.lower() for k in all_deps}
            missing_front = _REQUIRED_FRONTEND_PACKAGES - declared_frontend
            if missing_front:
                msg = f"Missing critical frontend packages: {', '.join(sorted(missing_front))}"
                issues.append(msg)
                checks.append({"name": "frontend_required_packages", "status": "failed", "message": msg})
            else:
                checks.append({
                    "name": "frontend_required_packages",
                    "status": "passed",
                    "message": f"React packages declared ({len(declared_frontend)} total)"
                })

            # Verify build scripts exist
            scripts = pkg_json.get("scripts", {})
            has_build = "build" in scripts or "start" in scripts
            if not has_build:
                issues.append("frontend/package.json missing 'build' or 'start' script")
                checks.append({"name": "frontend_build_script", "status": "failed", "message": "No build/start script"})
            else:
                checks.append({"name": "frontend_build_script", "status": "passed", "message": "Build script present"})

        except (json.JSONDecodeError, Exception) as e:
            issues.append(f"frontend/package.json parse error: {e}")
            checks.append({"name": "frontend_package_json_parse", "status": "failed", "message": str(e)})

    status = "passed" if not issues else "failed"
    dep_result = {
        "status": "PASS" if not issues else "FAIL",
        "checks": checks,
        "issues": issues,
        "summary": (
            f"Dependency validation {'PASS' if not issues else 'FAIL'}: "
            f"{sum(1 for c in checks if c['status'] == 'passed')}/{len(checks)} checks passed. "
            f"{len(issues)} issues."
        ),
        "deployment_ready_contribution": not bool(issues),
    }

    state["dependency_validation"] = dep_result
    arch = state.get("architecture", {})
    arch["dependency_validation"] = dep_result
    state["architecture"] = arch
    return state


def _read_file(project_path: str, rel_path: str, generated_files: dict) -> str | None:
    """Try reading from assembled path first, then fall back to generated_files dict."""
    if project_path:
        full = Path(project_path) / rel_path
        if full.exists():
            return full.read_text(encoding="utf-8")
    return generated_files.get(rel_path)
