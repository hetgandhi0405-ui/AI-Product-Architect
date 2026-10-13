# Secondary Route Handlers for categories (Category)
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

router = APIRouter()

class CategoryCreate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "active"

class CategoryResponse(BaseModel):
    id: int
    status: str = "active"
    created_at: Optional[datetime] = None

_categories_db = [
    {"id": 1, "name": "Primary Category Record", "status": "active", "created_at": datetime.utcnow()},
    {"id": 2, "name": "Secondary Category Record", "status": "completed", "created_at": datetime.utcnow()}
]

@router.get("/", response_model=List[Dict[str, Any]])
def list_categories(skip: int = Query(0, ge=0), limit: int = Query(50, le=100)):
    return _categories_db[skip:skip + limit]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate):
    new_id = len(_categories_db) + 1
    new_item = {
        "id": new_id,
        "name": payload.name or payload.title or f"Category {new_id}",
        "description": payload.description or "",
        "status": payload.status or "active",
        "created_at": datetime.utcnow()
    }
    _categories_db.append(new_item)
    return new_item

@router.get("/{item_id}")
def get_category(item_id: int):
    for item in _categories_db:
        if item.get("id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="Category record not found")
