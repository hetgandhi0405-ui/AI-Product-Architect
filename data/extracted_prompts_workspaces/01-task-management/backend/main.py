from datetime import datetime
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title='Task Management Platform', version="0.1.0", description='projects, tasks, priorities, due dates, status, summary metrics')
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

records: dict[str, list[dict[str, Any]]] = {'project': [], 'task': []}
counters = {'project': 1, 'task': 1}

class Record(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = ""

@app.get("/health")
def health():
    return {"status": "ok", "project": 'task-management', "mode": "development-prototype"}

@app.get('/projects')
def list_primary():
    return records['project']

@app.post('/projects', status_code=201)
def create_primary(body: Record):
    key = 'project'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get('/tasks')
def list_secondary():
    return records['task']

@app.post('/tasks', status_code=201)
def create_secondary(body: Record):
    key = 'task'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get("/summary")
def summary():
    return {"project_count": len(records['project']), "task_count": len(records['task'])}
