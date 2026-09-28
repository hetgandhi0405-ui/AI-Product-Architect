#!/usr/bin/env python3
"""
scripts/generate_project.py

Command-line interface for the AI Product Architect module:
Customer Prompt -> Specifications -> Architecture -> Code Generation -> Assembly ->
Validation -> Release Gate -> Deployment -> Monitoring -> Optimization -> ZIP Export.
"""

import argparse
import os
import subprocess
import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

# Load .env
load_dotenv(REPO_ROOT / ".env")

from backend.agents.graph import build_agent_graph
from backend.utils.security_redaction import redact_secrets


def run_destroy(project_dir: Path):
    """Run terraform destroy for teardown."""
    tf_dir = project_dir / "infrastructure"
    if not tf_dir.exists():
        tf_dir = project_dir / "terraform"
    if not tf_dir.exists():
        tf_dir = project_dir

    print(f"\n[TEARDOWN] Running terraform destroy in {tf_dir}...")
    try:
        proc = subprocess.run(
            ["terraform", "destroy", "-auto-approve"],
            cwd=str(tf_dir),
            capture_output=True,
            text=True,
            timeout=1200,
        )
        if proc.returncode == 0:
            print("[TEARDOWN SUCCESS] Cloud resources destroyed cleanly.")
        else:
            print(f"[TEARDOWN FAILED] {redact_secrets(proc.stderr)}")
    except Exception as e:
        print(f"[TEARDOWN ERROR] {redact_secrets(str(e))}")


def main():
    parser = argparse.ArgumentParser(description="AI Product Architect Full Pipeline CLI")
    parser.add_argument("positional_prompt", nargs="?", default=None, help="Product description prompt")
    parser.add_argument("--prompt", "-p", default=None, help="Product description prompt")
    parser.add_argument("--name", "-n", default=None, help="Optional project name")
    parser.add_argument("--auto", "-y", action="store_true", help="Non-interactive automatic mode")
    parser.add_argument(
        "--deploy-mode",
        choices=["dry-run", "real"],
        default="dry-run",
        help="Deployment mode: 'dry-run' (default) or 'real' (requires AWS credentials and approval)",
    )
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Explicit approval for real terraform apply",
    )
    parser.add_argument(
        "--destroy",
        action="store_true",
        help="Run terraform destroy to teardown project infrastructure",
    )
    parser.add_argument(
        "--project-path",
        default=None,
        help="Existing project path for --destroy teardown",
    )

    args = parser.parse_args()

    # Handle teardown request
    if args.destroy:
        if not args.project_path:
            print("[ERROR] Please provide --project-path <path> when using --destroy")
            sys.exit(1)
        run_destroy(Path(args.project_path))
        return

    default_prompt = (
        "Create a task management application where users can register, login, "
        "create tasks, update tasks, delete tasks and mark tasks as completed."
    )

    print("=" * 70)
    print("      AI PRODUCT ARCHITECT - 3-DAY MVP DELIVERY & DEPLOYMENT")
    print("=" * 70)

    # 1. Credentials check
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        print("[INFO] GEMINI_API_KEY detected. Real AI generation mode active.")
    else:
        print("[INFO] GEMINI_API_KEY omitted. Using deterministic synthesizer.")

    print(f"[DEPLOY MODE] {args.deploy_mode.upper()}")
    if args.deploy_mode == "real":
        aws_key = os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("AWS_PROFILE")
        if not aws_key:
            print("[ERROR] Real deploy mode selected but no AWS credentials found.")
            sys.exit(1)
        if not args.approve:
            confirm = input("Proceed with real AWS cloud deployment? (yes/no): ").strip().lower()
            if confirm not in ("yes", "y"):
                print("Deployment aborted: approval denied.")
                sys.exit(0)
            args.approve = True

    # 2. Determine prompt
    prompt = args.prompt or args.positional_prompt
    if not prompt:
        if args.auto or not sys.stdin.isatty():
            prompt = default_prompt
        else:
            print(f"\nDefault prompt:\n\"{default_prompt}\"")
            try:
                user_input = input("\nEnter product description (Press Enter for default):\n> ").strip()
                prompt = user_input if user_input else default_prompt
            except (EOFError, KeyboardInterrupt):
                prompt = default_prompt

    # 3. Determine project name
    project_name = args.name
    if not project_name:
        if args.auto or not sys.stdin.isatty() or args.positional_prompt:
            project_name = "Task Management App"
        else:
            try:
                name_input = input("\nEnter project name (optional, press Enter to derive):\n> ").strip()
                project_name = name_input if name_input else "Task Management App"
            except (EOFError, KeyboardInterrupt):
                project_name = "Task Management App"

    project_id = f"cli-{uuid.uuid4().hex[:8]}"

    print("\n" + "=" * 70)
    print(f"Project ID:   {project_id}")
    print(f"Project Name: {project_name}")
    print(f"Deploy Mode:  {args.deploy_mode}")
    print("=" * 70)
    print("\n[PIPELINE] Executing agent graph...\n")

    initial_state = {
        "project_id": project_id,
        "project_name": project_name,
        "requirements": prompt,
        "suggestions": [],
        "architecture": {},
        "deploy_mode": args.deploy_mode,
        "approved": args.approve,
        "correction_attempts": 0,
        "max_correction_attempts": 3,
        "code_correction_attempts": 0,
        "max_code_correction_attempts": 3,
        "integration_correction_attempts": 0,
        "max_integration_correction_attempts": 2,
    }

    agent_graph = build_agent_graph()
    result = agent_graph.invoke(initial_state)

    print("\n" + "=" * 70)
    print("                  STAGE EXECUTION SUMMARY")
    print("=" * 70)

    # Stage Status Vocabulary: PASSED | FAILED | SKIPPED | UNAVAILABLE
    # Health Vocabulary: HEALTHY | DEGRADED | UNHEALTHY | INSUFFICIENT_DATA

    code_val = result.get("code_validation", {}).get("status", "SKIPPED")
    build_val = result.get("build_validation", {}).get("status", "SKIPPED")
    api_val = result.get("api_validation", {}).get("status", "SKIPPED")
    db_val = result.get("database_validation", {}).get("status", "SKIPPED")
    docker_val = result.get("docker_validation", {}).get("status", "SKIPPED")
    gate_val = result.get("release_gate", {}).get("status", "BLOCKED")

    docker_build = result.get("docker_status", "SKIPPED")
    registry = result.get("registry_status", "SKIPPED")
    terraform = result.get("terraform_status", "SKIPPED")
    deployment = result.get("deployment_status", "SKIPPED")
    deploy_val = result.get("deployment_validation_status", "SKIPPED")
    health = result.get("health_status", "INSUFFICIENT_DATA")

    print(f"Code Validation:        {code_val}")
    print(f"Build Validation:       {build_val}")
    print(f"API Contract:           {api_val}")
    print(f"Database Integration:   {db_val}")
    print(f"Docker Runtime:         {docker_val}")
    print(f"Release Gate:           {gate_val}")
    print(f"Docker Build:           {docker_build}")
    print(f"Container Registry:     {registry}")
    print(f"Terraform Status:       {terraform}")

    # Deployment Line Format according to Section 11:
    if args.deploy_mode == "dry-run":
        print("Deployment:             SKIPPED (dry-run)")
    elif deployment == "FAILED":
        reason = redact_secrets(result.get("deployment_error") or "Deployment failed")
        print(f"Deployment:             FAILED / Reason: {reason} / Live Application: NOT AVAILABLE")
    else:
        print(f"Deployment:             {deployment}")

    print(f"Deployment Validation:  {deploy_val} (Health: {health})")

    # Service URL exposed ONLY if deployment validation PASSED
    service_url = result.get("service_url")
    if deploy_val == "PASSED" and service_url:
        print(f"Service URL:            {service_url}")
    else:
        print("Service URL:            NOT AVAILABLE")

    print("-" * 70)
    # Day 2 & 3 Metrics & Optimization
    cost_info = result.get("cost_analysis", {})
    cost_est = cost_info.get("monthly_total_usd", 0.0)
    print(f"Estimated Monthly Cost: ${cost_est:.2f} (ESTIMATE)")

    telemetry = result.get("telemetry_data", {})
    telemetry_source = telemetry.get("source") or telemetry.get("synthetic", {}).get("source", "none")
    print(f"Telemetry Source:       {telemetry_source}")

    candidates = result.get("optimization_candidates", [])
    print(f"Candidate Count:        {len(candidates)}")

    rec = result.get("optimization_recommendation", {})
    print(f"Optimization Rec:       {rec.get('decision')} ({rec.get('recommended_candidate')})")

    export_info = result.get("export", {})
    zip_path = export_info.get("zip_path", "NOT CREATED")
    print(f"ZIP Export Path:        {zip_path}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
