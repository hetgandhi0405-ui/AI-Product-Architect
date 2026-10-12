from datetime import datetime
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title='Personal Finance Tracker', version="0.1.0", description='income, expenses, budgets, owner-scoped summaries')
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

records: dict[str, list[dict[str, Any]]] = {'transaction': [], 'budget': []}
counters = {'transaction': 1, 'budget': 1}

class Record(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = ""

@app.get("/health")
def health():
    return {"status": "ok", "project": 'personal-finance', "mode": "development-prototype"}

@app.get('/transactions')
def list_primary():
    return records['transaction']

@app.post('/transactions', status_code=201)
def create_primary(body: Record):
    key = 'transaction'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get('/budgets')
def list_secondary():
    return records['budget']

@app.post('/budgets', status_code=201)
def create_secondary(body: Record):
    key = 'budget'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get("/summary")
def summary():
    return {"transaction_count": len(records['transaction']), "budget_count": len(records['budget'])}
