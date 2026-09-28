import pytest
from backend.agents.deployment_validation_agent import deployment_validation_agent
from backend.agents.state import AgentState


def test_validation_dry_run_skipped():
    state = AgentState(
        deploy_mode="dry-run",
        deployment_status="SKIPPED",
    )
    result = deployment_validation_agent(state)
    assert result["deployment_validation_status"] == "SKIPPED"
    assert result["health_status"] == "INSUFFICIENT_DATA"
    assert result["service_url"] is None


def test_validation_empty_service_url_on_failure():
    def failing_http(url, timeout):
        return 500, {"status": "error"}

    state = AgentState(
        deploy_mode="real",
        deployment_status="PASSED",
        _pending_service_url="http://alb-failed.amazonaws.com",
        http_getter=failing_http,
    )
    result = deployment_validation_agent(state)
    assert result["deployment_validation_status"] == "FAILED"
    assert result["health_status"] == "UNHEALTHY"
    # Essential requirement: service_url must be empty whenever validation is not PASSED
    assert result["service_url"] is None
    assert len(result["validation_errors"]) > 0


def test_validation_degraded_on_db_issue():
    def degraded_http(url, timeout):
        return 200, {"status": "degraded", "database": "disconnected"}

    state = AgentState(
        deploy_mode="real",
        deployment_status="PASSED",
        _pending_service_url="http://alb-degraded.amazonaws.com",
        http_getter=degraded_http,
    )
    result = deployment_validation_agent(state)
    assert result["deployment_validation_status"] == "FAILED"
    assert result["health_status"] == "DEGRADED"
    assert result["service_url"] is None


def test_validation_success_exposes_service_url():
    def success_http(url, timeout):
        return 200, {"status": "healthy", "database": "connected"}

    state = AgentState(
        deploy_mode="real",
        deployment_status="PASSED",
        _pending_service_url="http://alb-success.amazonaws.com",
        http_getter=success_http,
    )
    result = deployment_validation_agent(state)
    assert result["deployment_validation_status"] == "PASSED"
    assert result["health_status"] == "HEALTHY"
    assert result["service_url"] == "http://alb-success.amazonaws.com"
    assert result["validation_errors"] == []
