# Route Handlers for tickets (Ticket)
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

router = APIRouter()

class TicketCreate(BaseModel):
    title: Optional[str] = Field(None, description="Primary label or title")
    name: Optional[str] = Field(None, description="Entity name")
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    extra_data: Optional[Dict[str, Any]] = None

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class TicketResponse(BaseModel):
    id: int
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "active"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

_tickets_db = [
    {"id": 1, "created_at": datetime.utcnow(), "subject": "Payment Processing Failed", "priority": "urgent", "status": "in_progress", "dept": "Billing"},
    {"id": 2, "created_at": datetime.utcnow(), "subject": "Cannot Access Admin Settings", "priority": "high", "status": "open", "dept": "Auth"},
    {"id": 3, "created_at": datetime.utcnow(), "subject": "Upgrade Database Plan Inquiry", "priority": "low", "status": "resolved", "dept": "Sales"}
]

@router.get("/", response_model=List[Dict[str, Any]])
def list_tickets(skip: int = Query(0, ge=0), limit: int = Query(50, le=100)):
    return _tickets_db[skip:skip + limit]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreate):
    new_id = len(_tickets_db) + 1
    new_item = {
        "id": new_id,
        "title": payload.title or payload.name or f"Ticket {new_id}",
        "name": payload.name or payload.title or f"Ticket {new_id}",
        "description": payload.description or "",
        "priority": payload.priority or "medium",
        "status": payload.status or "active",
        "created_at": datetime.utcnow()
    }
    if payload.extra_data:
        new_item.update(payload.extra_data)
    _tickets_db.append(new_item)
    return new_item

@router.patch("/{item_id}/assign")
def assign_ticket(item_id: int, agent_id: int = Query(..., ge=1)):
    for item in _tickets_db:
        if item.get("id") == item_id:
            item["assigned_agent_id"] = agent_id
            item["status"] = "in_progress"
            return item
    return {"ticket_id": item_id, "assigned_agent_id": agent_id, "status": "in_progress"}

@router.get("/{item_id}")
def get_ticket(item_id: int):
    for item in _tickets_db:
        if item.get("id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="Ticket record not found")

@router.put("/{item_id}")
def update_ticket(item_id: int, payload: TicketUpdate):
    for item in _tickets_db:
        if item.get("id") == item_id:
            if payload.title is not None: item["title"] = payload.title
            if payload.name is not None: item["name"] = payload.name
            if payload.description is not None: item["description"] = payload.description
            if payload.priority is not None: item["priority"] = payload.priority
            if payload.status is not None: item["status"] = payload.status
            return item
    raise HTTPException(status_code=404, detail="Ticket record not found")

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_ticket(item_id: int):
    global _tickets_db
    initial_len = len(_tickets_db)
    _tickets_db = [item for item in _tickets_db if item.get("id") != item_id]
    if len(_tickets_db) == initial_len:
        raise HTTPException(status_code=404, detail="Ticket record not found")
    return {"deleted": True, "id": item_id, "message": "Ticket successfully removed"}
