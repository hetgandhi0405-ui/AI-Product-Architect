# Secondary Route Handlers for orders (Order)
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

router = APIRouter()

class OrderCreate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "active"

class OrderResponse(BaseModel):
    id: int
    status: str = "active"
    created_at: Optional[datetime] = None

_orders_db = [
    {"id": 1, "name": "Primary Order Record", "status": "active", "created_at": datetime.utcnow()},
    {"id": 2, "name": "Secondary Order Record", "status": "completed", "created_at": datetime.utcnow()}
]

@router.get("/", response_model=List[Dict[str, Any]])
def list_orders(skip: int = Query(0, ge=0), limit: int = Query(50, le=100)):
    return _orders_db[skip:skip + limit]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate):
    new_id = len(_orders_db) + 1
    new_item = {
        "id": new_id,
        "name": payload.name or payload.title or f"Order {new_id}",
        "description": payload.description or "",
        "status": payload.status or "active",
        "created_at": datetime.utcnow()
    }
    _orders_db.append(new_item)
    return new_item

@router.get("/{item_id}")
def get_order(item_id: int):
    for item in _orders_db:
        if item.get("id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="Order record not found")
