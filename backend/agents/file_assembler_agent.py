import os
from pathlib import Path
from backend.agents.state import AgentState


def file_assembler_agent(state: AgentState) -> AgentState:
    """
    Assemble generated file contents into a real physical directory structure
    at generated_projects/<project_id>/ with path traversal protection.
    """
    project_id = state.get("project_id", "default-project")
    generated_files = state.get("generated_files", {})

    base_dir_env = os.environ.get("AI_PRODUCT_ARCHITECT_PROJECTS_DIR")
    if base_dir_env:
        base_dir = Path(base_dir_env).resolve()
    else:
        # Resolve to <project_root>/generated_projects
        base_dir = (Path(__file__).resolve().parents[2] / "generated_projects").resolve()

    project_dir = (base_dir / project_id).resolve()
    project_dir.mkdir(parents=True, exist_ok=True)

    written_files = []
    errors = []

    for rel_path, content in generated_files.items():
        # Security protection against directory traversal attacks
        normalized_rel = os.path.normpath(rel_path).lstrip("/\\")
        target_path = (project_dir / normalized_rel).resolve()

        # Strict containment check
        try:
            target_path.relative_to(project_dir)
        except ValueError:
            errors.append(f"Illegal path traversal attempt detected for file: '{rel_path}'")
            continue

        # Create parent directories
        target_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(target_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            written_files.append(str(target_path))
        except Exception as e:
            errors.append(f"Failed to write '{rel_path}': {str(e)}")

    state["assembled_project_path"] = str(project_dir)

    architecture = state.get("architecture", {})
    architecture["assembly"] = {
        "project_dir": str(project_dir),
        "total_written": len(written_files),
        "errors": errors,
        "status": "SUCCESS" if not errors and written_files else "FAILED"
    }
    state["architecture"] = architecture

    return state
