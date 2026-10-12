from datetime import datetime
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title='Website Uptime Monitoring Platform', version="0.1.0", description='HTTP(S) monitor registration, synthetic check results, uptime history; no live check by default')
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

records: dict[str, list[dict[str, Any]]] = {'monitor': [], 'checkresult': []}
counters = {'monitor': 1, 'checkresult': 1}

class Record(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = ""

@app.get("/health")
def health():
    return {"status": "ok", "project": 'website-uptime-monitor', "mode": "development-prototype"}

@app.get('/monitors')
def list_primary():
    return records['monitor']

@app.post('/monitors', status_code=201)
def create_primary(body: Record):
    key = 'monitor'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get('/checks')
def list_secondary():
    return records['checkresult']

@app.post('/checks', status_code=201)
def create_secondary(body: Record):
    key = 'checkresult'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get("/summary")
def summary():
    return {"monitor_count": len(records['monitor']), "checkresult_count": len(records['checkresult'])}
