import pytest
from backend.agents.architecture_analysis_agent import architecture_analysis_agent
from backend.agents.state import AgentState


def test_architecture_analysis_dry_run():
    state = AgentState(
        requirements="Build task tracking app",
        telemetry_status="SKIPPED",
        performance_analysis={"status": "INSUFFICIENT_DATA", "detected_problems": []},
        cost_analysis={"monthly_total_usd": 45.0},
        reliability_analysis={"status": "INSUFFICIENT_DATA", "detected_issues": []}
    )
    result = architecture_analysis_agent(state)
    analysis = result["architecture_analysis"]
    assert analysis["architecture_status"] in ("HEALTHY", "DEGRADED")
    assert "no runtime data" in analysis["note"]


def test_architecture_analysis_with_problems():
    state = AgentState(
        requirements="Build task tracking app",
        telemetry_status="PASSED",
        performance_analysis={
            "status": "DEGRADED",
            "detected_problems": [{"problem": "high_cpu", "evidence": "CPU > 80%"}],
            "recommendations": ["Scale tasks"]
        },
        cost_analysis={"monthly_total_usd": 95.0},
        reliability_analysis={"status": "HEALTHY", "detected_issues": []}
    )
    result = architecture_analysis_agent(state)
    analysis = result["architecture_analysis"]
    assert analysis["architecture_status"] == "DEGRADED"
    assert len(analysis["problems"]) >= 2
    assert "Scale tasks" in analysis["recommendations"]
