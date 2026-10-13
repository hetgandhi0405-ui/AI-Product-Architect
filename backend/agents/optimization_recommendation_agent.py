from typing import Any, Dict, Optional
from backend.agents.state import AgentState


def optimization_recommendation_agent(state: AgentState) -> AgentState:
    """
    Selects the winning optimization candidate or recommends KEEP_CURRENT.
    Requires beating the baseline score by a minimum margin of 1.5 points.
    No automatic redeployment is triggered.
    """
    evaluation = state.get("candidate_evaluation", {})
    baseline = evaluation.get("baseline", {})
    candidates = evaluation.get("evaluated_candidates", [])
    project_path = state.get("assembled_project_path", "")

    baseline_score = baseline.get("total_score", 0.0)
    improvement_margin = 1.5

    # Filter out disqualified candidates
    valid_candidates = [c for c in candidates if not c.get("disqualified")]

    winner: Optional[Dict[str, Any]] = None
    if valid_candidates:
        best_candidate = valid_candidates[0]
        if best_candidate["total_score"] >= (baseline_score + improvement_margin):
            winner = best_candidate

    if winner:
        decision = "APPLY_CANDIDATE"
        recommended_candidate = winner["candidate_id"]
        rationale = (
            f"Candidate '{winner['candidate_id']}' scored {winner['total_score']} "
            f"(outperforming baseline score {baseline_score} by {round(winner['total_score'] - baseline_score, 2)} pts). "
            f"Architecture: {winner.get('architecture')}. {winner.get('reasoning')}"
        )
        tfvars_path = winner.get("tfvars_path")
    else:
        decision = "KEEP_CURRENT"
        recommended_candidate = "current_baseline"
        rationale = (
            f"Current architecture (score: {baseline_score}) is optimal. "
            f"No candidate exceeded the {improvement_margin} pt improvement threshold without tradeoffs."
        )
        tfvars_path = None

    state["optimization_recommendation"] = {
        "decision": decision,
        "recommended_candidate": recommended_candidate,
        "rationale": rationale,
        "baseline_score": baseline_score,
        "winning_score": winner["total_score"] if winner else baseline_score,
        "tfvars_path": tfvars_path,
        "auto_redeploy": False,
        "note": "Optimization candidate emitted as tfvars override. Review and apply manually if desired."
    }

    return state
