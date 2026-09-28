import os
import uuid
import re
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.agents.graph import build_agent_graph
from backend.schemas.requirement import RequirementRequest


router = APIRouter(
    prefix="/requirements",
    tags=["Requirements"]
)

agent_graph = build_agent_graph()


def _derive_project_name(description: str) -> str:
    """
    Derive a clean, concise project name from customer description.
    """
    # Clean words
    words = re.findall(r"[A-Za-z0-9]+", description)
    # Filter out common filler words
    stop_words = {"create", "a", "an", "the", "build", "make", "application", "app", "system", "platform", "where", "users", "can"}
    meaningful = [w for w in words if w.lower() not in stop_words]
    if meaningful:
        candidate = " ".join(meaningful[:3]).title() + " App"
        return candidate
    return "AI Cloud Application"


@router.post("/")
def process_requirement(request: RequirementRequest):
    """
    Process customer natural-language requirement prompt through the
    complete AI Product Architect graph pipeline:
    Requirements -> Product Plan -> Specs -> Architecture -> Contract ->
    Manifest -> Code Generation -> Assembly -> Validation -> Self-Correction ->
    Release Gate -> ZIP Export.
    """
    project_id = request.project_id or f"proj-{uuid.uuid4().hex[:8]}"
    project_name = request.project_name or _derive_project_name(request.description)

    initial_state = {
        "project_id": project_id,
        "project_name": project_name,
        "requirements": request.description,
        "suggestions": [],
        "architecture": {},
        "correction_attempts": 0,
        "max_correction_attempts": 3,
        "code_correction_attempts": 0,
        "max_code_correction_attempts": 3,
        "integration_correction_attempts": 0,
        "max_integration_correction_attempts": 2,
    }

    result = agent_graph.invoke(initial_state)

    architecture = result.get("architecture", {})
    manifest = result.get("file_manifest", {})
    release_gate = result.get("release_gate", {})
    export_info = result.get("export", {})

    download_url = None
    if export_info.get("status") == "SUCCESS" and export_info.get("zip_path"):
        download_url = f"/api/requirements/export/{project_id}"

    return {
        "project_id": project_id,
        "project_name": result.get("project_name", project_name),
        "requirements": result.get("requirements", request.description),
        "suggestions": result.get("suggestions", []),
        "architecture": architecture,
        "diagram": architecture.get("diagram", ""),
        "infrastructure": architecture.get("infrastructure", {}),
        "file_manifest": manifest,
        "generated_files_count": len(result.get("generated_files", {})),
        "assembled_project_path": result.get("assembled_project_path"),
        "code_validation": result.get("code_validation", {}),
        "build_validation": result.get("build_validation", {}),
        "api_validation": result.get("api_validation", {}),
        "database_validation": result.get("database_validation", {}),
        "docker_validation": result.get("docker_validation", {}),
        "release_gate": release_gate,
        "export": export_info,
        "download_url": download_url,
    }


@router.get("/export/{project_id}")
def export_project(project_id: str):
    """
    Download the generated project ZIP archive.
    """
    export_dir_env = os.environ.get("AI_PRODUCT_ARCHITECT_EXPORT_DIR")
    if export_dir_env:
        export_base = Path(export_dir_env).resolve()
    else:
        export_base = (Path(__file__).resolve().parents[2] / "generated_projects").resolve()

    zip_path = export_base / f"{project_id}.zip"

    if not zip_path.exists() or not zip_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Export archive for project '{project_id}' not found. Either generation is still running, or release gate blocked export."
        )

    return FileResponse(
        path=str(zip_path),
        filename=f"{project_id}.zip",
        media_type="application/zip"
    )