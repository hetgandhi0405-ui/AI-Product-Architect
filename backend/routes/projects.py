from fastapi import APIRouter, HTTPException
from uuid import uuid4

from backend.schemas.project import ProjectState

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

projects = {}


@router.post("/")
def create_project(project_name: str):

    project_id = str(uuid4())

    project = ProjectState(
        project_id=project_id,
        project_name=project_name,
        status="created"
    )

    projects[project_id] = project

    return project


@router.get("/{project_id}")
def get_project(project_id: str):

    project = projects.get(project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project