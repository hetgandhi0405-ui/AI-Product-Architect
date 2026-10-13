from datetime import datetime
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title='Customer Support Ticketing System', version="0.1.0", description='tickets, priorities, assignments, status transitions, comments')
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

records: dict[str, list[dict[str, Any]]] = {'ticket': [], 'comment': []}
counters = {'ticket': 1, 'comment': 1}

class Record(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = ""

@app.get("/health")
def health():
    return {"status": "ok", "project": 'support-ticketing', "mode": "development-prototype"}

@app.get('/tickets')
def list_primary():
    return records['ticket']

@app.post('/tickets', status_code=201)
def create_primary(body: Record):
    key = 'ticket'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get('/comments')
def list_secondary():
    return records['comment']

@app.post('/comments', status_code=201)
def create_secondary(body: Record):
    key = 'comment'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get("/summary")
def summary():
    return {"ticket_count": len(records['ticket']), "comment_count": len(records['comment'])}
