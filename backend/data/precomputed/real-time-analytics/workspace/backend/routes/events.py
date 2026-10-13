# Route Handlers for events (Event)
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

router = APIRouter()

class EventCreate(BaseModel):
    title: Optional[str] = Field(None, description="Primary label or title")
    name: Optional[str] = Field(None, description="Entity name")
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    extra_data: Optional[Dict[str, Any]] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class EventResponse(BaseModel):
    id: int
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

_events_db = [
    {"id": 1, "created_at": datetime.utcnow(), "type": "user_checkout_completed", "source": "Storefront Web", "eps": 1400, "status": "streaming"},
    {"id": 2, "created_at": datetime.utcnow(), "type": "api_latency_heartbeat", "source": "API Gateway", "eps": 820, "status": "streaming"},
    {"id": 3, "created_at": datetime.utcnow(), "type": "fraud_detection_scored", "source": "Security Worker", "eps": 310, "status": "streaming"}
]

@router.get("/", response_model=List[Dict[str, Any]])
def list_events(skip: int = Query(0, ge=0), limit: int = Query(50, le=100)):
    return _events_db[skip:skip + limit]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate):
    new_id = len(_events_db) + 1
    new_item = {
        "id": new_id,
        "title": payload.title or payload.name or f"Event {new_id}",
        "name": payload.name or payload.title or f"Event {new_id}",
        "description": payload.description or "",
        "priority": payload.priority or "medium",
        "status": payload.status or "active",
        "created_at": datetime.utcnow()
    }
    if payload.extra_data:
        new_item.update(payload.extra_data)
    _events_db.append(new_item)
    return new_item

@router.post("/ingest")
def ingest_event(payload: Dict[str, Any]):
    return {"status": "buffered", "event_id": len(_events_db) + 1, "buffer": "redis_stream", "timestamp": datetime.utcnow()}

@router.get("/realtime")
def get_realtime_aggregates():
    return {"window": "5m", "events_per_sec": 1420, "top_event": "user_checkout_completed", "cache_latency_ms": 1.2}

@router.get("/{item_id}")
def get_event(item_id: int):
    for item in _events_db:
        if item.get("id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="Event record not found")

@router.put("/{item_id}")
def update_event(item_id: int, payload: EventUpdate):
    for item in _events_db:
        if item.get("id") == item_id:
            if payload.title is not None: item["title"] = payload.title
            if payload.name is not None: item["name"] = payload.name
            if payload.description is not None: item["description"] = payload.description
            if payload.priority is not None: item["priority"] = payload.priority
            if payload.status is not None: item["status"] = payload.status
            return item
    raise HTTPException(status_code=404, detail="Event record not found")

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_event(item_id: int):
    global _events_db
    initial_len = len(_events_db)
    _events_db = [item for item in _events_db if item.get("id") != item_id]
    if len(_events_db) == initial_len:
        raise HTTPException(status_code=404, detail="Event record not found")
    return {"deleted": True, "id": item_id, "message": "Event successfully removed"}
