"""
Phase 2 — Unified Validation Report Agent
==========================================
Aggregates results from ALL Phase 2 validation agents into a single
structured report with a `deployment_ready` boolean flag.

This is the single source of truth for whether the generated product
is safe to proceed to cloud deployment.

Output schema:
{
  "status": "passed|failed",
  "deployment_ready": true|false,
  "checks": [
    {"name": "...", "status": "passed|failed|warn", "message": "..."}
  ],
  "blocking_issues": [...],
  "warnings": [...],
  "gates": {
    "code_validation": "PASS|FAIL",
    "build_validation": "PASS|FAIL",
    "dependency_validation": "PASS|FAIL",
    "frontend_validation": "PASS|FAIL",
    "api_validation": "PASS|FAIL",
    "database_validation": "PASS|FAIL",
    "docker_validation": "PASS|FAIL",
    "security_validation": "PASS|WARN|FAIL"
  },
  "gates_passed": 7,
  "gates_total": 8
}
"""
from __future__ import annotations

from typing import Dict, Any, List
from backend.agents.state import AgentState


# Gates that will BLOCK deployment if they fail (hard gates)
_HARD_GATES = {
    "code_validation",
    "build_validation",
    "api_validation",
    "database_validation",
    "docker_validation",
}

# Gates that produce warnings but don't block deployment
_SOFT_GATES = {
    "dependency_validation",
    "frontend_validation",
    "security_validation",
}


def validation_report_agent(state: AgentState) -> AgentState:
    """
    Aggregate all Phase 2 validation results into a unified deployment_ready report.
    """
    # Collect gate results
    gate_results: Dict[str, Dict[str, Any]] = {
        "code_validation":         state.get("code_validation", {}),
        "build_validation":        state.get("build_validation", {}),
        "dependency_validation":   state.get("dependency_validation", {}),
        "frontend_validation":     state.get("frontend_validation", {}),
        "api_validation":          state.get("api_validation", {}),
        "database_validation":     state.get("database_validation", {}),
        "docker_validation":       state.get("docker_validation", {}),
        "security_validation":     state.get("security_validation", {}),
    }

    gates_summary: Dict[str, str] = {}
    all_checks: List[Dict[str, Any]] = []
    blocking_issues: List[str] = []
    warnings: List[str] = []

    for gate_name, result in gate_results.items():
        gate_status = result.get("status", "FAIL") if result else "SKIPPED"
        gates_summary[gate_name] = gate_status

        # Collect per-check details
        for chk in result.get("checks", []):
            if isinstance(chk, dict):
                all_checks.append({**chk, "gate": gate_name})
            else:
                # Older agents may return strings in checks — normalize
                all_checks.append({"name": str(chk), "status": "passed", "gate": gate_name})

        gate_issues = result.get("issues", [])
        gate_warnings = result.get("warnings", [])

        if gate_name in _HARD_GATES and gate_status == "FAIL":
            blocking_issues.extend([f"[{gate_name}] {iss}" for iss in gate_issues])
        elif gate_name in _SOFT_GATES and gate_status == "FAIL":
            # Soft gate failures are warnings, not blockers
            warnings.extend([f"[{gate_name}] {iss}" for iss in gate_issues])

        warnings.extend(gate_warnings)

    gates_passed = sum(
        1 for g, s in gates_summary.items() if s in ("PASS", "WARN", "SKIPPED")
    )
    hard_gates_passed = all(
        gates_summary.get(g, "FAIL") in ("PASS", "WARN")
        for g in _HARD_GATES
    )

    deployment_ready = hard_gates_passed and not blocking_issues
    overall_status = "passed" if deployment_ready else "failed"

    report = {
        "status": overall_status,
        "deployment_ready": deployment_ready,
        "checks": all_checks,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
        "gates": gates_summary,
        "gates_passed": gates_passed,
        "gates_total": len(gate_results),
        "summary": (
            f"Validation {'PASSED' if deployment_ready else 'FAILED'} — "
            f"{gates_passed}/{len(gate_results)} gates passed. "
            f"{len(blocking_issues)} blocking issue(s), {len(warnings)} warning(s). "
            f"Deployment ready: {deployment_ready}."
        ),
    }

    state["validation_report"] = report

    # Surface into architecture dict for API response
    arch = state.get("architecture", {})
    arch["validation_report"] = report
    state["architecture"] = arch

    return state
