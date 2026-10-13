# Route Handlers for devices (Device)
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

router = APIRouter()

class DeviceCreate(BaseModel):
    title: Optional[str] = Field(None, description="Primary label or title")
    name: Optional[str] = Field(None, description="Entity name")
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    extra_data: Optional[Dict[str, Any]] = None

class DeviceUpdate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class DeviceResponse(BaseModel):
    id: int
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

_devices_db = [
    {"id": 1, "created_at": datetime.utcnow(), "name": "Living Room Thermostat", "type": "thermostat", "room": "Living Room", "status": "online"},
    {"id": 2, "created_at": datetime.utcnow(), "name": "Balcony Weather Sensor", "type": "sensor", "room": "Outdoor", "status": "online"},
    {"id": 3, "created_at": datetime.utcnow(), "name": "Basement Smart Power Meter", "type": "energy", "room": "Basement", "status": "online"}
]

@router.get("/", response_model=List[Dict[str, Any]])
def list_devices(skip: int = Query(0, ge=0), limit: int = Query(50, le=100)):
    return _devices_db[skip:skip + limit]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_device(payload: DeviceCreate):
    new_id = len(_devices_db) + 1
    new_item = {
        "id": new_id,
        "title": payload.title or payload.name or f"Device {new_id}",
        "name": payload.name or payload.title or f"Device {new_id}",
        "description": payload.description or "",
        "priority": payload.priority or "medium",
        "status": payload.status or "active",
        "created_at": datetime.utcnow()
    }
    if payload.extra_data:
        new_item.update(payload.extra_data)
    _devices_db.append(new_item)
    return new_item

@router.post("/{item_id}/telemetry")
def ingest_telemetry(item_id: int, payload: Dict[str, Any]):
    return {"device_id": item_id, "status": "ingested", "metric": payload.get("metric", "temperature"), "timestamp": datetime.utcnow()}

@router.get("/{item_id}")
def get_device(item_id: int):
    for item in _devices_db:
        if item.get("id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="Device record not found")

@router.put("/{item_id}")
def update_device(item_id: int, payload: DeviceUpdate):
    for item in _devices_db:
        if item.get("id") == item_id:
            if payload.title is not None: item["title"] = payload.title
            if payload.name is not None: item["name"] = payload.name
            if payload.description is not None: item["description"] = payload.description
            if payload.priority is not None: item["priority"] = payload.priority
            if payload.status is not None: item["status"] = payload.status
            return item
    raise HTTPException(status_code=404, detail="Device record not found")

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_device(item_id: int):
    global _devices_db
    initial_len = len(_devices_db)
    _devices_db = [item for item in _devices_db if item.get("id") != item_id]
    if len(_devices_db) == initial_len:
        raise HTTPException(status_code=404, detail="Device record not found")
    return {"deleted": True, "id": item_id, "message": "Device successfully removed"}
