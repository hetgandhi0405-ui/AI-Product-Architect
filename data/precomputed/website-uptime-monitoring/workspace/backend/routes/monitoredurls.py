# Route Handlers for monitoredurls (MonitoredUrl)
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

router = APIRouter()

class MonitoredUrlCreate(BaseModel):
    title: Optional[str] = Field(None, description="Primary label or title")
    name: Optional[str] = Field(None, description="Entity name")
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    extra_data: Optional[Dict[str, Any]] = None

class MonitoredUrlUpdate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class MonitoredUrlResponse(BaseModel):
    id: int
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

_monitoredurls_db = [
    {"id": 1, "created_at": datetime.utcnow(), "name": "Payment Gateway API", "url": "https://api.payments.internal", "status": "Operational", "latency": "38 ms"},
    {"id": 2, "created_at": datetime.utcnow(), "name": "User Identity Service", "url": "https://auth.enterprise.io", "status": "Operational", "latency": "22 ms"},
    {"id": 3, "created_at": datetime.utcnow(), "name": "Global Edge CDN Ingress", "url": "https://cdn.global.net", "status": "Operational", "latency": "14 ms"}
]

@router.get("/", response_model=List[Dict[str, Any]])
def list_monitoredurls(skip: int = Query(0, ge=0), limit: int = Query(50, le=100)):
    return _monitoredurls_db[skip:skip + limit]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_monitoredurl(payload: MonitoredUrlCreate):
    new_id = len(_monitoredurls_db) + 1
    new_item = {
        "id": new_id,
        "title": payload.title or payload.name or f"MonitoredUrl {new_id}",
        "name": payload.name or payload.title or f"MonitoredUrl {new_id}",
        "description": payload.description or "",
        "priority": payload.priority or "medium",
        "status": payload.status or "active",
        "created_at": datetime.utcnow()
    }
    if payload.extra_data:
        new_item.update(payload.extra_data)
    _monitoredurls_db.append(new_item)
    return new_item

@router.post("/{item_id}/check")
def trigger_prober_check(item_id: int):
    return {"monitor_id": item_id, "is_up": True, "status_code": 200, "response_time_ms": 38.4, "checked_at": datetime.utcnow()}

@router.get("/{item_id}")
def get_monitoredurl(item_id: int):
    for item in _monitoredurls_db:
        if item.get("id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="MonitoredUrl record not found")

@router.put("/{item_id}")
def update_monitoredurl(item_id: int, payload: MonitoredUrlUpdate):
    for item in _monitoredurls_db:
        if item.get("id") == item_id:
            if payload.title is not None: item["title"] = payload.title
            if payload.name is not None: item["name"] = payload.name
            if payload.description is not None: item["description"] = payload.description
            if payload.priority is not None: item["priority"] = payload.priority
            if payload.status is not None: item["status"] = payload.status
            return item
    raise HTTPException(status_code=404, detail="MonitoredUrl record not found")

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_monitoredurl(item_id: int):
    global _monitoredurls_db
    initial_len = len(_monitoredurls_db)
    _monitoredurls_db = [item for item in _monitoredurls_db if item.get("id") != item_id]
    if len(_monitoredurls_db) == initial_len:
        raise HTTPException(status_code=404, detail="MonitoredUrl record not found")
    return {"deleted": True, "id": item_id, "message": "MonitoredUrl successfully removed"}
