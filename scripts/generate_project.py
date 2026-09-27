import os
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

from backend.agents.graph import build_agent_graph
from backend.core.execution_config import get_execution_config
from backend.core.pipeline_metrics import create_metrics


DEFAULT_PROMPT = """Build a full-stack task management web application.
Users can register and login, create/edit/delete tasks, search and filter tasks,
and view a dashboard with task statistics. Use React, FastAPI, PostgreSQL,
JWT authentication, REST APIs, Docker Compose and Terraform. Include tests,
README and .env.example. Generate the actual runnable source-code files,
not only architecture documentation."""


def main() -> None:
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit("GEMINI_API_KEY is not set. Add it to your .env file first.")

    print("AI Product Architect - Prompt to Code Deliverables")
    print("=" * 58)
    print("Paste your customer prompt. Finish with an empty line.")
    print("Press Enter twice to use the default example.\n")

    lines = []
    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)

    prompt = "\n".join(lines).strip() or DEFAULT_PROMPT
    project_name = input("Project name (optional): ").strip() or "Generated Product"

    project_id = str(uuid4())
    config = get_execution_config("FULL")
    state = {
        "project_id": project_id,
        "execution_mode": config.mode,
        "pipeline_metrics": create_metrics(),
        "project_name": project_name,
        "requirements": prompt,
        "users": None,
        "features": [],
        "security_level": "medium",
        "availability": "medium",
        "suggestions": [],
        "architecture": {},
    }

    print("\nRunning complete pipeline...\n")
    result = build_agent_graph().invoke(state)

    release = result.get("release_gate", {})
    export = result.get("project_export", {})
    manifest = result.get("file_manifest", {})

    print("\n" + "=" * 58)
    print("PIPELINE RESULT")
    print("=" * 58)
    print(f"Project ID : {project_id}")
    print(f"Files      : {manifest.get('file_count', 0)}")
    print(f"Code       : {result.get('generated_code_validation', {}).get('status', 'UNKNOWN')}")
    print(f"Build      : {result.get('project_build', {}).get('status', 'UNKNOWN')}")
    print(f"API        : {result.get('api_contract_validation', {}).get('status', 'UNKNOWN')}")
    print(f"Database   : {result.get('database_integration_validation', {}).get('status', 'UNKNOWN')}")
    print(f"Docker     : {result.get('docker_runtime_validation', {}).get('status', 'UNKNOWN')}")
    print(f"Release    : {release.get('status', 'UNKNOWN')}")

    project_path = result.get("generated_project_path", "")
    print(f"Project    : {project_path}")

    if release.get("status") == "APPROVED" and export.get("status") == "EXPORTED":
        print(f"ZIP        : {export.get('zip_path')}")
        print("\nDELIVERABLES:")
        root = Path(project_path)
        for file_path in sorted(p for p in root.rglob("*") if p.is_file()):
            print(f"  - {file_path.relative_to(root).as_posix()}")
        print("\nSUCCESS: Your prompt produced a code deliverable package.")
    else:
        print("\nDELIVERY BLOCKED")
        print(release.get("summary", "The release gate did not approve the generated project."))
        for failure in release.get("failures", []):
            print(f"  - {failure.get('stage')}: {failure.get('summary')}")


if __name__ == "__main__":
    main()
