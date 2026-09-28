#!/usr/bin/env python3
"""
scripts/generate_project.py

Command-line interface for the AI Product Architect module.
Demonstrates the full pipeline:
Customer Prompt -> Requirements -> Product Plan -> Specs -> Architecture ->
Contract -> Manifest -> Code Generation -> Assembly -> Validation ->
Self-Correction -> Release Gate -> ZIP Export.
"""

import os
import sys
import uuid
import argparse
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

# Load .env
load_dotenv(REPO_ROOT / ".env")

from backend.agents.graph import build_agent_graph


def main():
    parser = argparse.ArgumentParser(description="AI Product Architect Project Generator CLI")
    parser.add_argument("positional_prompt", nargs="?", default=None, help="Product description prompt")
    parser.add_argument("--prompt", "-p", default=None, help="Product description prompt")
    parser.add_argument("--name", "-n", default=None, help="Optional project name")
    parser.add_argument("--auto", "-y", action="store_true", help="Non-interactive automatic mode")

    args = parser.parse_args()

    default_prompt = (
        "Create a task management application where users can register, login, "
        "create tasks, update tasks, delete tasks and mark tasks as completed."
    )

    print("=" * 70)
    print("      AI PRODUCT ARCHITECT - FULL DELIVERY PIPELINE")
    print("=" * 70)

    # 1 & 2. Verify Gemini Key
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        print("[INFO] GEMINI_API_KEY detected. Real AI generation mode active.")
    else:
        print("[WARN] GEMINI_API_KEY not found in environment or .env.")
        print("       Running in deterministic high-fidelity synthesizer mode.")

    # 3. Determine prompt
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

    # 4. Determine project name
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
    print(f"Description:  {prompt}")
    print("=" * 70)
    print("\n[PIPELINE] Starting LangGraph agent execution...\n")

    initial_state = {
        "project_id": project_id,
        "project_name": project_name,
        "requirements": prompt,
        "suggestions": [],
        "architecture": {},
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
    print("                  PIPELINE EXECUTION RESULTS")
    print("=" * 70)

    # File Manifest
    manifest = result.get("file_manifest", {})
    files = manifest.get("files", [])
    print(f"[1] Manifest Generation:    {len(files)} files planned")

    # Code Generation
    gen_files = result.get("generated_files", {})
    print(f"[2] Code Generation:        {len(gen_files)} files synthesized")

    # Assembly
    project_path = result.get("assembled_project_path", "")
    print(f"[3] File Assembly:          {project_path}")

    # Validations
    code_val = result.get("code_validation", {})
    build_val = result.get("build_validation", {})
    api_val = result.get("api_validation", {})
    db_val = result.get("database_validation", {})
    docker_val = result.get("docker_validation", {})

    print(f"[4] Code Validation:        {code_val.get('status', 'N/A')} - {code_val.get('summary', '')}")
    print(f"[5] Build Validation:       {build_val.get('status', 'N/A')} - {build_val.get('summary', '')}")
    print(f"[6] API Validation:         {api_val.get('status', 'N/A')} - {api_val.get('summary', '')}")
    print(f"[7] Database Validation:    {db_val.get('status', 'N/A')} - {db_val.get('summary', '')}")
    print(f"[8] Docker Validation:      {docker_val.get('status', 'N/A')} - {docker_val.get('summary', '')}")

    # Release Gate
    gate = result.get("release_gate", {})
    gate_status = gate.get("status", "BLOCKED")
    print(f"[9] Release Gate:           {gate_status}")

    if gate_status != "APPROVED":
        print("\n[BLOCKED] Release gate failed with the following issues:")
        for issue in gate.get("blocking_issues", []):
            print(f"  * {issue}")
    else:
        export_info = result.get("export", {})
        zip_path = export_info.get("zip_path")
        print("\n[SUCCESS] RELEASE APPROVED!")
        print(f"Generated Project Location: {project_path}")
        print(f"Generated ZIP Location:     {zip_path}")
        print(f"Total Files Packaged:       {export_info.get('file_count', 0)}")

    print("=" * 70)


if __name__ == "__main__":
    main()
