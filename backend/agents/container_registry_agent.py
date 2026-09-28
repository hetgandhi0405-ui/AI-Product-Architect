import os
import shutil
import subprocess
from typing import Any, Callable, Dict, Optional

from backend.agents.state import AgentState
from backend.utils.security_redaction import redact_secrets


def container_registry_agent(
    state: AgentState,
    ecr_client: Optional[Any] = None,
    runner: Optional[
        Callable[[list[str], str, int], tuple[int, str, str]]
    ] = None,
) -> AgentState:
    """
    Manage container registry (ECR) repository, authentication, tagging, and pushing.
    Vocabulary: PASSED | FAILED | SKIPPED | UNAVAILABLE
    """
    deploy_mode = state.get("deploy_mode", "dry-run")
    docker_status = state.get("docker_status", "SKIPPED")
    image_name = state.get("image_name", "ai-product-app")
    image_tag = state.get("image_tag", "latest")

    # If docker build did not pass, container registry stage must be SKIPPED
    if docker_status != "PASSED":
        state["registry_status"] = "SKIPPED"
        state["registry_error"] = (
            f"Docker build was {docker_status}; registry push skipped."
        )
        return state

    aws_region = os.getenv("AWS_REGION", "us-east-1")
    repo_name = os.getenv("ECR_REPOSITORY", image_name)
    aws_account_id = os.getenv("AWS_ACCOUNT_ID", "123456789012")

    registry_url = f"{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com"
    full_image_uri = f"{registry_url}/{repo_name}:{image_tag}"

    state["registry_url"] = registry_url
    state["image_uri"] = full_image_uri

    # Custom injected runner or mock client takes priority
    injected_client = (
        ecr_client or state.get("ecr_client") or state.get("boto3_ecr_client")
    )
    injected_runner = runner or state.get("registry_runner")

    if injected_client is not None or injected_runner is not None:
        try:
            if injected_client:
                # Mock or real boto3 ecr client
                try:
                    injected_client.describe_repositories(
                        repositoryNames=[repo_name]
                    )
                except Exception:
                    injected_client.create_repository(repositoryName=repo_name)
            if injected_runner:
                code, stdout, stderr = injected_runner(
                    ["docker", "push", full_image_uri], "", 300
                )
                if code != 0:
                    state["registry_status"] = "FAILED"
                    state["registry_error"] = redact_secrets(
                        stderr or stdout or "ECR push failed"
                    )
                    return state

            state["registry_status"] = "PASSED"
            state["registry_error"] = None
            return state
        except Exception as exc:
            state["registry_status"] = "FAILED"
            state["registry_error"] = redact_secrets(str(exc))
            return state

    # In dry-run mode, no real cloud registry push is performed
    if deploy_mode == "dry-run":
        state["registry_status"] = "SKIPPED"
        state["registry_error"] = None
        return state

    # Real deployment mode requires AWS credentials
    if not (
        os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE")
    ) and not os.getenv("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI"):
        state["registry_status"] = "FAILED"
        state["registry_error"] = (
            "AWS credentials not configured for real container registry push"
        )
        return state

    try:
        import boto3

        client = boto3.client("ecr", region_name=aws_region)
        # Verify or create repository
        try:
            client.describe_repositories(repositoryNames=[repo_name])
        except client.exceptions.RepositoryNotFoundException:
            client.create_repository(
                repositoryName=repo_name,
                tags=[
                    {"Key": "ManagedBy", "Value": "ai-product-architect"},
                    {"Key": "Project", "Value": image_name},
                ],
            )

        # Login and push via docker CLI if available
        docker_bin = shutil.which("docker")
        if not docker_bin:
            state["registry_status"] = "FAILED"
            state["registry_error"] = (
                "Docker binary not found on PATH for registry push"
            )
            return state

        # Tag image for remote ECR
        tag_cmd = [
            docker_bin,
            "tag",
            f"{image_name}:{image_tag}",
            full_image_uri,
        ]
        tag_res = subprocess.run(tag_cmd, capture_output=True, text=True)
        if tag_res.returncode != 0:
            state["registry_status"] = "FAILED"
            state["registry_error"] = redact_secrets(tag_res.stderr)
            return state

        # Push to ECR
        push_cmd = [docker_bin, "push", full_image_uri]
        push_res = subprocess.run(
            push_cmd, capture_output=True, text=True, timeout=600
        )
        if push_res.returncode != 0:
            state["registry_status"] = "FAILED"
            state["registry_error"] = redact_secrets(push_res.stderr)
            return state

        state["registry_status"] = "PASSED"
        state["registry_error"] = None
    except Exception as exc:
        state["registry_status"] = "FAILED"
        state["registry_error"] = redact_secrets(str(exc))

    return state
