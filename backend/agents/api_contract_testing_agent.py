import os
import re
from pathlib import Path
from typing import Dict, Any, List
from backend.agents.state import AgentState


def api_contract_testing_agent(state: AgentState) -> AgentState:
    """
    Validate that the generated backend implementation and frontend client
    satisfy the agreed API specification contract via static code analysis.
    """
    project_path_str = state.get("assembled_project_path")
    api_spec = state.get("api_specification", {})
    expected_endpoints = api_spec.get("endpoints", [])

    if not project_path_str or not os.path.exists(project_path_str):
        state["api_validation"] = {
            "status": "FAIL",
            "mode": "STATIC_CONTRACT_ANALYSIS",
            "endpoints_checked": [],
            "issues": ["Project directory does not exist for API contract validation"],
            "summary": "API validation failed: project directory missing."
        }
        return state

    project_dir = Path(project_path_str)
    backend_api_file = project_dir / "backend" / "routes" / "api.py"
    backend_main_file = project_dir / "backend" / "main.py"
    frontend_api_file = project_dir / "frontend" / "src" / "api.js"

    # Read backend code
    backend_code = ""
    if backend_api_file.exists():
        backend_code += backend_api_file.read_text(encoding="utf-8")
    if backend_main_file.exists():
        backend_code += "\n" + backend_main_file.read_text(encoding="utf-8")

    # Read frontend code
    frontend_code = ""
    if frontend_api_file.exists():
        frontend_code = frontend_api_file.read_text(encoding="utf-8")

    issues: List[str] = []
    endpoints_checked: List[Dict[str, Any]] = []

    # If no endpoints were defined in spec, treat as empty contract or standard routes
    if not expected_endpoints:
        # Check if backend at least has basic endpoints
        has_routes = bool(re.search(r"@router\.(get|post|put|delete|patch)", backend_code))
        status = "PASS" if has_routes else "WARN"
        summary = "No explicit endpoints in API specification. Basic backend router verified."
        state["api_validation"] = {
            "status": status,
            "mode": "STATIC_CONTRACT_ANALYSIS",
            "endpoints_checked": [],
            "issues": issues,
            "summary": summary
        }
        return state

    for ep in expected_endpoints:
        method = ep.get("method", "GET").upper()
        raw_endpoint = ep.get("endpoint", "")
        # Normalize endpoint path
        normalized_path = "/" + raw_endpoint.strip("/")
        # Extract base path without parameters for regex checking (e.g. /tasks/{id} -> /tasks)
        base_route_pattern = re.sub(r'\{[a-zA-Z_]+\}', r'[^"]+', normalized_path)

        # Check backend router registration
        # Regex matching: @router.get("/tasks...") or @app.get("/tasks...")
        method_lower = method.lower()
        backend_pattern = rf'@(?:router|app)\.{method_lower}\s*\(\s*["\'](?:/api)?{base_route_pattern}["\']'
        backend_match = bool(re.search(backend_pattern, backend_code, re.IGNORECASE))

        # Check if route pattern appears anywhere in backend routes if strict decorator didn't match
        if not backend_match:
            simple_path_pattern = rf'["\'](?:/api)?{base_route_pattern}["\']'
            backend_match = bool(re.search(simple_path_pattern, backend_code))

        # Check frontend invocation
        clean_path_frag = re.sub(r'\{[a-zA-Z_]+\}', '', normalized_path).strip('/')
        frontend_match = clean_path_frag in frontend_code if clean_path_frag else True

        check_record = {
            "method": method,
            "endpoint": normalized_path,
            "backend_implemented": backend_match,
            "frontend_referenced": frontend_match,
        }
        endpoints_checked.append(check_record)

        if not backend_match:
            issues.append(f"Backend route missing or method mismatch: [{method}] {normalized_path}")

    status = "PASS" if len(issues) == 0 else "FAIL"
    summary = (
        f"API contract static analysis {status}: "
        f"{sum(1 for c in endpoints_checked if c['backend_implemented'])}/{len(endpoints_checked)} "
        f"endpoints implemented in backend. Issues detected: {len(issues)}."
    )

    api_result = {
        "status": status,
        "mode": "STATIC_CONTRACT_ANALYSIS",
        "endpoints_checked": endpoints_checked,
        "issues": issues,
        "summary": summary
    }

    state["api_validation"] = api_result

    architecture = state.get("architecture", {})
    architecture["api_validation"] = api_result
    state["architecture"] = architecture

    return state
