from datetime import datetime
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title='Hospital Appointment Management System', version="0.1.0", description='providers, appointment booking, cancellation, schedule conflict checks; synthetic data only')
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

records: dict[str, list[dict[str, Any]]] = {'provider': [], 'appointment': []}
counters = {'provider': 1, 'appointment': 1}

class Record(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = ""

@app.get("/health")
def health():
    return {"status": "ok", "project": 'hospital-appointments', "mode": "development-prototype"}

@app.get('/providers')
def list_primary():
    return records['provider']

@app.post('/providers', status_code=201)
def create_primary(body: Record):
    key = 'provider'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get('/appointments')
def list_secondary():
    return records['appointment']

@app.post('/appointments', status_code=201)
def create_secondary(body: Record):
    key = 'appointment'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get("/summary")
def summary():
    return {"provider_count": len(records['provider']), "appointment_count": len(records['appointment'])}
