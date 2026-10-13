# Secondary Route Handlers for streamsources (StreamSource)
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

router = APIRouter()

class StreamSourceCreate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "active"

class StreamSourceResponse(BaseModel):
    id: int
    status: str = "active"
    created_at: Optional[datetime] = None

_streamsources_db = [
    {"id": 1, "name": "Primary StreamSource Record", "status": "active", "created_at": datetime.utcnow()},
    {"id": 2, "name": "Secondary StreamSource Record", "status": "completed", "created_at": datetime.utcnow()}
]

@router.get("/", response_model=List[Dict[str, Any]])
def list_streamsources(skip: int = Query(0, ge=0), limit: int = Query(50, le=100)):
    return _streamsources_db[skip:skip + limit]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_streamsource(payload: StreamSourceCreate):
    new_id = len(_streamsources_db) + 1
    new_item = {
        "id": new_id,
        "name": payload.name or payload.title or f"StreamSource {new_id}",
        "description": payload.description or "",
        "status": payload.status or "active",
        "created_at": datetime.utcnow()
    }
    _streamsources_db.append(new_item)
    return new_item

@router.get("/{item_id}")
def get_streamsource(item_id: int):
    for item in _streamsources_db:
        if item.get("id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="StreamSource record not found")
