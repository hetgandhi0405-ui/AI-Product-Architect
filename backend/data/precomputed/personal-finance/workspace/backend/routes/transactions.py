# Route Handlers for transactions (Transaction)
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

router = APIRouter()

class TransactionCreate(BaseModel):
    title: Optional[str] = Field(None, description="Primary label or title")
    name: Optional[str] = Field(None, description="Entity name")
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    extra_data: Optional[Dict[str, Any]] = None

class TransactionUpdate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

_transactions_db = [
    {"id": 1, "created_at": datetime.utcnow(), "description": "Software Engineering Salary", "amount": 6200.0, "type": "income", "category": "Salary"},
    {"id": 2, "created_at": datetime.utcnow(), "description": "Apartment Rent", "amount": 1850.0, "type": "expense", "category": "Housing"},
    {"id": 3, "created_at": datetime.utcnow(), "description": "Supermarket Groceries", "amount": 215.4, "type": "expense", "category": "Food"}
]

@router.get("/", response_model=List[Dict[str, Any]])
def list_transactions(skip: int = Query(0, ge=0), limit: int = Query(50, le=100)):
    return _transactions_db[skip:skip + limit]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate):
    new_id = len(_transactions_db) + 1
    new_item = {
        "id": new_id,
        "title": payload.title or payload.name or f"Transaction {new_id}",
        "name": payload.name or payload.title or f"Transaction {new_id}",
        "description": payload.description or "",
        "priority": payload.priority or "medium",
        "status": payload.status or "active",
        "created_at": datetime.utcnow()
    }
    if payload.extra_data:
        new_item.update(payload.extra_data)
    _transactions_db.append(new_item)
    return new_item

@router.get("/export-csv")
def export_transactions_csv():
    from fastapi.responses import PlainTextResponse
    lines = ["id,description,amount,type,category,date"]
    for t in _transactions_db:
        lines.append(f"{t.get('id')},{t.get('description','Item')},{t.get('amount',0)},{t.get('type','expense')},{t.get('category','General')},{t.get('created_at',datetime.utcnow())}")
    return PlainTextResponse("\n".join(lines), media_type="text/csv")

@router.get("/{item_id}")
def get_transaction(item_id: int):
    for item in _transactions_db:
        if item.get("id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="Transaction record not found")

@router.put("/{item_id}")
def update_transaction(item_id: int, payload: TransactionUpdate):
    for item in _transactions_db:
        if item.get("id") == item_id:
            if payload.title is not None: item["title"] = payload.title
            if payload.name is not None: item["name"] = payload.name
            if payload.description is not None: item["description"] = payload.description
            if payload.priority is not None: item["priority"] = payload.priority
            if payload.status is not None: item["status"] = payload.status
            return item
    raise HTTPException(status_code=404, detail="Transaction record not found")

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_transaction(item_id: int):
    global _transactions_db
    initial_len = len(_transactions_db)
    _transactions_db = [item for item in _transactions_db if item.get("id") != item_id]
    if len(_transactions_db) == initial_len:
        raise HTTPException(status_code=404, detail="Transaction record not found")
    return {"deleted": True, "id": item_id, "message": "Transaction successfully removed"}
