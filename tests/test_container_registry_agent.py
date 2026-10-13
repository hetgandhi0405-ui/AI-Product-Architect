import pytest
from unittest.mock import MagicMock
from backend.agents.container_registry_agent import container_registry_agent
from backend.agents.state import AgentState


def test_container_registry_skipped_if_docker_failed():
    state = AgentState(
        docker_status="FAILED",
        deploy_mode="real"
    )
    result = container_registry_agent(state)
    assert result["registry_status"] == "SKIPPED"
    assert "Docker build was FAILED" in result["registry_error"]


def test_container_registry_dry_run_skipped():
    state = AgentState(
        docker_status="PASSED",
        deploy_mode="dry-run",
        image_name="test-app",
        image_tag="v1"
    )
    result = container_registry_agent(state)
    assert result["registry_status"] == "SKIPPED"
    assert result["image_uri"] is not None
    assert "test-app:v1" in result["image_uri"]


def test_container_registry_mock_client_success():
    mock_ecr = MagicMock()
    mock_ecr.describe_repositories.return_value = {"repositories": [{"repositoryName": "test-app"}]}

    def mock_runner(cmd, cwd, timeout):
        return 0, "Pushed image successfully", ""

    state = AgentState(
        docker_status="PASSED",
        deploy_mode="real",
        image_name="test-app",
        image_tag="latest",
        ecr_client=mock_ecr,
        registry_runner=mock_runner
    )

    result = container_registry_agent(state)
    assert result["registry_status"] == "PASSED"
    assert result["registry_error"] is None
    assert "test-app:latest" in result["image_uri"]


def test_container_registry_mock_runner_failure():
    mock_ecr = MagicMock()
    def failing_runner(cmd, cwd, timeout):
        return 1, "", "Push failed: token=secret-jwt-token-123 expired"

    state = AgentState(
        docker_status="PASSED",
        deploy_mode="real",
        image_name="test-app",
        ecr_client=mock_ecr,
        registry_runner=failing_runner
    )

    result = container_registry_agent(state)
    assert result["registry_status"] == "FAILED"
    assert "secret-jwt-token-123" not in result["registry_error"]
    assert "[REDACTED]" in result["registry_error"]
