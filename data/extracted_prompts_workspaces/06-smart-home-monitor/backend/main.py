from datetime import datetime
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title='Smart Home Monitoring Dashboard', version="0.1.0", description='devices, states, sensor readings; simulated readings are labelled')
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

records: dict[str, list[dict[str, Any]]] = {'device': [], 'reading': []}
counters = {'device': 1, 'reading': 1}

class Record(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = ""

@app.get("/health")
def health():
    return {"status": "ok", "project": 'smart-home-monitor', "mode": "development-prototype"}

@app.get('/devices')
def list_primary():
    return records['device']

@app.post('/devices', status_code=201)
def create_primary(body: Record):
    key = 'device'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get('/readings')
def list_secondary():
    return records['reading']

@app.post('/readings', status_code=201)
def create_secondary(body: Record):
    key = 'reading'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get("/summary")
def summary():
    return {"device_count": len(records['device']), "reading_count": len(records['reading'])}
