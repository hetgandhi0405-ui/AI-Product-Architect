# Route Handlers for products (Product)
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

router = APIRouter()

class ProductCreate(BaseModel):
    title: Optional[str] = Field(None, description="Primary label or title")
    name: Optional[str] = Field(None, description="Entity name")
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    extra_data: Optional[Dict[str, Any]] = None

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

_products_db = [
    {"id": 1, "created_at": datetime.utcnow(), "name": "Wireless Noise-Canceling Headphones", "price": 199.99, "stock": 45, "category": "Audio"},
    {"id": 2, "created_at": datetime.utcnow(), "name": "Mechanical RGB Gaming Keyboard", "price": 129.5, "stock": 20, "category": "Peripherals"},
    {"id": 3, "created_at": datetime.utcnow(), "name": "Ultra-Wide 4K IPS Monitor 34\"", "price": 499.0, "stock": 12, "category": "Displays"}
]

@router.get("/", response_model=List[Dict[str, Any]])
def list_products(skip: int = Query(0, ge=0), limit: int = Query(50, le=100)):
    return _products_db[skip:skip + limit]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate):
    new_id = len(_products_db) + 1
    new_item = {
        "id": new_id,
        "title": payload.title or payload.name or f"Product {new_id}",
        "name": payload.name or payload.title or f"Product {new_id}",
        "description": payload.description or "",
        "priority": payload.priority or "medium",
        "status": payload.status or "active",
        "created_at": datetime.utcnow()
    }
    if payload.extra_data:
        new_item.update(payload.extra_data)
    _products_db.append(new_item)
    return new_item

@router.post("/{item_id}/checkout")
def checkout_order(item_id: int):
    for item in _products_db:
        if item.get("id") == item_id:
            return {"order_id": item_id, "status": "paid", "amount": item.get("price", 199.99), "transaction_id": "tx_sandbox_948102"}
    return {"order_id": item_id, "status": "paid", "amount": 199.99, "transaction_id": "tx_sandbox_948102"}

@router.get("/{item_id}")
def get_product(item_id: int):
    for item in _products_db:
        if item.get("id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="Product record not found")

@router.put("/{item_id}")
def update_product(item_id: int, payload: ProductUpdate):
    for item in _products_db:
        if item.get("id") == item_id:
            if payload.title is not None: item["title"] = payload.title
            if payload.name is not None: item["name"] = payload.name
            if payload.description is not None: item["description"] = payload.description
            if payload.priority is not None: item["priority"] = payload.priority
            if payload.status is not None: item["status"] = payload.status
            return item
    raise HTTPException(status_code=404, detail="Product record not found")

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_product(item_id: int):
    global _products_db
    initial_len = len(_products_db)
    _products_db = [item for item in _products_db if item.get("id") != item_id]
    if len(_products_db) == initial_len:
        raise HTTPException(status_code=404, detail="Product record not found")
    return {"deleted": True, "id": item_id, "message": "Product successfully removed"}
