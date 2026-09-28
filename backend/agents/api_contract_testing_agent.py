import re
from pathlib import Path
from typing import List, Set, Tuple

from backend.agents.state import AgentState

_HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"}


def _normalize_path(path: str) -> str:
    path = path.strip().strip("'").strip('"')
    if not path.startswith("/"):
        path = "/" + path
    path = re.sub(r"/+", "/", path)
    return path.rstrip("/") or "/"


def _spec_endpoints(state: AgentState) -> Set[Tuple[str, str]]:
    spec = state.get("api_specification", {})
    endpoints = spec.get("endpoints", []) if isinstance(spec, dict) else []
    found = set()
    base = str(spec.get("base_path", "")).strip("/") if isinstance(spec, dict) else ""
    for item in endpoints:
        if not isinstance(item, dict):
            continue
        method = str(item.get("method", "GET")).upper()
        endpoint = item.get("endpoint")
        if method in _HTTP_METHODS and isinstance(endpoint, str):
            path = _normalize_path(f"/{base}/{endpoint.strip('/')}" if base else endpoint)
            found.add((method, path))
    return found


def _backend_routes(root: Path) -> Set[Tuple[str, str]]:
    routes = set()
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(
            r'@(?:app|router)\.(get|post|put|patch|delete|options|head)\(\s*[\'"]([^\'"]+)',
            text,
            re.IGNORECASE,
        ):
            routes.add((match.group(1).upper(), _normalize_path(match.group(2))))
    return routes


def _frontend_calls(root: Path) -> List[Tuple[str, str, str]]:
    calls = []
    frontend = root / "frontend"
    if not frontend.exists():
        return calls
    for path in frontend.rglob("*"):
        if not path.is_file() or path.suffix not in {".js", ".jsx", ".ts", ".tsx"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for match in re.finditer(
            r'\b(fetch|axios\.(?:get|post|put|patch|delete))\s*\(\s*[\'"]([^\'"]+)',
            text,
            re.IGNORECASE,
        ):
            method = "GET" if "." not in match.group(1) else match.group(1).split(".", 1)[1].upper()
            raw = match.group(2)
            if method in _HTTP_METHODS and raw.startswith("/"):
                calls.append((method, _normalize_path(raw), str(path.relative_to(root))))
    return calls


def api_contract_testing_agent(state: AgentState) -> AgentState:
    root = Path(state.get("generated_project_path", ""))
    issues = []
    checks = []

    if not root.exists():
        issues.append("Generated project directory does not exist.")
    else:
        spec_routes = _spec_endpoints(state)
        backend_routes = _backend_routes(root)
        frontend_calls = _frontend_calls(root)

        for method, path in sorted(spec_routes - backend_routes):
            issues.append(f"API specification route is missing from backend: {method} {path}")
        for method, path in sorted(backend_routes - spec_routes):
            issues.append(f"Backend route is missing from API specification: {method} {path}")

        for method, path, source in frontend_calls:
            if spec_routes and (method, path) not in spec_routes:
                issues.append(f"Frontend API call is not declared in API specification: {method} {path} ({source})")
            if backend_routes and (method, path) not in backend_routes:
                issues.append(f"Frontend API call has no matching backend route: {method} {path} ({source})")

        checks.extend([
            f"API specification routes: {len(spec_routes)}",
            f"Backend routes discovered: {len(backend_routes)}",
            f"Frontend API calls discovered: {len(frontend_calls)}",
        ])
        if not spec_routes:
            issues.append("API specification contains no usable endpoints.")

    state["api_contract_validation"] = {
        "status": "VALID" if not issues else "INVALID",
        "is_valid": not issues,
        "checks": checks,
        "issues": issues,
        "summary": "API contract checks passed." if not issues else f"API contract checks found {len(issues)} issue(s).",
    }
    return state
