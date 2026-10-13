import pytest
from pathlib import Path
from backend.agents.candidate_generation_agent import candidate_generation_agent
from backend.agents.state import AgentState


def test_candidate_generation_exact_two_candidates(tmp_path):
    state = AgentState(
        assembled_project_path=str(tmp_path),
        architecture_analysis={"problems": []},
    )
    result = candidate_generation_agent(state)
    candidates = result["optimization_candidates"]

    # Rule: EXACTLY 2 candidates
    assert len(candidates) == 2
    assert candidates[0]["candidate_id"] == "candidate_a"
    assert candidates[1]["candidate_id"] == "candidate_b"

    # Schema verification
    for c in candidates:
        assert "architecture" in c
        assert "infrastructure_changes" in c
        assert "estimated_cost" in c
        assert c["estimated_cost"]["label"] == "projected"
        assert "expected_performance" in c
        assert c["expected_performance"]["label"] == "projected"
        assert "expected_reliability" in c
        assert c["expected_reliability"]["label"] == "projected"
        assert c["requirement_compliance"] == 100.0
        assert "reasoning" in c

    # Verify .tfvars files were created
    assert (tmp_path / "optimization" / "candidate_a.tfvars").exists()
    assert (tmp_path / "optimization" / "candidate_b.tfvars").exists()


def test_candidate_generation_performance_focus(tmp_path):
    state = AgentState(
        assembled_project_path=str(tmp_path),
        architecture_analysis={
            "problems": [{"dimension": "performance", "problem": "high_cpu_utilization"}]
        },
    )
    result = candidate_generation_agent(state)
    candidates = result["optimization_candidates"]
    assert len(candidates) == 2
    assert any("compute" in c["architecture"] or "multi_task" in c["architecture"] for c in candidates)
