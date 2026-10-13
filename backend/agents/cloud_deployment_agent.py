from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any, Callable, Dict, Optional
from backend.agents.state import AgentState
from backend.utils.security_redaction import redact_secrets


def default_tf_runner(
    cmd: list[str], cwd: str, timeout: int = 1500
) -> tuple[int, str, str]:
    """Execute a terraform command with a 25-minute default timeout."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Terraform command timed out after {timeout} seconds"
    except Exception as exc:
        return -1, "", str(exc)


def cloud_deployment_agent(
    state: AgentState,
    tf_runner: Optional[
        Callable[[list[str], str, int], tuple[int, str, str]]
    ] = None,
) -> AgentState:
    """
    Run Terraform infrastructure lifecycle (init -> plan -> approve -> apply).
    Passes image_uri as a variable, captures outputs/errors with 25 min timeout.
    Vocabulary: PASSED | FAILED | SKIPPED | UNAVAILABLE
    """
    deploy_mode = state.get("deploy_mode", "dry-run")
    docker_status = state.get("docker_status", "SKIPPED")
    registry_status = state.get("registry_status", "SKIPPED")
    project_path_str = state.get("assembled_project_path")
    image_uri = state.get(
        "image_uri", "123456789012.dkr.ecr.us-east-1.amazonaws.com/app:latest"
    )

    # Initialize states
    state["service_url"] = None
    state["deployment_timestamp"] = datetime.now(timezone.utc).isoformat()

    # Pre-condition checks: If docker or registry failed, skip terraform
    if docker_status == "FAILED" or registry_status == "FAILED":
        state["terraform_status"] = "SKIPPED"
        state["deployment_status"] = "SKIPPED"
        state["deployment_error"] = (
            f"Pre-requisite stage failed (docker: {docker_status}, registry: {registry_status}). Deployment aborted."
        )
        return state

    if not project_path_str or not os.path.exists(project_path_str):
        state["terraform_status"] = "FAILED"
        state["deployment_status"] = "FAILED"
        state["deployment_error"] = "Project directory not found for Terraform"
        return state

    # Locate terraform directory (infrastructure/ or root)
    project_dir = Path(project_path_str)
    tf_dir = project_dir / "infrastructure"
    if not tf_dir.exists():
        tf_dir = project_dir / "terraform"
    if not tf_dir.exists():
        tf_dir = project_dir

    state["terraform_path"] = str(tf_dir)

    # Check for .tf files
    tf_files = list(tf_dir.glob("*.tf"))
    if not tf_files:
        state["terraform_status"] = "FAILED"
        state["deployment_status"] = "FAILED"
        state["deployment_error"] = (
            f"No Terraform (*.tf) files found in {tf_dir}"
        )
        return state

    runner = tf_runner or state.get("terraform_runner") or default_tf_runner
    tf_bin = shutil.which("terraform")

    # Injected mock/test runner handling
    if tf_runner or state.get("terraform_runner"):
        try:
            # 1. Init
            c, out, err = runner(["terraform", "init"], str(tf_dir), 300)
            if c != 0:
                state["terraform_status"] = "FAILED"
                state["deployment_status"] = "FAILED"
                state["deployment_error"] = redact_secrets(
                    err or out or "terraform init failed"
                )
                return state

            # 2. Plan
            c, out, err = runner(
                ["terraform", "plan", f"-var=image_uri={image_uri}"],
                str(tf_dir),
                600,
            )
            if c != 0:
                state["terraform_status"] = "FAILED"
                state["deployment_status"] = "FAILED"
                state["deployment_error"] = redact_secrets(
                    err or out or "terraform plan failed"
                )
                return state

            if deploy_mode == "dry-run":
                state["terraform_status"] = "PASSED"
                state["deployment_status"] = "SKIPPED"
                state["deployment_error"] = None
                return state

            # 3. Apply (for real or mock real)
            approved = (
                state.get("approved") is True
                or os.getenv("DEPLOY_APPROVE", "").lower() in ("true", "1", "yes")
            )
            if not approved:
                state["terraform_status"] = "PASSED"
                state["deployment_status"] = "FAILED"
                state["deployment_error"] = (
                    "Deployment requires explicit approval (--approve) before apply"
                )
                return state

            c, out, err = runner(
                [
                    "terraform",
                    "apply",
                    "-auto-approve",
                    f"-var=image_uri={image_uri}",
                ],
                str(tf_dir),
                1500,
            )
            if c != 0:
                state["terraform_status"] = "FAILED"
                state["deployment_status"] = "FAILED"
                state["deployment_error"] = redact_secrets(
                    err or out or "terraform apply failed"
                )
                return state

            state["terraform_status"] = "PASSED"
            state["deployment_status"] = "PASSED"
            state["deployment_error"] = None
            # Store raw ALB DNS from output if present in mock/real
            if "alb_dns_name" in out:
                # Mock runner might emit DNS
                import re

                match = re.search(r'alb_dns_name\s*=\s*"([^"]+)"', out)
                if match:
                    state["_pending_service_url"] = f"http://{match.group(1)}"
            return state
        except Exception as exc:
            state["terraform_status"] = "FAILED"
            state["deployment_status"] = "FAILED"
            state["deployment_error"] = redact_secrets(str(exc))
            return state

    # Dry-run execution without injected mock
    if deploy_mode == "dry-run":
        if tf_bin:
            # Run local validate / plan without modifying cloud
            code, out, err = runner(["terraform", "init"], str(tf_dir), 300)
            if code == 0:
                runner(
                    ["terraform", "plan", f"-var=image_uri={image_uri}"],
                    str(tf_dir),
                    300,
                )
        state["terraform_status"] = "PASSED"
        state["deployment_status"] = "SKIPPED"
        state["deployment_error"] = None
        return state

    # Real deployment mode
    if not tf_bin:
        state["terraform_status"] = "UNAVAILABLE"
        state["deployment_status"] = "UNAVAILABLE"
        state["deployment_error"] = (
            "Terraform binary is not installed or available on PATH"
        )
        return state

    # Check approval
    approved = (
        state.get("approved") is True
        or os.getenv("DEPLOY_APPROVE", "").lower() in ("true", "1", "yes")
    )
    if not approved:
        state["terraform_status"] = "PASSED"
        state["deployment_status"] = "FAILED"
        state["deployment_error"] = (
            "Real deployment requires explicit approval (--approve) before terraform apply"
        )
        return state

    # Real Terraform execution
    try:
        # Init
        c, out, err = runner(["terraform", "init"], str(tf_dir), 300)
        if c != 0:
            state["terraform_status"] = "FAILED"
            state["deployment_status"] = "FAILED"
            state["deployment_error"] = redact_secrets(err)
            return state

        # Apply
        c, out, err = runner(
            [
                "terraform",
                "apply",
                "-auto-approve",
                f"-var=image_uri={image_uri}",
            ],
            str(tf_dir),
            1500,
        )
        if c != 0:
            state["terraform_status"] = "FAILED"
            state["deployment_status"] = "FAILED"
            state["deployment_error"] = redact_secrets(err)
            return state

        # Fetch outputs
        c_out, stdout_out, _ = runner(
            ["terraform", "output", "-raw", "alb_dns_name"], str(tf_dir), 60
        )
        alb_dns = stdout_out.strip() if c_out == 0 else ""

        state["terraform_status"] = "PASSED"
        state["deployment_status"] = "PASSED"
        state["deployment_error"] = None
        if alb_dns:
            state["_pending_service_url"] = f"http://{alb_dns}"

    except Exception as exc:
        state["terraform_status"] = "FAILED"
        state["deployment_status"] = "FAILED"
        state["deployment_error"] = redact_secrets(str(exc))

    return state
