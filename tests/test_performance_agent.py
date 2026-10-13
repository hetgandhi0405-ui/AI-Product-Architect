import pytest
from backend.agents.performance_agent import performance_agent
from backend.agents.state import AgentState


def test_performance_agent_insufficient_data():
    state = AgentState(
        telemetry_status="SKIPPED",
        telemetry_data={"status": "SKIPPED", "metrics": {}}
    )
    result = performance_agent(state)
    analysis = result["performance_analysis"]
    assert analysis["status"] == "INSUFFICIENT_DATA"
    assert "no runtime data" in analysis["note"]


def test_performance_agent_degraded_cpu():
    state = AgentState(
        telemetry_status="PASSED",
        telemetry_data={
            "status": "PASSED",
            "metrics": {
                "cpu_utilization": 84.5,
                "memory_utilization": 45.0,
                "latency_p95_ms": 250.0,
                "error_rate": 0.0,
            }
        }
    )
    result = performance_agent(state)
    analysis = result["performance_analysis"]
    assert analysis["status"] == "DEGRADED"
    assert any("cpu" in p["problem"] for p in analysis["detected_problems"])


def test_performance_agent_unhealthy_latency():
    state = AgentState(
        telemetry_status="PASSED",
        telemetry_data={
            "status": "PASSED",
            "metrics": {
                "cpu_utilization": 30.0,
                "memory_utilization": 40.0,
                "latency_p95_ms": 3200.0,
                "error_rate": 2.0,
            }
        }
    )
    result = performance_agent(state)
    analysis = result["performance_analysis"]
    assert analysis["status"] == "UNHEALTHY"
    assert any("latency" in p["problem"] for p in analysis["detected_problems"])
