import pytest
from backend.agents.candidate_generation_agent import candidate_generation_agent
from backend.agents.candidate_evaluation_agent import candidate_evaluation_agent
from backend.agents.optimization_recommendation_agent import optimization_recommendation_agent
from backend.agents.state import AgentState


def test_full_optimization_loop_flow(tmp_path):
    state = AgentState(
        assembled_project_path=str(tmp_path),
        architecture_analysis={
            "problems": [{"dimension": "performance", "problem": "high_cpu_utilization"}],
        },
        cost_analysis={"monthly_total_usd": 70.0},
    )

    s1 = candidate_generation_agent(state)
    assert len(s1["optimization_candidates"]) == 2

    s2 = candidate_evaluation_agent(s1)
    eval_res = s2["candidate_evaluation"]
    assert len(eval_res["evaluated_candidates"]) == 2

    s3 = optimization_recommendation_agent(s2)
    rec = s3["optimization_recommendation"]
    assert rec["decision"] in ("APPLY_CANDIDATE", "KEEP_CURRENT")
    assert rec["auto_redeploy"] is False
    assert rec["recommended_candidate"] is not None
