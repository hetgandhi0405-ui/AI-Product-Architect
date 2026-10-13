import pytest
from backend.agents.candidate_evaluation_agent import candidate_evaluation_agent
from backend.agents.state import AgentState


def test_candidate_evaluation_determinism():
    state = AgentState(
        cost_analysis={"monthly_total_usd": 60.0},
        optimization_candidates=[
            {
                "candidate_id": "candidate_a",
                "architecture": "cost_reduced",
                "infrastructure_changes": {"desired_count": 1, "db_instance_class": "db.t4g.micro"},
                "estimated_cost": {"monthly_usd": 45.0},
                "expected_performance": {"score": 82.0},
                "expected_reliability": {"score": 85.0},
                "requirement_compliance": 100.0,
                "reasoning": "Standard downsize",
            },
            {
                "candidate_id": "candidate_b",
                "architecture": "high_resilience",
                "infrastructure_changes": {"desired_count": 2, "db_instance_class": "db.t4g.micro"},
                "estimated_cost": {"monthly_usd": 65.0},
                "expected_performance": {"score": 90.0},
                "expected_reliability": {"score": 95.0},
                "requirement_compliance": 100.0,
                "reasoning": "Redundant tasks",
            },
        ],
    )

    # Determinism: Run twice, assert exact equality
    res1 = candidate_evaluation_agent(state.copy())
    res2 = candidate_evaluation_agent(state.copy())

    eval1 = res1["candidate_evaluation"]
    eval2 = res2["candidate_evaluation"]

    assert eval1 == eval2
    assert "formula" in eval1
    assert "weights" in eval1
    assert len(eval1["evaluated_candidates"]) == 2


def test_candidate_evaluation_hard_compliance_gate():
    state = AgentState(
        cost_analysis={"monthly_total_usd": 60.0},
        optimization_candidates=[
            {
                "candidate_id": "candidate_invalid",
                "architecture": "non_compliant_app",
                "infrastructure_changes": {"desired_count": 1, "db_instance_class": "db.t4g.micro"},
                "estimated_cost": {"monthly_usd": 20.0},
                "expected_performance": {"score": 100.0},
                "expected_reliability": {"score": 100.0},
                "requirement_compliance": 85.0,  # Below 100% hard gate
                "reasoning": "Missing auth requirement",
            }
        ],
    )
    result = candidate_evaluation_agent(state)
    evaluated = result["candidate_evaluation"]["evaluated_candidates"]
    assert len(evaluated) == 1
    assert evaluated[0]["disqualified"] is True
    assert "100%" in evaluated[0]["disqualification_reason"]
