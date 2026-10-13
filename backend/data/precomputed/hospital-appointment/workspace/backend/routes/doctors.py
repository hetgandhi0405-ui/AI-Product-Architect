# Route Handlers for doctors (Doctor)
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

router = APIRouter()

class DoctorCreate(BaseModel):
    title: Optional[str] = Field(None, description="Primary label or title")
    name: Optional[str] = Field(None, description="Entity name")
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    extra_data: Optional[Dict[str, Any]] = None

class DoctorUpdate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class DoctorResponse(BaseModel):
    id: int
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

_doctors_db = [
    {"id": 1, "created_at": datetime.utcnow(), "name": "Dr. Meredith Grey, MD", "specialty": "General Surgery", "room": "OR-4B", "available": True},
    {"id": 2, "created_at": datetime.utcnow(), "name": "Dr. Gregory House, MD", "specialty": "Diagnostics & Infectious", "room": "Clinic-101", "available": True},
    {"id": 3, "created_at": datetime.utcnow(), "name": "Dr. Cristina Yang, MD", "specialty": "Cardiothoracic Surgery", "room": "OR-2A", "available": False}
]

@router.get("/", response_model=List[Dict[str, Any]])
def list_doctors(skip: int = Query(0, ge=0), limit: int = Query(50, le=100)):
    return _doctors_db[skip:skip + limit]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_doctor(payload: DoctorCreate):
    new_id = len(_doctors_db) + 1
    new_item = {
        "id": new_id,
        "title": payload.title or payload.name or f"Doctor {new_id}",
        "name": payload.name or payload.title or f"Doctor {new_id}",
        "description": payload.description or "",
        "priority": payload.priority or "medium",
        "status": payload.status or "active",
        "created_at": datetime.utcnow()
    }
    if payload.extra_data:
        new_item.update(payload.extra_data)
    _doctors_db.append(new_item)
    return new_item

@router.patch("/{item_id}/cancel")
def cancel_appointment(item_id: int):
    for item in _doctors_db:
        if item.get("id") == item_id:
            item["available"] = True
    return {"appointment_id": item_id, "status": "cancelled", "message": "Appointment cancelled and doctor slot released"}

@router.get("/available-slots")
def get_available_slots():
    return [{"doctor_id": 1, "doctor_name": "Dr. Meredith Grey, MD", "slots": ["09:00 AM", "11:30 AM", "02:00 PM"]}]

@router.get("/{item_id}")
def get_doctor(item_id: int):
    for item in _doctors_db:
        if item.get("id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="Doctor record not found")

@router.put("/{item_id}")
def update_doctor(item_id: int, payload: DoctorUpdate):
    for item in _doctors_db:
        if item.get("id") == item_id:
            if payload.title is not None: item["title"] = payload.title
            if payload.name is not None: item["name"] = payload.name
            if payload.description is not None: item["description"] = payload.description
            if payload.priority is not None: item["priority"] = payload.priority
            if payload.status is not None: item["status"] = payload.status
            return item
    raise HTTPException(status_code=404, detail="Doctor record not found")

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_doctor(item_id: int):
    global _doctors_db
    initial_len = len(_doctors_db)
    _doctors_db = [item for item in _doctors_db if item.get("id") != item_id]
    if len(_doctors_db) == initial_len:
        raise HTTPException(status_code=404, detail="Doctor record not found")
    return {"deleted": True, "id": item_id, "message": "Doctor successfully removed"}
