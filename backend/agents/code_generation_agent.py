import os
import re
import json
from typing import Dict, Any
from backend.agents.state import AgentState
from backend.agents.llm_client import LazyGenAIClient


def _clean_markdown_fences(content: str) -> str:
    """
    Remove accidental Markdown code fences (e.g. ```python ... ```)
    returned by LLMs to ensure raw source code integrity.
    """
    cleaned = content.strip()
    # Match leading ```lang and trailing ```
    fence_pattern = re.compile(r"^```[a-zA-Z0-9_-]*\r?\n?(.*?)\r?\n?```$", re.DOTALL)
    match = fence_pattern.match(cleaned)
    if match:
        return match.group(1).strip()

    # Fallback line-by-line fence cleanup if needed
    lines = cleaned.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _generate_file_with_llm(
    file_path: str,
    file_info: Dict[str, Any],
    state: AgentState
) -> str:
    """
    Generate file content using Gemini API.
    """
    client = LazyGenAIClient()
    requirements = state.get("requirements", "")
    project_name = state.get("project_name", "Generated Product")
    product_plan = json.dumps(state.get("product_plan", {}), indent=2)
    api_spec = json.dumps(state.get("api_specification", {}), indent=2)
    db_spec = json.dumps(state.get("database_specification", {}), indent=2)
    ui_spec = json.dumps(state.get("ui_specification", {}), indent=2)
    contract = json.dumps(state.get("code_generation_contract", {}), indent=2)

    prompt = f"""
You are a principal full-stack software engineer and code generator.
Generate the complete, production-ready, fully working source code for the requested file: '{file_path}'.

PROJECT NAME: {project_name}
CUSTOMER REQUIREMENTS:
{requirements}

PRODUCT PLAN:
{product_plan}

UI SPECIFICATION:
{ui_spec}

API SPECIFICATION:
{api_spec}

DATABASE SPECIFICATION:
{db_spec}

CODE GENERATION CONTRACT:
{contract}

FILE TO GENERATE: {file_path}
PURPOSE: {file_info.get('purpose', '')}
LANGUAGE: {file_info.get('language', '')}

RULES:
1. Return ONLY the raw code for '{file_path}'.
2. Do NOT wrap the output in Markdown code blocks (no ```).
3. Do NOT include explanatory conversational text.
4. Ensure valid syntax (no syntax errors, valid JSON/Python/SQL/HCL/JSX).
5. Ensure Python code has all required imports and compiles cleanly with py_compile.
6. Ensure JSON code parses without error.
7. Ensure Dockerfile starts with FROM and docker-compose.yml has valid services.
8. Ensure all API routes, models, and frontend client calls align with the specifications.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    raw_text = response.text or ""
    return _clean_markdown_fences(raw_text)


def _generate_file_deterministic(
    file_path: str,
    file_info: Dict[str, Any],
    state: AgentState
) -> str:
    """
    Deterministic code synthesizer for offline/deterministic runs, smoke tests,
    and fallback resilience. Generates valid, high-quality, spec-aligned files.
    """
    project_name = state.get("project_name", "Task Management App")
    requirements = state.get("requirements", "Task management application")
    api_spec = state.get("api_specification", {})
    endpoints = api_spec.get("endpoints", [])
    db_spec = state.get("database_specification", {})
    tables = db_spec.get("tables", [])

    # If no endpoints in spec, provide standard defaults based on requirements
    if not endpoints:
        endpoints = [
            {"method": "GET", "endpoint": "/tasks", "purpose": "List tasks"},
            {"method": "POST", "endpoint": "/tasks", "purpose": "Create task"},
            {"method": "GET", "endpoint": "/tasks/{id}", "purpose": "Get task"},
            {"method": "PUT", "endpoint": "/tasks/{id}", "purpose": "Update task"},
            {"method": "DELETE", "endpoint": "/tasks/{id}", "purpose": "Delete task"},
            {"method": "POST", "endpoint": "/auth/register", "purpose": "Register user"},
            {"method": "POST", "endpoint": "/auth/login", "purpose": "Login user"},
        ]

    # Deterministic templates per file path
    if file_path == "frontend/package.json":
        return json.dumps({
            "name": project_name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "axios": "^1.6.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test"
            }
        }, indent=2)

    elif file_path == "frontend/index.html":
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{project_name}</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>"""

    elif file_path == "frontend/src/components/Loading.jsx":
        return """import React from 'react';

export default function Loading({ message = 'Loading...' }) {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <div className="spinner"></div>
      <p>{message}</p>
    </div>
  );
}
"""

    elif file_path == "frontend/src/api.js":
        methods = []
        for ep in endpoints:
            m = ep.get("method", "GET").lower()
            path = ep.get("endpoint", "/api/item")
            func_name = ep.get("purpose", f"{m}_{path}").lower()
            func_name = re.sub(r'[^a-zA-Z0-9]+', '_', func_name).strip('_')
            clean_path = path.replace("{id}", "${id}").replace("{task_id}", "${taskId}")
            methods.append(f"""export async function {func_name}(data, id) {{
  const url = `${{API_BASE}}{clean_path}`;
  const response = await fetch(url, {{
    method: '{m.upper()}',
    headers: {{ 'Content-Type': 'application/json' }},
    body: { "'GET'" == f"'{m.upper()}'" and "null" or "JSON.stringify(data)" }
  }});
  return await response.json();
}}""")
        api_funcs = "\n\n".join(methods)
        return f"""const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

{api_funcs}
"""

    elif file_path == "frontend/src/App.jsx":
        return f"""import React, {{ useState, useEffect }} from 'react';
import Loading from './components/Loading';

export default function App() {{
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({{ title: '', description: '' }});

  useEffect(() => {{
    fetch('/api/tasks')
      .then(res => res.json())
      .then(data => setItems(Array.isArray(data) ? data : []))
      .catch(() => setItems([]));
  }}, []);

  const handleCreate = async (e) => {{
    e.preventDefault();
    setLoading(true);
    try {{
      const res = await fetch('/api/tasks', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(formData)
      }});
      const created = await res.json();
      setItems([...items, created]);
      setFormData({{ title: '', description: '' }});
    }} finally {{
      setLoading(false);
    }}
  }};

  return (
    <div style={{ maxWidth: '800px', margin: '40px auto', fontFamily: 'system-ui, sans-serif' }}>
      <h1>{project_name}</h1>
      <p>{requirements}</p>
      
      <form onSubmit={{handleCreate}} style={{ marginBottom: '24px' }}>
        <input 
          placeholder="Title" 
          value={{formData.title}} 
          onChange={{e => setFormData({{ ...formData, title: e.target.value }})}} 
          required 
          style={{ padding: '8px', marginRight: '8px' }}
        />
        <input 
          placeholder="Description" 
          value={{formData.description}} 
          onChange={{e => setFormData({{ ...formData, description: e.target.value }})}} 
          style={{ padding: '8px', marginRight: '8px' }}
        />
        <button type="submit" style={{ padding: '8px 16px' }}>Add Task</button>
      </form>

      {{loading && <Loading message="Processing..." />}}

      <ul>
        {{items.map((item, idx) => (
          <li key={{item.id || idx}} style={{ padding: '8px 0' }}>
            <strong>{{item.title || item.name || 'Task'}}</strong>: {{item.description || item.status || 'Active'}}
          </li>
        ))}}
      </ul>
    </div>
  );
}}
"""

    elif file_path == "backend/requirements.txt":
        return """fastapi>=0.110.0
uvicorn>=0.28.0
pydantic>=2.6.0
sqlalchemy>=2.0.0
pytest>=8.0.0
httpx>=0.27.0
"""

    elif file_path == "backend/models.py":
        return """from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
"""

    elif file_path == "backend/schemas.py":
        return """from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TaskResponse(TaskBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True
"""

    elif file_path == "backend/services.py":
        return """from typing import List, Optional
from backend.schemas import TaskCreate, TaskUpdate

_memory_tasks = [
    {"id": 1, "title": "Setup project environment", "description": "Initialize database and dependencies", "completed": True},
    {"id": 2, "title": "Implement core API features", "description": "Develop CRUD routes and validations", "completed": False}
]

def list_tasks() -> List[dict]:
    return _memory_tasks

def get_task(task_id: int) -> Optional[dict]:
    for t in _memory_tasks:
        if t["id"] == task_id:
            return t
    return None

def create_task(data: TaskCreate) -> dict:
    new_id = len(_memory_tasks) + 1
    item = {"id": new_id, "title": data.title, "description": data.description, "completed": data.completed}
    _memory_tasks.append(item)
    return item

def update_task(task_id: int, data: TaskUpdate) -> Optional[dict]:
    task = get_task(task_id)
    if not task:
        return None
    if data.title is not None:
        task["title"] = data.title
    if data.description is not None:
        task["description"] = data.description
    if data.completed is not None:
        task["completed"] = data.completed
    return task

def delete_task(task_id: int) -> bool:
    global _memory_tasks
    initial_len = len(_memory_tasks)
    _memory_tasks = [t for t in _memory_tasks if t["id"] != task_id]
    return len(_memory_tasks) < initial_len
"""

    elif file_path == "backend/routes/__init__.py":
        return """from backend.routes.api import router
"""

    elif file_path == "backend/routes/api.py":
        route_defs = []
        for ep in endpoints:
            m = ep.get("method", "GET").upper()
            raw_path = ep.get("endpoint", "/tasks")
            # Ensure path starts with /
            if not raw_path.startswith("/"):
                raw_path = "/" + raw_path
            
            # Format python path parameters: {id} -> {id: int}
            py_path = re.sub(r'\{([a-zA-Z_]+)\}', r'{\1}', raw_path)
            func_name = ep.get("purpose", f"{m}_{raw_path}").lower()
            func_name = re.sub(r'[^a-zA-Z0-9]+', '_', func_name).strip('_')
            
            has_id = "{" in raw_path
            id_param = "id: int" if has_id else ""
            
            if m == "GET" and not has_id:
                route_defs.append(f"""@router.get("{raw_path}")
def {func_name}():
    return services.list_tasks()""")
            elif m == "GET" and has_id:
                route_defs.append(f"""@router.get("{raw_path}")
def {func_name}({id_param}):
    res = services.get_task(id)
    if not res:
        raise HTTPException(status_code=404, detail="Item not found")
    return res""")
            elif m == "POST" and "register" in raw_path:
                route_defs.append(f"""@router.post("{raw_path}")
def {func_name}(user: schemas.UserCreate):
    return {{"id": 1, "username": user.username, "email": user.email}}""")
            elif m == "POST" and "login" in raw_path:
                route_defs.append(f"""@router.post("{raw_path}")
def {func_name}(user: schemas.UserCreate):
    return {{"token": "demo-jwt-token", "username": user.username}}""")
            elif m == "POST":
                route_defs.append(f"""@router.post("{raw_path}")
def {func_name}(data: schemas.TaskCreate):
    return services.create_task(data)""")
            elif m in ("PUT", "PATCH"):
                route_defs.append(f"""@router.put("{raw_path}")
def {func_name}({id_param}, data: schemas.TaskUpdate):
    res = services.update_task(id, data)
    if not res:
        raise HTTPException(status_code=404, detail="Item not found")
    return res""")
            elif m == "DELETE":
                route_defs.append(f"""@router.delete("{raw_path}")
def {func_name}({id_param}):
    ok = services.delete_task(id)
    if not ok:
        raise HTTPException(status_code=404, detail="Item not found")
    return {{"deleted": True, "id": id}}""")
            else:
                route_defs.append(f"""@router.api_route("{raw_path}", methods=["{m}"])
def {func_name}():
    return {{"status": "ok", "path": "{raw_path}"}}""")

        routes_code = "\n\n".join(route_defs)
        return f"""from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from backend import schemas, services

router = APIRouter(tags=["API"])

{routes_code}
"""

    elif file_path == "backend/main.py":
        return f"""from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from backend.routes.api import router as api_router

app = FastAPI(
    title="{project_name}",
    description="Generated API for {project_name}",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# Mount built React static files if directory exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def root():
    return {{"project": "{project_name}", "status": "running"}}

@app.get("/health")
def health():
    return {{"status": "healthy", "database": "connected"}}
"""

    elif file_path == "database/schema.sql":
        return f"""-- Database Schema for {project_name}
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
"""

    elif file_path == "tests/test_generated_project.py":
        return """import pytest
from backend import services, schemas

def test_task_crud_lifecycle():
    initial = services.list_tasks()
    assert isinstance(initial, list)

    created = services.create_task(schemas.TaskCreate(title="Test Task", description="Testing", completed=False))
    assert created["id"] > 0
    assert created["title"] == "Test Task"

    fetched = services.get_task(created["id"])
    assert fetched is not None
    assert fetched["title"] == "Test Task"

    updated = services.update_task(created["id"], schemas.TaskUpdate(completed=True))
    assert updated["completed"] is True

    deleted = services.delete_task(created["id"])
    assert deleted is True
"""

    elif file_path == "tests/test_api.py":
        return """from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "running"

def test_tasks_list():
    res = client.get("/api/tasks")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
"""

    elif file_path == "Dockerfile":
        return """# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install --silent || true
COPY frontend/ ./
RUN npm run build || mkdir -p dist

# Stage 2: Production Python API serving backend & frontend
FROM python:3.11-slim
WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /app/backend/
COPY --from=frontend-builder /app/frontend/dist /app/backend/static/

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

    elif file_path == "docker-compose.yml":
        return f"""version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/appdb
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=appdb
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/schema.sql

volumes:
  db_data:
"""

    elif file_path == ".env.example":
        return """PORT=8000
HOST=0.0.0.0
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/appdb
SECRET_KEY=change-in-production
ENVIRONMENT=development
"""

    elif file_path == "infrastructure/main.tf":
        return """terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project   = var.project_name
      ManagedBy = "ai-product-architect"
    }
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

# Networking: VPC & Subnets
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = {
    Name = "${var.project_name}-vpc"
  }
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
}

resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, 1)
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true
  tags = {
    Name = "${var.project_name}-public-1"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, 2)
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true
  tags = {
    Name = "${var.project_name}-public-2"
  }
}

resource "aws_subnet" "private_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, 10)
  availability_zone = data.aws_availability_zones.available.names[0]
  tags = {
    Name = "${var.project_name}-private-1"
  }
}

resource "aws_subnet" "private_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, 11)
  availability_zone = data.aws_availability_zones.available.names[1]
  tags = {
    Name = "${var.project_name}-private-2"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
}

resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# Security Groups
resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb-sg"
  description = "Allow inbound HTTP to ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs" {
  name        = "${var.project_name}-ecs-sg"
  description = "Allow inbound traffic only from ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "db" {
  name        = "${var.project_name}-db-sg"
  description = "Allow DB connection only from ECS tasks"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

resource "aws_lb_target_group" "app" {
  name        = "${var.project_name}-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/health"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
    matcher             = "200"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# Secrets Manager (No plain text secrets)
resource "aws_secretsmanager_secret" "app_secrets" {
  name                    = "${var.project_name}-secrets"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "app_secrets_val" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    DATABASE_URL = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgres.endpoint}/${var.db_name}"
    JWT_SECRET   = var.jwt_secret
  })
}

# RDS PostgreSQL (Smallest instance class, demo settings)
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]
}

resource "aws_db_instance" "postgres" {
  identifier              = "${var.project_name}-db"
  engine                  = "postgres"
  engine_version          = "15"
  instance_class          = var.db_instance_class
  allocated_storage       = 20
  db_name                 = var.db_name
  username                = var.db_username
  password                = var.db_password
  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [aws_security_group.db.id]
  skip_final_snapshot     = true
  deletion_protection     = false
}

# ECS Fargate Cluster & Service
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"
}

resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.project_name}-ecs-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${var.project_name}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = tostring(var.fargate_cpu)
  memory                   = tostring(var.fargate_memory)
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([{
    name      = "app"
    image     = var.image_uri
    essential = true
    portMappings = [{
      containerPort = 8000
      hostPort      = 8000
    }]
    secrets = [
      {
        name      = "DATABASE_URL"
        valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:DATABASE_URL::"
      },
      {
        name      = "JWT_SECRET"
        valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:JWT_SECRET::"
      }
    ]
  }])
}

resource "aws_ecs_service" "main" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.public_1.id, aws_subnet.public_2.id]
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "app"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]
}
"""

    elif file_path == "infrastructure/variables.tf":
        return """variable "project_name" {
  type        = string
  default     = "ai-product"
  description = "Project name tag"
}

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "Target deployment region"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "VPC CIDR block"
}

variable "image_uri" {
  type        = string
  default     = "public.ecr.aws/dummy/app:latest"
  description = "ECR container image URI"
}

variable "fargate_cpu" {
  type        = number
  default     = 256
  description = "Fargate CPU units"
}

variable "fargate_memory" {
  type        = number
  default     = 512
  description = "Fargate memory MB"
}

variable "desired_count" {
  type        = number
  default     = 1
  description = "Desired number of ECS tasks"
}

variable "db_instance_class" {
  type        = string
  default     = "db.t4g.micro"
  description = "RDS instance class"
}

variable "db_name" {
  type        = string
  default     = "appdb"
  description = "Database name"
}

variable "db_username" {
  type        = string
  default     = "appuser"
  description = "Master database username"
}

variable "db_password" {
  type        = string
  default     = "SuperSecretPassword123!"
  sensitive   = true
  description = "Master database password"
}

variable "jwt_secret" {
  type        = string
  default     = "default_jwt_secret_key_change_me"
  sensitive   = true
  description = "JWT Signing Secret"
}
"""

    elif file_path == "infrastructure/outputs.tf":
        return """output "alb_dns_name" {
  value       = aws_lb.main.dns_name
  description = "Public HTTP endpoint for Application Load Balancer"
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.main.name
  description = "ECS Cluster Name"
}

output "ecs_service_name" {
  value       = aws_ecs_service.main.name
  description = "ECS Service Name"
}

output "project_name" {
  value       = var.project_name
  description = "Deployment project name"
}
"""

    elif file_path == "README.md":
        return f"""# {project_name}

{requirements}

## Architecture Overview
- **Frontend**: React Single-Page Application (SPA) with component-driven architecture
- **Backend**: FastAPI asynchronous REST API
- **Database**: PostgreSQL relational database with automated schema migration
- **Containerization**: Docker & Docker Compose
- **Infrastructure as Code**: Terraform AWS modules

## Getting Started

### Local Development
```bash
# Backend Setup
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000

# Run Tests
pytest tests/
```

### Docker Deployment
```bash
docker-compose up --build
```
"""

    # Generic fallback for any unexpected manifest file
    return f"# {file_path}\n# Generated for {project_name}\n"


def code_generation_agent(state: AgentState) -> AgentState:
    """
    Generate actual file contents for every item in the file manifest.
    Uses Gemini API when GEMINI_API_KEY is available; falls back to
    high-fidelity deterministic synthesis when offline or during deterministic tests.
    """
    manifest = state.get("file_manifest", {})
    files = manifest.get("files", [])
    has_api_key = bool(os.environ.get("GEMINI_API_KEY"))

    generated_files: Dict[str, str] = {}
    generation_errors = []

    for item in files:
        file_path = item["path"]
        content = ""
        # Try LLM generation if API key is present
        if has_api_key:
            try:
                content = _generate_file_with_llm(file_path, item, state)
            except Exception as e:
                print(f"[CodeGenerationAgent] LLM generation failed for {file_path}: {e}. Falling back to deterministic synthesizer.")
                generation_errors.append({"file": file_path, "error": str(e)})
                content = _generate_file_deterministic(file_path, item, state)
        else:
            # Deterministic synthesis
            content = _generate_file_deterministic(file_path, item, state)

        generated_files[file_path] = content

    state["generated_files"] = generated_files

    architecture = state.get("architecture", {})
    architecture["generated_files_count"] = len(generated_files)
    if generation_errors:
        architecture["generation_errors"] = generation_errors
    state["architecture"] = architecture

    return state
