import os
from pathlib import Path
import zipfile

from backend.agents.state import AgentState


def project_export_agent(state: AgentState) -> AgentState:
    root = Path(state.get("generated_project_path", ""))
    if not root.exists():
        state["export_status"] = "FAILED"
        state["export_error"] = "Generated project directory does not exist."
        return state
    output_dir = Path(os.getenv("AI_PRODUCT_ARCHITECT_EXPORT_DIR", "generated_projects"))
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"{root.name}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in root.rglob("*"):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(root))
    state["project_export"] = {
        "status": "EXPORTED",
        "zip_path": str(zip_path),
        "file_count": sum(1 for p in root.rglob("*") if p.is_file()),
        "validation_status": state.get("generated_code_validation", {}).get("status", "UNKNOWN"),
    }
    state["export_status"] = "EXPORTED"
    return state
