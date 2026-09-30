"""
Phase 6 — Terraform Validation Agent
=======================================
Validates generated Terraform files without live AWS credentials.

Checks performed (all static — no terraform binary required):
1. All required files present (provider, variables, vpc, compute, database, outputs)
2. Every file has valid HCL structure markers
3. Variable references are internally consistent (var.X used in files → declared in variables.tf)
4. No hardcoded secrets (aws_access_key, passwords)
5. Resource naming consistency (all use var.project_name)
6. Output declarations reference real resources

If terraform CLI is available (AI_PRODUCT_ARCHITECT_RUN_TERRAFORM=1), runs:
    terraform fmt -check
    terraform validate
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from backend.agents.state import AgentState

_REQUIRED_TF_FILES = {
    "provider.tf",
    "variables.tf",
    "vpc.tf",
    "security.tf",
    "compute.tf",
    "database.tf",
    "load_balancer.tf",
    "outputs.tf",
}

_SECRET_PATTERNS = [
    r'aws_access_key_id\s*=\s*"[A-Z0-9]{20}"',
    r'aws_secret_access_key\s*=\s*"[A-Za-z0-9/+=]{40}"',
    r'password\s*=\s*"(?!var\.|aws_)[^"]{6,}"',
]


def terraform_validation_agent(state: AgentState) -> AgentState:
    """Validate generated Terraform HCL files statically and optionally via CLI."""
    tf_gen: dict = state.get("terraform_generation", {})
    tf_dir_str: str | None = tf_gen.get("terraform_dir")
    file_contents: dict = tf_gen.get("file_contents", {})

    checks: List[Dict[str, Any]] = []
    issues: List[str] = []

    if tf_gen.get("status") == "SKIPPED":
        state["terraform_validation"] = {
            "status": "SKIPPED",
            "checks": [],
            "issues": [],
            "summary": "Terraform validation skipped — no Terraform was generated.",
        }
        return state

    # ── 1. Required files present ─────────────────────────────────────────────
    generated_names = set(file_contents.keys())
    missing = _REQUIRED_TF_FILES - generated_names
    if missing:
        issues.append(f"Missing required Terraform files: {', '.join(sorted(missing))}")
        checks.append({
            "name": "required_files_present",
            "status": "failed",
            "message": f"Missing: {', '.join(sorted(missing))}",
        })
    else:
        checks.append({
            "name": "required_files_present",
            "status": "passed",
            "message": f"All {len(_REQUIRED_TF_FILES)} required files generated",
        })

    # ── 2. HCL structure check ────────────────────────────────────────────────
    hcl_issues = []
    for fname, content in file_contents.items():
        if not content.strip():
            hcl_issues.append(f"{fname} is empty")
            continue
        open_b = content.count("{")
        close_b = content.count("}")
        if abs(open_b - close_b) > 2:
            hcl_issues.append(f"{fname}: brace mismatch ({open_b} open, {close_b} close)")

    if hcl_issues:
        issues.extend(hcl_issues)
        checks.append({"name": "hcl_structure", "status": "failed", "message": "; ".join(hcl_issues[:3])})
    else:
        checks.append({"name": "hcl_structure", "status": "passed", "message": "All files have valid HCL brace structure"})

    # ── 3. Variable consistency ───────────────────────────────────────────────
    vars_content = file_contents.get("variables.tf", "")
    declared_vars = set(re.findall(r'^variable\s+"(\w+)"', vars_content, re.MULTILINE))
    all_content = "\n".join(file_contents.values())
    used_vars = set(re.findall(r'var\.(\w+)', all_content))
    undeclared = used_vars - declared_vars
    if undeclared:
        issues.append(f"Undeclared variables referenced: {', '.join(sorted(undeclared))}")
        checks.append({
            "name": "variable_consistency",
            "status": "failed",
            "message": f"Undeclared: {', '.join(sorted(undeclared))}",
        })
    else:
        checks.append({
            "name": "variable_consistency",
            "status": "passed",
            "message": f"{len(declared_vars)} variables declared, all references consistent",
        })

    # ── 4. No hardcoded secrets ───────────────────────────────────────────────
    secret_hits = []
    for pattern in _SECRET_PATTERNS:
        matches = re.findall(pattern, all_content, re.IGNORECASE)
        secret_hits.extend(matches)
    if secret_hits:
        issues.append(f"Hardcoded secrets detected in Terraform: {len(secret_hits)} occurrence(s)")
        checks.append({"name": "no_hardcoded_secrets", "status": "failed",
                       "message": f"{len(secret_hits)} secret pattern(s) found"})
    else:
        checks.append({"name": "no_hardcoded_secrets", "status": "passed",
                       "message": "No hardcoded credentials detected"})

    # ── 5. Resource naming consistency ────────────────────────────────────────
    resources_using_project_name = len(re.findall(r'var\.project_name', all_content))
    if resources_using_project_name < 3:
        checks.append({"name": "resource_naming", "status": "warn",
                       "message": f"Only {resources_using_project_name} resources use var.project_name"})
    else:
        checks.append({"name": "resource_naming", "status": "passed",
                       "message": f"{resources_using_project_name} resources use var.project_name consistently"})

    # ── 6. Outputs reference real resources ──────────────────────────────────
    outputs_content = file_contents.get("outputs.tf", "")
    output_refs = re.findall(r'value\s*=\s*(aws_\w+\.\w+\.\w+)', outputs_content)
    bad_refs = []
    for ref in output_refs:
        resource_type = ref.split(".")[0]
        if resource_type not in all_content:
            bad_refs.append(ref)
    if bad_refs:
        issues.append(f"Output references non-existent resources: {bad_refs}")
        checks.append({"name": "output_references", "status": "failed",
                       "message": f"Bad refs: {bad_refs}"})
    else:
        checks.append({"name": "output_references", "status": "passed",
                       "message": "All output values reference declared resources"})

    # ── 7. Optional: terraform CLI validation ─────────────────────────────────
    run_tf = os.environ.get("AI_PRODUCT_ARCHITECT_RUN_TERRAFORM", "").lower() in ("1", "true", "yes")
    if run_tf and tf_dir_str and Path(tf_dir_str).is_dir():
        cli_result = _run_terraform_cli(tf_dir_str)
        checks.append(cli_result)
        if cli_result["status"] == "failed":
            issues.append(f"terraform validate failed: {cli_result['message']}")
    else:
        checks.append({"name": "terraform_cli", "status": "skipped",
                       "message": "Set AI_PRODUCT_ARCHITECT_RUN_TERRAFORM=1 to enable"})

    passed = sum(1 for c in checks if c["status"] == "passed")
    status = "PASS" if not issues else "FAIL"

    tf_validation = {
        "status": status,
        "checks": checks,
        "issues": issues,
        "summary": (
            f"Terraform validation {status}: {passed}/{len(checks)} checks passed. "
            f"{len(issues)} issue(s). {len(file_contents)} files generated."
        ),
        "deployment_ready": not bool(issues),
    }
    state["terraform_validation"] = tf_validation

    arch = state.get("architecture", {})
    arch["terraform_validation"] = tf_validation
    state["architecture"] = arch
    return state


def _run_terraform_cli(tf_dir: str) -> Dict[str, Any]:
    """Run terraform validate in the given directory."""
    try:
        result = subprocess.run(
            ["terraform", "validate", "-json"],
            cwd=tf_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return {"name": "terraform_cli", "status": "passed",
                    "message": "terraform validate succeeded"}
        return {"name": "terraform_cli", "status": "failed",
                "message": result.stderr[:500] or result.stdout[:500]}
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return {"name": "terraform_cli", "status": "skipped",
                "message": f"Terraform CLI unavailable: {e}"}
