# Route Handlers for employees (Employee)
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

router = APIRouter()

class EmployeeCreate(BaseModel):
    title: Optional[str] = Field(None, description="Primary label or title")
    name: Optional[str] = Field(None, description="Entity name")
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    extra_data: Optional[Dict[str, Any]] = None

class EmployeeUpdate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class EmployeeResponse(BaseModel):
    id: int
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

_employees_db = [
    {"id": 1, "created_at": datetime.utcnow(), "code": "EMP-4401", "name": "Sophia Rodriguez", "dept": "Engineering", "balance": 22},
    {"id": 2, "created_at": datetime.utcnow(), "code": "EMP-4402", "name": "Marcus Vance", "dept": "Product", "balance": 18},
    {"id": 3, "created_at": datetime.utcnow(), "code": "EMP-4403", "name": "Amina Chen", "dept": "Operations", "balance": 24}
]

@router.get("/", response_model=List[Dict[str, Any]])
def list_employees(skip: int = Query(0, ge=0), limit: int = Query(50, le=100)):
    return _employees_db[skip:skip + limit]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate):
    new_id = len(_employees_db) + 1
    new_item = {
        "id": new_id,
        "title": payload.title or payload.name or f"Employee {new_id}",
        "name": payload.name or payload.title or f"Employee {new_id}",
        "description": payload.description or "",
        "priority": payload.priority or "medium",
        "status": payload.status or "active",
        "created_at": datetime.utcnow()
    }
    if payload.extra_data:
        new_item.update(payload.extra_data)
    _employees_db.append(new_item)
    return new_item

@router.post("/clock-in")
def clock_in(employee_id: int = Query(..., ge=1)):
    return {"employee_id": employee_id, "status": "present", "clock_in_time": datetime.utcnow(), "message": "Clock-in recorded"}

@router.post("/clock-out")
def clock_out(employee_id: int = Query(..., ge=1)):
    return {"employee_id": employee_id, "status": "clocked_out", "clock_out_time": datetime.utcnow(), "message": "Clock-out recorded"}

@router.get("/{item_id}")
def get_employee(item_id: int):
    for item in _employees_db:
        if item.get("id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="Employee record not found")

@router.put("/{item_id}")
def update_employee(item_id: int, payload: EmployeeUpdate):
    for item in _employees_db:
        if item.get("id") == item_id:
            if payload.title is not None: item["title"] = payload.title
            if payload.name is not None: item["name"] = payload.name
            if payload.description is not None: item["description"] = payload.description
            if payload.priority is not None: item["priority"] = payload.priority
            if payload.status is not None: item["status"] = payload.status
            return item
    raise HTTPException(status_code=404, detail="Employee record not found")

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_employee(item_id: int):
    global _employees_db
    initial_len = len(_employees_db)
    _employees_db = [item for item in _employees_db if item.get("id") != item_id]
    if len(_employees_db) == initial_len:
        raise HTTPException(status_code=404, detail="Employee record not found")
    return {"deleted": True, "id": item_id, "message": "Employee successfully removed"}
