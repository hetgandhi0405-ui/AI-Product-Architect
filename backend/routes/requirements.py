import os
import re
from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.agents.graph import build_agent_graph
from backend.schemas.requirement import RequirementRequest
from backend.core.execution_config import get_execution_config
from backend.core.pipeline_metrics import create_metrics


router = APIRouter(prefix="/requirements", tags=["Requirements"])
agent_graph = build_agent_graph()


def _derive_project_name(prompt: str) -> str:
    text = re.sub(r"[^A-Za-z0-9\\s-]", " ", prompt)
    stop = {"create", "build", "make", "develop", "design", "application", "app", "website", "web", "system", "platform", "where", "that", "with", "for", "the", "and", "users", "user"}
    words = [word for word in text.split() if word and word.lower() not in stop][:5]
    return " ".join(words).title() if words else "Generated Product"


@router.post("/")
def process_requirement(request: RequirementRequest, execution_mode: str = "FULL"):
    """Accept one customer prompt and return the generated project deliverables."""
    try:
        config = get_execution_config(execution_mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    project_id = str(uuid4())
    project_name = request.project_name.strip() if request.project_name else _derive_project_name(request.description)
    state = {
        "project_id": project_id,
        "execution_mode": config.mode,
        "pipeline_metrics": create_metrics(),
        "project_name": project_name,
        "requirements": request.description,
        "users": request.users,
        "features": request.features,
        "security_level": request.security_level,
        "availability": request.availability,
        "suggestions": [],
        "architecture": {},
    }

    try:
        result = agent_graph.invoke(state)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {exc}") from exc

    export = result.get("project_export", {})
    export_status = export.get("status")
    download_url = None
    if export_status == "EXPORTED":
        download_url = f"/api/requirements/export/{project_id}"

    architecture = result.get("architecture", {})
    release_gate = result.get("release_gate", {})

    return {
        "project_id": project_id,
        "project_name": result.get("project_name", project_name),
        "prompt": result.get("requirements", request.description),
        "requirements": result.get("requirements", request.description),
        "execution_mode": result.get("execution_mode", config.mode),
        "status": "DELIVERED" if download_url else "BLOCKED",
        "download_url": download_url,
        "pipeline_metrics": result.get("pipeline_metrics", {}),
        "suggestions": result.get("suggestions", []),
        "architecture": architecture,
        "diagram": architecture.get("diagram", ""),
        "infrastructure": architecture.get("infrastructure", {}),
        "tool_registry": result.get("tool_registry", {}),
        "selected_tools": result.get("selected_tools", {}),
        "security_analysis": result.get("security_analysis", {}),
        "cost_analysis": result.get("cost_analysis", {}),
        "architecture_recommendation": result.get("architecture_recommendation", {}),
        "requirement_traceability": result.get("requirement_traceability", {}),
        "dependency_specification": result.get("dependency_specification", {}),
        "environment_configuration": result.get("environment_configuration", {}),
        "code_generation_contract": result.get("code_generation_contract", {}),
        "file_manifest": result.get("file_manifest", {}),
        "generated_code_validation": result.get("generated_code_validation", {}),
        "generated_project_path": result.get("generated_project_path", ""),
        "project_export": export,
        "project_build": result.get("project_build", {}),
        "api_contract_validation": result.get("api_contract_validation", {}),
        "database_integration_validation": result.get("database_integration_validation", {}),
        "docker_runtime_validation": result.get("docker_runtime_validation", {}),
        "release_gate": release_gate,
    }


@router.get("/export/{project_id}")
def download_project(project_id: str):
    """Download the generated project ZIP by project ID."""
    output_dir = Path(os.getenv("AI_PRODUCT_ARCHITECT_EXPORT_DIR", "generated_projects"))
    export = output_dir / f"{project_id}.zip"
    if not export.exists():
        raise HTTPException(status_code=404, detail="Generated project ZIP not found")
    return FileResponse(path=export, media_type="application/zip", filename=export.name)
