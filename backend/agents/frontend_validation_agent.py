"""
Phase 2 — Frontend Build Validation Agent
==========================================
Validates the generated React/frontend code structure for:
- index.html entry point exists and has <div id="root">
- App.jsx / App.js exists with valid JSX structure
- api.js exists with fetch/axios calls
- Loading component exists
- No obvious JSX syntax catastrophes (unmatched braces)
- Reasonable component count

Does NOT run npm build (too slow for validation phase).
Uses static analysis of generated frontend files.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Any, List

from backend.agents.state import AgentState


def frontend_validation_agent(state: AgentState) -> AgentState:
    """
    Validate frontend structure and basic JSX integrity via static analysis.
    """
    project_path_str = state.get("assembled_project_path", "")
    generated_files: dict = state.get("generated_files", {})

    checks: List[Dict[str, Any]] = []
    issues: List[str] = []

    # ── index.html ────────────────────────────────────────────────────────────
    index_html = _read_file(project_path_str, "frontend/index.html", generated_files)
    if index_html is None:
        issues.append("frontend/index.html missing")
        checks.append({"name": "index_html_exists", "status": "failed", "message": "Missing"})
    else:
        checks.append({"name": "index_html_exists", "status": "passed", "message": "Present"})
        if 'id="root"' not in index_html and "id='root'" not in index_html:
            issues.append("frontend/index.html missing <div id='root'> mount point")
            checks.append({"name": "index_html_root_div", "status": "failed", "message": "Missing root mount point"})
        else:
            checks.append({"name": "index_html_root_div", "status": "passed", "message": "Root div present"})

    # ── App.jsx / App.js ──────────────────────────────────────────────────────
    app_jsx = (
        _read_file(project_path_str, "frontend/src/App.jsx", generated_files)
        or _read_file(project_path_str, "frontend/src/App.js", generated_files)
    )
    if app_jsx is None:
        issues.append("frontend/src/App.jsx missing")
        checks.append({"name": "app_jsx_exists", "status": "failed", "message": "Missing"})
    else:
        checks.append({"name": "app_jsx_exists", "status": "passed", "message": "Present"})

        # Check for React import or JSX return
        has_react_usage = (
            "import React" in app_jsx
            or "from 'react'" in app_jsx
            or 'from "react"' in app_jsx
            or "export default" in app_jsx
        )
        if not has_react_usage:
            issues.append("App.jsx does not appear to be a valid React component")
            checks.append({"name": "app_jsx_react_component", "status": "failed", "message": "No React import or export default"})
        else:
            checks.append({"name": "app_jsx_react_component", "status": "passed", "message": "Valid React component structure"})

        # Check brace balance (catastrophic JSX errors)
        open_braces = app_jsx.count("{")
        close_braces = app_jsx.count("}")
        brace_diff = abs(open_braces - close_braces)
        if brace_diff > 5:  # Allow small diffs for template literals
            issues.append(f"App.jsx has severely unbalanced braces ({open_braces} open vs {close_braces} close)")
            checks.append({"name": "app_jsx_brace_balance", "status": "failed", "message": f"Brace imbalance: {brace_diff}"})
        else:
            checks.append({"name": "app_jsx_brace_balance", "status": "passed", "message": "Brace balance acceptable"})

    # ── api.js ────────────────────────────────────────────────────────────────
    api_js = _read_file(project_path_str, "frontend/src/api.js", generated_files)
    if api_js is None:
        issues.append("frontend/src/api.js missing")
        checks.append({"name": "api_js_exists", "status": "failed", "message": "Missing"})
    else:
        checks.append({"name": "api_js_exists", "status": "passed", "message": "Present"})
        has_http_calls = (
            "fetch(" in api_js
            or "axios" in api_js
            or "export async function" in api_js
            or "export function" in api_js
        )
        if not has_http_calls:
            issues.append("frontend/src/api.js has no HTTP call functions")
            checks.append({"name": "api_js_http_functions", "status": "failed", "message": "No fetch/axios calls"})
        else:
            checks.append({"name": "api_js_http_functions", "status": "passed", "message": "HTTP functions present"})

    # ── Loading component ─────────────────────────────────────────────────────
    loading = _read_file(project_path_str, "frontend/src/components/Loading.jsx", generated_files)
    if loading is None:
        checks.append({"name": "loading_component_exists", "status": "failed", "message": "Missing"})
        # Not critical — just a warning
    else:
        checks.append({"name": "loading_component_exists", "status": "passed", "message": "Present"})

    # ── package.json build entry ──────────────────────────────────────────────
    pkg_json_raw = _read_file(project_path_str, "frontend/package.json", generated_files)
    if pkg_json_raw:
        import json
        try:
            pkg = json.loads(pkg_json_raw)
            scripts = pkg.get("scripts", {})
            has_start = "start" in scripts or "build" in scripts
            if has_start:
                checks.append({"name": "frontend_npm_scripts", "status": "passed", "message": "npm start/build configured"})
            else:
                checks.append({"name": "frontend_npm_scripts", "status": "failed", "message": "No npm scripts defined"})
        except Exception:
            pass

    passed = sum(1 for c in checks if c["status"] == "passed")
    total = len(checks)
    # Loading component missing is not a blocker
    critical_issues = [i for i in issues if "Loading" not in i]

    frontend_result = {
        "status": "PASS" if not critical_issues else "FAIL",
        "checks": checks,
        "issues": issues,
        "summary": (
            f"Frontend validation {'PASS' if not critical_issues else 'FAIL'}: "
            f"{passed}/{total} checks passed. {len(critical_issues)} critical issues."
        ),
        "deployment_ready_contribution": not bool(critical_issues),
    }

    state["frontend_validation"] = frontend_result
    arch = state.get("architecture", {})
    arch["frontend_validation"] = frontend_result
    state["architecture"] = arch
    return state


def _read_file(project_path: str, rel_path: str, generated_files: dict) -> str | None:
    if project_path:
        full = Path(project_path) / rel_path
        if full.exists():
            return full.read_text(encoding="utf-8")
    return generated_files.get(rel_path)
