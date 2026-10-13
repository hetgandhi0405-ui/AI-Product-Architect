import os
import pytest
from pathlib import Path
from backend.agents.docker_build_agent import docker_build_agent
from backend.agents.state import AgentState


def test_docker_build_agent_dry_run_success(tmp_path):
    # Setup dummy project with Dockerfile
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM python:3.11-slim\nWORKDIR /app\n", encoding="utf-8")

    state = AgentState(
        project_id="test-proj-1",
        assembled_project_path=str(tmp_path),
        deploy_mode="dry-run",
    )

    result = docker_build_agent(state)
    assert result["docker_status"] == "PASSED"
    assert result["image_name"] == "ai-product-test-proj-1"
    assert result["image_tag"] == "latest"
    assert result["docker_error"] is None


def test_docker_build_agent_missing_dockerfile(tmp_path):
    state = AgentState(
        project_id="test-proj-2",
        assembled_project_path=str(tmp_path),
        deploy_mode="dry-run",
    )

    result = docker_build_agent(state)
    assert result["docker_status"] == "FAILED"
    assert "Dockerfile not found" in result["docker_error"]


def test_docker_build_agent_injected_runner_failure(tmp_path):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM python:3.11-slim\n", encoding="utf-8")

    def failing_runner(cmd, cwd, timeout):
        return 1, "", "Error: secret_password=SuperSecret123 failed to build"

    state = AgentState(
        project_id="test-proj-3",
        assembled_project_path=str(tmp_path),
        deploy_mode="real",
        docker_runner=failing_runner,
    )

    result = docker_build_agent(state)
    assert result["docker_status"] == "FAILED"
    assert "SuperSecret123" not in result["docker_error"]
    assert "[REDACTED]" in result["docker_error"]


def test_docker_build_agent_skipped_on_blocked_gate(tmp_path):
    state = AgentState(
        project_id="test-proj-4",
        assembled_project_path=str(tmp_path),
        deploy_mode="dry-run",
        release_gate={"decision": "BLOCKED", "summary": "Code failed tests"},
    )

    result = docker_build_agent(state)
    assert result["docker_status"] == "SKIPPED"
