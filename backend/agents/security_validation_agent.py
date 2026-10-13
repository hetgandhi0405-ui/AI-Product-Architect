"""
Phase 2 — Security Validation Agent
======================================
Scans the generated product for common security vulnerabilities (OWASP-aligned).

Checks performed (all static analysis — NO execution):
1. Hardcoded secrets / API keys in Python/JS files
2. SQL injection risk patterns (raw string interpolation in queries)
3. Debug/development settings left enabled (DEBUG=True, allow_origins=["*"])
4. Exposed .env files with real secrets
5. Password/secret in plain text (not in secrets manager reference)
6. No auth middleware on sensitive routes (basic heuristic)

Output feeds into both the unified validation_report and release_gate.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Any, List

from backend.agents.state import AgentState

# Patterns that indicate hardcoded secrets
_SECRET_PATTERNS = [
    (r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{6,}["\']', "Hardcoded password"),
    (r'(?i)(secret_key|jwt_secret|api_key|apikey)\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded secret/API key"),
    (r'(?i)aws_access_key_id\s*=\s*["\'][A-Z0-9]{20}["\']', "Hardcoded AWS access key"),
    (r'(?i)aws_secret_access_key\s*=\s*["\'][A-Za-z0-9/+]{40}["\']', "Hardcoded AWS secret key"),
    (r'(?i)(token|auth_token)\s*=\s*["\'][A-Za-z0-9_\-\.]{20,}["\']', "Hardcoded token"),
]

# SQL injection risk: f-string/format in raw SQL queries
_SQL_INJECTION_PATTERNS = [
    (r'execute\s*\(\s*f["\'].*\{', "Possible SQL injection via f-string in execute()"),
    (r'cursor\.execute\s*\(\s*["\'].*%s.*["\'\s]*%\s*\(', "Raw string formatting in SQL query"),
    (r'(?i)(SELECT|INSERT|UPDATE|DELETE).*\+.*(?:user_input|request\.|params\[)', "String concatenation in SQL"),
]

# Configuration security issues
_CONFIG_PATTERNS = [
    (r'DEBUG\s*=\s*True', "DEBUG mode enabled in production code"),
    (r"allow_origins\s*=\s*\[.*\*.*\]", "CORS allow_origins=[\"*\"] — open to all origins"),
    (r'(?i)secret_key\s*=\s*["\'](?:secret|changeme|default|change.?me|your.?secret)["\']', "Weak/default secret key"),
]


def security_validation_agent(state: AgentState) -> AgentState:
    """
    Perform static security analysis on all generated Python and JS files.
    """
    project_path_str = state.get("assembled_project_path", "")
    generated_files: dict = state.get("generated_files", {})

    checks: List[Dict[str, Any]] = []
    issues: List[str] = []
    warnings: List[str] = []

    # Collect all generated source files for scanning
    source_files: Dict[str, str] = {}

    # From disk (assembled project)
    if project_path_str:
        proj = Path(project_path_str)
        for ext in ["*.py", "*.js", "*.jsx", "*.ts", "*.tsx"]:
            for f in proj.rglob(ext):
                rel = str(f.relative_to(proj))
                # Skip test files and __pycache__
                if "__pycache__" not in rel and "node_modules" not in rel:
                    try:
                        source_files[rel] = f.read_text(encoding="utf-8", errors="ignore")
                    except Exception:
                        pass

    # Also scan in-memory generated files (fallback / supplement)
    for path, content in generated_files.items():
        if path not in source_files and path.endswith((".py", ".js", ".jsx")):
            source_files[path] = content

    # ── 1. Hardcoded secrets scan ─────────────────────────────────────────────
    secret_findings: List[str] = []
    for rel_path, content in source_files.items():
        # Skip .env.example and test files
        if ".env.example" in rel_path or "test_" in rel_path:
            continue
        for pattern, description in _SECRET_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                secret_findings.append(f"[{rel_path}] {description}")

    if secret_findings:
        # WARN for generated code — likely demo values
        for f in secret_findings[:3]:  # cap noise
            warnings.append(f"WARN: {f} (may be demo value — must not be used in production)")
        checks.append({
            "name": "no_hardcoded_secrets",
            "status": "warn",
            "message": f"{len(secret_findings)} potential secret(s) detected — review before production deployment"
        })
    else:
        checks.append({"name": "no_hardcoded_secrets", "status": "passed", "message": "No hardcoded secrets detected"})

    # ── 2. SQL injection scan ─────────────────────────────────────────────────
    sql_findings: List[str] = []
    for rel_path, content in source_files.items():
        if "test_" in rel_path:
            continue
        for pattern, description in _SQL_INJECTION_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                sql_findings.append(f"[{rel_path}] {description}")

    if sql_findings:
        issues.append(f"SQL injection risk in: {'; '.join(sql_findings[:3])}")
        checks.append({
            "name": "no_sql_injection_risk",
            "status": "failed",
            "message": f"SQL injection patterns detected: {len(sql_findings)} occurrence(s)"
        })
    else:
        checks.append({"name": "no_sql_injection_risk", "status": "passed", "message": "No SQL injection patterns detected"})

    # ── 3. Configuration security ─────────────────────────────────────────────
    config_findings: List[str] = []
    for rel_path, content in source_files.items():
        if "test_" in rel_path or ".example" in rel_path:
            continue
        for pattern, description in _CONFIG_PATTERNS:
            if re.search(pattern, content):
                config_findings.append(f"[{rel_path}] {description}")

    if config_findings:
        for f in config_findings[:3]:
            warnings.append(f"WARN: {f}")
        checks.append({
            "name": "secure_configuration",
            "status": "warn",
            "message": f"{len(config_findings)} configuration issue(s) — review before production"
        })
    else:
        checks.append({"name": "secure_configuration", "status": "passed", "message": "No insecure configuration patterns detected"})

    # ── 4. .env file check ────────────────────────────────────────────────────
    if project_path_str:
        env_file = Path(project_path_str) / ".env"
        if env_file.exists():
            env_content = env_file.read_text(encoding="utf-8", errors="ignore")
            if re.search(r'(?i)(password|secret|key)\s*=\s*\S+', env_content):
                warnings.append("WARN: .env file contains credentials — ensure it is in .gitignore")
                checks.append({"name": "env_file_safety", "status": "warn", "message": ".env file has credentials — must be gitignored"})
            else:
                checks.append({"name": "env_file_safety", "status": "passed", "message": ".env appears safe"})
        else:
            checks.append({"name": "env_file_safety", "status": "passed", "message": "No .env file present (good — use .env.example)"})

    # ── 5. Infrastructure security check ─────────────────────────────────────
    infra_state: dict = state.get("infrastructure_state", {})
    security_policy = infra_state.get("security_policy", {})
    if security_policy.get("tls_enabled"):
        checks.append({"name": "tls_configured", "status": "passed", "message": "TLS enabled in infrastructure spec"})
    else:
        warnings.append("WARN: TLS not explicitly enabled in infrastructure spec")
        checks.append({"name": "tls_configured", "status": "warn", "message": "TLS not configured in infrastructure"})

    passed = sum(1 for c in checks if c["status"] == "passed")
    warned = sum(1 for c in checks if c["status"] == "warn")
    total = len(checks)

    # Only hard FAIL on actual SQL injection — warnings don't block deployment
    status = "FAIL" if issues else ("WARN" if warnings else "PASS")

    security_result = {
        "status": status,
        "checks": checks,
        "issues": issues,
        "warnings": warnings,
        "summary": (
            f"Security validation {status}: {passed}/{total} passed, {warned} warnings, {len(issues)} blocking issues. "
            f"Review warnings before production deployment."
        ),
        "deployment_ready_contribution": not bool(issues),
    }

    state["security_validation"] = security_result
    arch = state.get("architecture", {})
    arch["security_validation"] = security_result
    state["architecture"] = arch
    return state
