from typing import Any, Dict, List, Optional
from backend.agents.state import AgentState

FORMULA_DOCUMENTATION = (
    "Score = 0.35 * performance_score + 0.30 * reliability_score + 0.25 * cost_score + 0.10 * complexity_score. "
    "All criteria normalized 0-100. Cost score = max(0, min(100, (120 - monthly_usd) / 120 * 100)). "
    "Complexity score = 100 - (15 if tasks > 1 else 0) - (15 if db != micro else 0). "
    "Hard gate: requirement_compliance == 100% required, else DISQUALIFIED."
)

WEIGHTS = {
    "performance": 0.35,
    "reliability": 0.30,
    "cost": 0.25,
    "complexity": 0.10,
}


def score_architecture(
    perf_val: float,
    rel_val: float,
    cost_usd: float,
    tasks: int,
    db_class: str,
    compliance: float,
) -> Dict[str, Any]:
    """Calculate deterministic scores across all dimensions."""
    if compliance < 100.0:
        return {
            "disqualified": True,
            "disqualification_reason": f"Requirement compliance is {compliance}% (< 100% hard gate)",
            "total_score": 0.0,
            "subscores": {},
        }

    # Normalize performance 0-100
    norm_perf = max(0.0, min(100.0, float(perf_val)))

    # Normalize reliability 0-100
    norm_rel = max(0.0, min(100.0, float(rel_val)))

    # Normalize cost (lower is better, baseline scale up to $120/mo)
    norm_cost = max(0.0, min(100.0, ((120.0 - cost_usd) / 120.0) * 100.0))

    # Normalize complexity (simpler single-task/micro setups score higher)
    penalty = (15.0 if tasks > 1 else 0.0) + (15.0 if db_class != "db.t4g.micro" else 0.0)
    norm_complexity = max(0.0, 100.0 - penalty)

    total = (
        WEIGHTS["performance"] * norm_perf
        + WEIGHTS["reliability"] * norm_rel
        + WEIGHTS["cost"] * norm_cost
        + WEIGHTS["complexity"] * norm_complexity
    )

    return {
        "disqualified": False,
        "total_score": round(total, 2),
        "subscores": {
            "performance": round(norm_perf, 2),
            "reliability": round(norm_rel, 2),
            "cost": round(norm_cost, 2),
            "complexity": round(norm_complexity, 2),
        },
    }


def candidate_evaluation_agent(state: AgentState) -> AgentState:
    """
    Evaluates baseline architecture and candidates with a deterministic scoring formula.
    Hard gate: requirement_compliance must be 100%.
    """
    candidates = state.get("optimization_candidates", [])
    cost_analysis = state.get("cost_analysis", {})
    base_cost = cost_analysis.get("monthly_total_usd", 55.0)

    # Score baseline current architecture
    baseline_evaluation = score_architecture(
        perf_val=80.0,
        rel_val=80.0,
        cost_usd=base_cost,
        tasks=1,
        db_class="db.t4g.micro",
        compliance=100.0,
    )
    baseline_evaluation["architecture_id"] = "current_baseline"
    baseline_evaluation["cost_usd"] = base_cost

    evaluated_candidates: List[Dict[str, Any]] = []

    for cand in candidates:
        cand_id = cand.get("candidate_id")
        comp = cand.get("requirement_compliance", 100.0)
        cost_val = cand.get("estimated_cost", {}).get("monthly_usd", 50.0)
        perf_val = cand.get("expected_performance", {}).get("score", 80.0)
        rel_val = cand.get("expected_reliability", {}).get("score", 80.0)
        changes = cand.get("infrastructure_changes", {})

        tasks = changes.get("desired_count", 1)
        db_cls = changes.get("db_instance_class", "db.t4g.micro")

        eval_res = score_architecture(
            perf_val=perf_val,
            rel_val=rel_val,
            cost_usd=cost_val,
            tasks=tasks,
            db_class=db_cls,
            compliance=comp,
        )

        evaluated_candidates.append({
            "candidate_id": cand_id,
            "architecture": cand.get("architecture"),
            "disqualified": eval_res["disqualified"],
            "disqualification_reason": eval_res.get("disqualification_reason"),
            "total_score": eval_res["total_score"],
            "subscores": eval_res["subscores"],
            "cost_usd": cost_val,
            "tfvars_path": cand.get("tfvars_path"),
            "reasoning": cand.get("reasoning"),
        })

    # Sort candidates by total score descending, tie break: lower cost, then candidate_id
    evaluated_candidates.sort(
        key=lambda c: (-c["total_score"], c["cost_usd"], c["candidate_id"])
    )

    state["candidate_evaluation"] = {
        "formula": FORMULA_DOCUMENTATION,
        "weights": WEIGHTS,
        "baseline": baseline_evaluation,
        "evaluated_candidates": evaluated_candidates,
    }

    return state
