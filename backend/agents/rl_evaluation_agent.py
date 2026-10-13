"""
Phase 12 — RL-Based Evaluation Agent
======================================
Evaluates proposed architecture candidates using a formal Reinforcement Learning
reward formulation.

Reward Function:
  Reward = (w_perf * PerfGain) + (w_rel * RelGain) - (w_cost * CostDelta) - RiskPenalty

State Representation:
  - Current Infrastructure State (resources, monthly cost, P95 latency, SLA)
  - Current Telemetry (CPU, error rate, request volume)

Action Representation:
  - Optimization recommendation (e.g. scale instances, add Redis cache, adjust multi-AZ)

Returns:
  - rl_state: dict
  - rl_action: dict
  - rl_evaluation: {reward, breakdown, is_policy_safe, recommendation_accepted}
"""
from __future__ import annotations

from typing import Dict, Any
from backend.agents.state import AgentState


def rl_evaluation_agent(state: AgentState) -> AgentState:
    """
    Apply RL reward scoring to candidate architectural recommendations.
    """
    infra_state = state.get("infrastructure_state", {})
    recommendation = state.get("optimization_recommendation", {})
    candidates = state.get("optimization_candidates", [])
    telemetry = state.get("telemetry_data", {})
    perf_analysis = state.get("performance_analysis", {})
    cost_analysis = state.get("cost_analysis", {})
    rel_analysis = state.get("reliability_analysis", {})

    # Extract current metrics
    expected_metrics = infra_state.get("expected_metrics", {})
    curr_cost = expected_metrics.get("monthly_cost_usd", 100.0)
    curr_latency = expected_metrics.get("latency_p95_ms", 250.0)
    curr_sla = 99.9

    # RL State Vector
    rl_state = {
        "architecture_id": infra_state.get("architecture_id", "ARCH-000"),
        "resource_count": len(infra_state.get("resources", [])),
        "monthly_cost": curr_cost,
        "latency_p95_ms": curr_latency,
        "availability_sla": curr_sla,
        "cpu_utilization": telemetry.get("metrics", {}).get("cpu_utilization", 30.0),
        "error_rate": telemetry.get("metrics", {}).get("error_rate", 0.0),
    }

    if not recommendation or not candidates:
        state["rl_state"] = rl_state
        state["rl_action"] = {"action": "NO_CHANGE", "reason": "No optimization recommendation"}
        state["rl_evaluation"] = {
            "reward": 0.0,
            "reward_breakdown": {"perf_gain": 0, "rel_gain": 0, "cost_delta": 0, "risk_penalty": 0},
            "is_policy_safe": True,
            "recommendation_accepted": False,
            "summary": "RL evaluation: NO_CHANGE policy evaluated with 0.0 reward."
        }
        state["rl_policy_validated"] = True
        return state

    top_candidate = candidates[0] if candidates else {}

    # Extract action
    rl_action = {
        "action": recommendation.get("recommended_action", "OPTIMIZE"),
        "candidate_id": top_candidate.get("candidate_id", "CAND-001"),
        "description": recommendation.get("summary", ""),
        "changes": top_candidate.get("changes", []),
    }

    # Project metric gains from candidate
    est_cost = top_candidate.get("estimated_cost_usd", curr_cost)
    est_latency = top_candidate.get("estimated_latency_p95_ms", curr_latency)
    est_sla = top_candidate.get("estimated_sla", curr_sla)

    cost_delta = (est_cost - curr_cost) / max(curr_cost, 1.0)  # relative cost increase
    perf_gain = (curr_latency - est_latency) / max(curr_latency, 1.0)  # relative latency reduction
    rel_gain = max(0.0, est_sla - curr_sla) / 100.0  # SLA improvement

    # Risk Penalty
    risk_score = top_candidate.get("risk_score", 0.2)
    risk_penalty = risk_score * 0.5

    # Weights
    w_perf = 0.4
    w_rel = 0.4
    w_cost = 0.3

    reward = (w_perf * perf_gain) + (w_rel * rel_gain) - (w_cost * cost_delta) - risk_penalty
    reward = round(reward, 4)

    is_policy_safe = risk_score < 0.7
    recommendation_accepted = reward > 0.05 and is_policy_safe

    rl_evaluation = {
        "reward": reward,
        "reward_breakdown": {
            "perf_gain": round(perf_gain, 4),
            "rel_gain": round(rel_gain, 4),
            "cost_delta": round(cost_delta, 4),
            "risk_penalty": round(risk_penalty, 4),
        },
        "is_policy_safe": is_policy_safe,
        "recommendation_accepted": recommendation_accepted,
        "projected_cost": est_cost,
        "projected_latency_ms": est_latency,
        "summary": (
            f"RL evaluation score: {reward} (Safe: {is_policy_safe}, Accepted: {recommendation_accepted}). "
            f"Perf gain: {perf_gain:.2%}, Cost delta: {cost_delta:.2%}."
        ),
    }

    state["rl_state"] = rl_state
    state["rl_action"] = rl_action
    state["rl_evaluation"] = rl_evaluation
    state["rl_policy_validated"] = is_policy_safe

    arch = state.get("architecture", {})
    arch["rl_evaluation"] = rl_evaluation
    state["architecture"] = arch

    return state
