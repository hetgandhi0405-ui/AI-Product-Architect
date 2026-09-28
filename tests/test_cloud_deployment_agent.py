import pytest
from pathlib import Path
from backend.agents.cloud_deployment_agent import cloud_deployment_agent
from backend.agents.state import AgentState


def test_cloud_deployment_dry_run_success(tmp_path):
    infra_dir = tmp_path / "infrastructure"
    infra_dir.mkdir()
    (infra_dir / "main.tf").write_text("resource \"aws_vpc\" \"main\" {}", encoding="utf-8")

    state = AgentState(
        assembled_project_path=str(tmp_path),
        deploy_mode="dry-run",
        docker_status="PASSED",
        registry_status="SKIPPED",
    )

    result = cloud_deployment_agent(state)
    assert result["terraform_status"] == "PASSED"
    assert result["deployment_status"] == "SKIPPED"
    assert result["service_url"] is None


def test_cloud_deployment_pre_stage_failure():
    state = AgentState(
        docker_status="FAILED",
        registry_status="SKIPPED",
        deploy_mode="dry-run"
    )
    result = cloud_deployment_agent(state)
    assert result["terraform_status"] == "SKIPPED"
    assert result["deployment_status"] == "SKIPPED"


def test_cloud_deployment_requires_approval(tmp_path):
    infra_dir = tmp_path / "infrastructure"
    infra_dir.mkdir()
    (infra_dir / "main.tf").write_text("resource \"aws_vpc\" \"main\" {}", encoding="utf-8")

    def mock_runner(cmd, cwd, timeout):
        return 0, "Plan: 5 to add, 0 to change, 0 to destroy.", ""

    state = AgentState(
        assembled_project_path=str(tmp_path),
        deploy_mode="real",
        docker_status="PASSED",
        registry_status="PASSED",
        approved=False,
        terraform_runner=mock_runner
    )

    result = cloud_deployment_agent(state)
    assert result["terraform_status"] == "PASSED"
    assert result["deployment_status"] == "FAILED"
    assert "requires explicit approval" in result["deployment_error"]


def test_cloud_deployment_real_success_with_approval(tmp_path):
    infra_dir = tmp_path / "infrastructure"
    infra_dir.mkdir()
    (infra_dir / "main.tf").write_text("resource \"aws_vpc\" \"main\" {}", encoding="utf-8")

    def mock_runner(cmd, cwd, timeout):
        if "apply" in cmd:
            return 0, 'Apply complete! Resources: 10 added.\nalb_dns_name = "test-alb-12345.us-east-1.elb.amazonaws.com"', ""
        return 0, "success", ""

    state = AgentState(
        assembled_project_path=str(tmp_path),
        deploy_mode="real",
        docker_status="PASSED",
        registry_status="PASSED",
        approved=True,
        terraform_runner=mock_runner
    )

    result = cloud_deployment_agent(state)
    assert result["terraform_status"] == "PASSED"
    assert result["deployment_status"] == "PASSED"
    assert result["_pending_service_url"] == "http://test-alb-12345.us-east-1.elb.amazonaws.com"
    # Service url must remain empty until deployment_validation passes
    assert result["service_url"] is None
