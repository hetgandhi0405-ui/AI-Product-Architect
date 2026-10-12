from datetime import datetime
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title='Employee Attendance Management System', version="0.1.0", description='clock-in/out, attendance history, leave requests')
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

records: dict[str, list[dict[str, Any]]] = {'attendance': [], 'leaverequest': []}
counters = {'attendance': 1, 'leaverequest': 1}

class Record(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = ""

@app.get("/health")
def health():
    return {"status": "ok", "project": 'employee-attendance', "mode": "development-prototype"}

@app.get('/attendance')
def list_primary():
    return records['attendance']

@app.post('/attendance', status_code=201)
def create_primary(body: Record):
    key = 'attendance'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get('/leave-requests')
def list_secondary():
    return records['leaverequest']

@app.post('/leave-requests', status_code=201)
def create_secondary(body: Record):
    key = 'leaverequest'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get("/summary")
def summary():
    return {"attendance_count": len(records['attendance']), "leaverequest_count": len(records['leaverequest'])}
