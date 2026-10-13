from datetime import datetime
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title='Student Learning Management System', version="0.1.0", description='courses, enrollments, assignments, progress tracking')
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

records: dict[str, list[dict[str, Any]]] = {'course': [], 'enrollment': []}
counters = {'course': 1, 'enrollment': 1}

class Record(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = ""

@app.get("/health")
def health():
    return {"status": "ok", "project": 'student-lms', "mode": "development-prototype"}

@app.get('/courses')
def list_primary():
    return records['course']

@app.post('/courses', status_code=201)
def create_primary(body: Record):
    key = 'course'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get('/enrollments')
def list_secondary():
    return records['enrollment']

@app.post('/enrollments', status_code=201)
def create_secondary(body: Record):
    key = 'enrollment'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get("/summary")
def summary():
    return {"course_count": len(records['course']), "enrollment_count": len(records['enrollment'])}
