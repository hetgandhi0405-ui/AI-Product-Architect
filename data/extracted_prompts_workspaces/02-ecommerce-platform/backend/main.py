from datetime import datetime
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title='E-Commerce Platform', version="0.1.0", description='product catalog, stock, development-mode orders, order history; never collect card details')
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

records: dict[str, list[dict[str, Any]]] = {'product': [], 'order': []}
counters = {'product': 1, 'order': 1}

class Record(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = ""

@app.get("/health")
def health():
    return {"status": "ok", "project": 'ecommerce-platform', "mode": "development-prototype"}

@app.get('/products')
def list_primary():
    return records['product']

@app.post('/products', status_code=201)
def create_primary(body: Record):
    key = 'product'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get('/orders')
def list_secondary():
    return records['order']

@app.post('/orders', status_code=201)
def create_secondary(body: Record):
    key = 'order'
    item = {"id": counters[key], **body.model_dump(), "created_at": datetime.utcnow().isoformat()}
    counters[key] += 1
    records[key].append(item)
    return item

@app.get("/summary")
def summary():
    return {"product_count": len(records['product']), "order_count": len(records['order'])}
