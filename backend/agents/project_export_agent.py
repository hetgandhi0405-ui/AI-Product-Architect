import os
import zipfile
from pathlib import Path
from backend.agents.state import AgentState


def project_export_agent(state: AgentState) -> AgentState:
    """
    Package the assembled project into a downloadable ZIP archive
    upon release gate approval (or record blocked status if release failed).
    """
    project_id = state.get("project_id", "project-export")
    project_path_str = state.get("assembled_project_path")
    release_gate = state.get("release_gate", {})

    # If release gate is blocked, do not create release package
    if release_gate.get("status") != "APPROVED" or not release_gate.get("approved"):
        state["export"] = {
            "status": "BLOCKED",
            "zip_path": None,
            "file_count": 0,
            "validation_status": release_gate.get("status", "BLOCKED"),
            "summary": "Export blocked by release gate."
        }
        return state

    if not project_path_str or not os.path.exists(project_path_str):
        state["export"] = {
            "status": "FAILED",
            "zip_path": None,
            "file_count": 0,
            "validation_status": "ERROR",
            "summary": "Export failed: assembled project path does not exist."
        }
        return state

    project_dir = Path(project_path_str)

    export_dir_env = os.environ.get("AI_PRODUCT_ARCHITECT_EXPORT_DIR")
    if export_dir_env:
        export_base = Path(export_dir_env).resolve()
    else:
        export_base = (Path(__file__).resolve().parents[2] / "generated_projects").resolve()

    export_base.mkdir(parents=True, exist_ok=True)
    zip_path = export_base / f"{project_id}.zip"

    EXCLUDED_PATTERNS = [
        ".env",
        ".terraform",
        "terraform.tfstate",
        ".tfstate",
        "__pycache__",
        ".git",
        ".DS_Store",
    ]

    file_count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in project_dir.rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(project_dir)
                rel_parts = rel_path.parts
                # Check exclusions
                should_exclude = any(
                    exc in part for part in rel_parts for exc in EXCLUDED_PATTERNS
                ) or file.name == ".env" or file.name.endswith(".tfstate") or file.name.endswith(".tfstate.backup")
                if not should_exclude:
                    zipf.write(file, arcname=str(rel_path))
                    file_count += 1

    export_result = {
        "status": "SUCCESS",
        "zip_path": str(zip_path),
        "file_count": file_count,
        "validation_status": "APPROVED",
        "summary": f"Successfully packaged {file_count} files into {zip_path.name}"
    }

    state["export"] = export_result

    architecture = state.get("architecture", {})
    architecture["export"] = export_result
    state["architecture"] = architecture

    return state
