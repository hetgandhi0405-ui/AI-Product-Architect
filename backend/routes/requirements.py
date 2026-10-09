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
def process_requirement(request: RequirementRequest, execution_mode: str = "QUICK"):
    """
    Process customer natural-language requirement prompt through the
    complete AI Product Architect graph pipeline:
    Requirements -> Product Plan -> Specs -> Architecture -> Contract ->
    Manifest -> Code Generation -> Assembly -> Validation -> Self-Correction ->
    Release Gate -> ZIP Export.
    """
    project_id = request.project_id or f"proj-{uuid.uuid4().hex[:8]}"
    project_name = request.project_name or _derive_project_name(request.description)
    mode = request.execution_mode or execution_mode or "QUICK"

    initial_state = {
        "project_id": project_id,
        "project_name": project_name,
        "requirements": request.description,
        "execution_mode": mode,
        "suggestions": [],
        "architecture": {},
        "correction_attempts": 0,
        "max_correction_attempts": 3,
        "code_correction_attempts": 0,
        "max_code_correction_attempts": 3,
        "integration_correction_attempts": 0,
        "max_integration_correction_attempts": 2,
    }

    try:
        result = agent_graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

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
        "deploy_mode": result.get("deploy_mode", "dry-run"),
        "docker_status": result.get("docker_status"),
        "registry_status": result.get("registry_status"),
        "deployment_status": result.get("deployment_status"),
        "terraform_status": result.get("terraform_status"),
        "deployment_validation_status": result.get("deployment_validation_status"),
        "health_status": result.get("health_status"),
        "service_url": result.get("service_url"),
        "telemetry_status": result.get("telemetry_status"),
        "cost_analysis": result.get("cost_analysis"),
        "performance_analysis": result.get("performance_analysis"),
        "reliability_analysis": result.get("reliability_analysis"),
        "architecture_analysis": result.get("architecture_analysis"),
        "optimization_candidates": result.get("optimization_candidates"),
        "optimization_recommendation": result.get("optimization_recommendation"),
        # Phase 1 — Product Metadata
        "product_metadata": result.get("product_metadata", {}),
        # Phase 2 — Extended Validation
        "dependency_validation": result.get("dependency_validation", {}),
        "frontend_validation": result.get("frontend_validation", {}),
        "security_validation": result.get("security_validation", {}),
        "validation_report": result.get("validation_report", {}),
        # Phase 6 — Terraform
        "terraform_generation": {
            k: v for k, v in result.get("terraform_generation", {}).items()
            if k != "file_contents"  # exclude raw HCL content from main response (too large)
        },
        "terraform_validation": result.get("terraform_validation", {}),
        # Phase 3 — Cloud Architecture
        "cloud_architecture_spec": result.get("cloud_architecture_spec", {}),
        # Phase 4 — Infrastructure State
        "infrastructure_state": result.get("infrastructure_state", {}),
        "infrastructure_state_path": result.get("infrastructure_state_path"),
        # Phase 5 — Architecture Diagram
        "architecture_diagram": result.get("architecture_diagram", ""),
        # Phase 8 — Deployment Approval & History
        "deployment_approval": result.get("deployment_approval", {}),
        "deployment_history": result.get("deployment_history", []),
        # Phase 12 — RL Evaluation
        "rl_evaluation": result.get("rl_evaluation", {}),
        "rl_state": result.get("rl_state", {}),
        "rl_action": result.get("rl_action", {}),
        # Phase 15 — Fine-tuning Dataset Record
        "finetuning_dataset_record": result.get("finetuning_dataset_record", {}),
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


@router.get("/terraform/{project_id}")
def get_terraform(project_id: str):
    """
    Download the generated Terraform files for a project as a ZIP archive.
    """
    export_dir_env = os.environ.get("AI_PRODUCT_ARCHITECT_EXPORT_DIR")
    if export_dir_env:
        export_base = Path(export_dir_env).resolve()
    else:
        export_base = (Path(__file__).resolve().parents[2] / "generated_projects").resolve()

    project_dir = export_base / project_id
    tf_dir = project_dir / "infrastructure" / "terraform"

    if not tf_dir.exists() or not tf_dir.is_dir():
        raise HTTPException(
            status_code=404,
            detail=f"Terraform files for project '{project_id}' not found. Run the generation pipeline first."
        )

    import zipfile
    import io
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for tf_file in sorted(tf_dir.glob("*.tf")):
            zf.write(tf_file, arcname=f"terraform/{tf_file.name}")
    buf.seek(0)

    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{project_id}-terraform.zip"'},
    )


@router.post("/rollback/{project_id}")
def rollback_deployment(project_id: str):
    """
    Execute controlled rollback to the previous known-good infrastructure snapshot.
    """
    export_dir_env = os.environ.get("AI_PRODUCT_ARCHITECT_EXPORT_DIR")
    if export_dir_env:
        export_base = Path(export_dir_env).resolve()
    else:
        export_base = (Path(__file__).resolve().parents[2] / "generated_projects").resolve()

    infra_file = export_base / project_id / "infrastructure" / "infrastructure_state.json"
    if not infra_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No infrastructure state found for project '{project_id}' to rollback."
        )

    import json
    from backend.agents.deployment_approval_agent import execute_rollback

    current_state = {
        "project_id": project_id,
        "infrastructure_state": json.loads(infra_file.read_text(encoding="utf-8")),
        "rollback_state": {
            "snapshot_id": f"snap-rollback-{project_id}",
            "infrastructure_state": json.loads(infra_file.read_text(encoding="utf-8")),
        }
    }

    result = execute_rollback(current_state)
    return {
        "project_id": project_id,
        "rollback_status": result.get("rollback_status", {}),
        "restored_infrastructure_state": result.get("infrastructure_state", {}),
    }