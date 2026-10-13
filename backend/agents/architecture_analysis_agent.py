from typing import Any, Dict, List
from backend.agents.state import AgentState


def architecture_analysis_agent(state: AgentState) -> AgentState:
    """
    Synthesizes overall architecture health by comparing requirements,
    infrastructure specifications, cost breakdown, and telemetry/reliability.
    Vocabulary: HEALTHY | DEGRADED | UNHEALTHY | INSUFFICIENT_DATA
    """
    reqs = state.get("requirements", "")
    arch = state.get("architecture", {})
    infra = arch.get("infrastructure", {})

    perf = state.get("performance_analysis", {})
    cost = state.get("cost_analysis", {})
    reliability = state.get("reliability_analysis", {})
    telemetry_status = state.get("telemetry_status", "SKIPPED")

    problems: List[Dict[str, Any]] = []
    recommendations: List[str] = []

    # 1. Performance problems
    for p in perf.get("detected_problems", []):
        problems.append({
            "dimension": "performance",
            "problem": p.get("problem"),
            "evidence": p.get("evidence"),
        })
    recommendations.extend(perf.get("recommendations", []))

    # 2. Reliability problems
    for issue in reliability.get("detected_issues", []):
        problems.append({
            "dimension": "reliability",
            "problem": "host_or_error_fault",
            "evidence": issue,
        })

    # 3. Cost considerations
    monthly_cost = cost.get("monthly_total_usd", 0.0)
    if monthly_cost > 75.0:
        problems.append({
            "dimension": "cost",
            "problem": "high_monthly_run_rate",
            "evidence": f"Estimated monthly cost of ${monthly_cost} exceeds $75 baseline target",
        })
        recommendations.append("Apply cost optimization overrides to downsize idle capacity.")

    # 4. Determine overall architecture status
    if any(p.get("dimension") == "reliability" for p in problems) or perf.get("status") == "UNHEALTHY":
        arch_status = "UNHEALTHY"
    elif problems or perf.get("status") == "DEGRADED":
        arch_status = "DEGRADED"
    elif telemetry_status in ("SKIPPED", "UNAVAILABLE"):
        arch_status = "HEALTHY" if not problems else "DEGRADED"
    else:
        arch_status = "HEALTHY"

    is_runtime = telemetry_status == "PASSED"
    runtime_note = "analyzed with live runtime telemetry" if is_runtime else "no runtime data (static architecture analysis)"

    state["architecture_analysis"] = {
        "architecture_status": arch_status,
        "problems": problems,
        "recommendations": list(dict.fromkeys(recommendations)),  # deduplicate
        "evaluated_dimensions": {
            "performance_status": perf.get("status", "INSUFFICIENT_DATA"),
            "reliability_status": reliability.get("status", "INSUFFICIENT_DATA"),
            "monthly_cost_usd": monthly_cost,
            "runtime_telemetry_available": is_runtime,
        },
        "note": runtime_note,
    }

    return state
