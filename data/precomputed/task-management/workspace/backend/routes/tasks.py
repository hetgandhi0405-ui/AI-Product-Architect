# Route Handlers for tasks (Task)
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

router = APIRouter()

class TaskCreate(BaseModel):
    title: Optional[str] = Field(None, description="Primary label or title")
    name: Optional[str] = Field(None, description="Entity name")
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    extra_data: Optional[Dict[str, Any]] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

_tasks_db = [
    {"id": 1, "created_at": datetime.utcnow(), "title": "Design Database Schema", "priority": "high", "status": "completed", "due": "Today"},
    {"id": 2, "created_at": datetime.utcnow(), "title": "Implement REST Endpoints", "priority": "urgent", "status": "in_progress", "due": "Tomorrow"},
    {"id": 3, "created_at": datetime.utcnow(), "title": "Write Integration Test Suite", "priority": "medium", "status": "pending", "due": "Friday"}
]

@router.get("/", response_model=List[Dict[str, Any]])
def list_tasks(skip: int = Query(0, ge=0), limit: int = Query(50, le=100)):
    return _tasks_db[skip:skip + limit]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    new_id = len(_tasks_db) + 1
    new_item = {
        "id": new_id,
        "title": payload.title or payload.name or f"Task {new_id}",
        "name": payload.name or payload.title or f"Task {new_id}",
        "description": payload.description or "",
        "priority": payload.priority or "medium",
        "status": payload.status or "active",
        "created_at": datetime.utcnow()
    }
    if payload.extra_data:
        new_item.update(payload.extra_data)
    _tasks_db.append(new_item)
    return new_item

@router.patch("/{item_id}/status")
def toggle_status(item_id: int, new_status: str = Query("completed")):
    for item in _tasks_db:
        if item.get("id") == item_id:
            item["status"] = new_status
            return item
    return {"id": item_id, "status": new_status, "updated_at": datetime.utcnow()}

@router.get("/{item_id}")
def get_task(item_id: int):
    for item in _tasks_db:
        if item.get("id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="Task record not found")

@router.put("/{item_id}")
def update_task(item_id: int, payload: TaskUpdate):
    for item in _tasks_db:
        if item.get("id") == item_id:
            if payload.title is not None: item["title"] = payload.title
            if payload.name is not None: item["name"] = payload.name
            if payload.description is not None: item["description"] = payload.description
            if payload.priority is not None: item["priority"] = payload.priority
            if payload.status is not None: item["status"] = payload.status
            return item
    raise HTTPException(status_code=404, detail="Task record not found")

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_task(item_id: int):
    global _tasks_db
    initial_len = len(_tasks_db)
    _tasks_db = [item for item in _tasks_db if item.get("id") != item_id]
    if len(_tasks_db) == initial_len:
        raise HTTPException(status_code=404, detail="Task record not found")
    return {"deleted": True, "id": item_id, "message": "Task successfully removed"}
