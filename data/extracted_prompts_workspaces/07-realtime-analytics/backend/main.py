from datetime import datetime
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title='Real-Time Analytics Dashboard', version="0.1.0", description='event ingestion, event listing, aggregated metrics, synthetic demo data')
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

records: dict[str, list[dict[str, Any]]] = {'event': [], 'metric': []}
counters = {'event': 1, 'metric': 1}

class Record(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = ""

@app.get("/health")
def health():
    return {"status": "ok", "project": 'realtime-analytics', "mode": "development-prototype"}

@app.get('/events')
def list_primary():
    return records['event']

@app.post('/events', status_code=201)
def create_primary(body: Record):
    key = 'event'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get('/metrics')
def list_secondary():
    return records['metric']

@app.post('/metrics', status_code=201)
def create_secondary(body: Record):
    key = 'metric'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get("/summary")
def summary():
    return {"event_count": len(records['event']), "metric_count": len(records['metric'])}
