import pytest
from backend.agents.reliability_agent import reliability_agent
from backend.agents.state import AgentState


def test_reliability_insufficient_data():
    state = AgentState(
        deploy_mode="dry-run",
        deployment_validation_status="SKIPPED",
    )
    result = reliability_agent(state)
    rel = result["reliability_analysis"]
    assert rel["status"] == "INSUFFICIENT_DATA"
    assert rel["availability"] is None


def test_reliability_healthy_calculation():
    state = AgentState(
        deploy_mode="real",
        deployment_validation_status="PASSED",
        health_status="HEALTHY",
        telemetry_data={
            "synthetic": {"window": "5m"},
            "metrics": {
                "total_requests": 100,
                "error_count": 0,
                "healthy_host_count": 1,
            }
        }
    )
    result = reliability_agent(state)
    rel = result["reliability_analysis"]
    assert rel["status"] == "HEALTHY"
    assert rel["availability"] == 100.0


def test_reliability_degraded_on_errors():
    state = AgentState(
        deploy_mode="real",
        deployment_validation_status="PASSED",
        health_status="HEALTHY",
        telemetry_data={
            "synthetic": {"window": "5m"},
            "metrics": {
                "total_requests": 100,
                "error_count": 2,
                "healthy_host_count": 1,
            }
        }
    )
    result = reliability_agent(state)
    rel = result["reliability_analysis"]
    assert rel["status"] == "DEGRADED"
    assert rel["availability"] == 98.0
