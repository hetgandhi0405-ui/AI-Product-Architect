import os
import json
from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from uuid import uuid4

from backend.schemas.project import ProjectState

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

STORE_PATH = Path(__file__).resolve().parents[2] / "data" / "projects_store.json"


def _load_store() -> Dict[str, Any]:
    if STORE_PATH.exists():
        try:
            with open(STORE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_store(data: Dict[str, Any]):
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


projects = _load_store()


def record_project(data: Dict[str, Any]):
    p_id = data.get("project_id")
    if not p_id:
        return
    store = _load_store()
    store[p_id] = data
    _save_store(store)
    projects[p_id] = data


@router.get("/")
def list_projects() -> List[Dict[str, Any]]:
    """
    List all created and executed projects from persistent storage.
    """
    store = _load_store()
    # If store is empty, include a demo project so the UI has initial data
    if not store:
        demo = {
            "project_id": "PRJ_20261010_001",
            "project_name": "E-Commerce Platform",
            "status": "completed",
            "project_type": "Full Stack Web App",
            "preferred_stack": "React, FastAPI, PostgreSQL, Redis",
            "created_at": "10 Oct 2026, 12:15 PM",
            "duration": "4 minutes 32 seconds",
            "requirements": "Create an e-commerce website for small businesses with user authentication, product management, payment integration, and admin dashboard.",
            "coverage": 92,
            "release_gate": "PASSED"
        }
        record_project(demo)
        return [demo]
    return list(store.values())


@router.post("/")
def create_project(project_name: str):
    project_id = str(uuid4())

    project = ProjectState(
        project_id=project_id,
        project_name=project_name,
        status="created"
    )

    record_project(project.model_dump())
    return project


@router.get("/{project_id}")
def get_project(project_id: str):
    store = _load_store()
    project = store.get(project_id) or projects.get(project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project


@router.delete("/{project_id}")
def delete_project(project_id: str):
    """
    Safely delete a project record from persistent storage.
    """
    store = _load_store()
    if project_id in store:
        del store[project_id]
        _save_store(store)
    if project_id in projects:
        del projects[project_id]
    return {"status": "deleted", "project_id": project_id}