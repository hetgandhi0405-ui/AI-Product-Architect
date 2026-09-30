"""
Phase 1 — Product Metadata Extractor
======================================
After the code generation pipeline assembles the project, this agent
inspects the ACTUAL generated product metadata (not just the user prompt)
and extracts structured product metadata for use in Phase 3 (Cloud Architecture).

Extracted metadata drives:
- Cloud architecture spec (Phase 3)
- Infrastructure state (Phase 4)
- Terraform generation (Phase 6)
"""
from __future__ import annotations

import os
import json
import re
from pathlib import Path

from backend.agents.state import AgentState


def product_metadata_agent(state: AgentState) -> AgentState:
    """
    Inspect the actual generated product to extract structured metadata:
    frontend tech, backend tech, database requirements, ports, auth, scale.
    """
    generated_files: dict = state.get("generated_files", {})
    product_plan: dict = state.get("product_plan", {})
    requirements: str = state.get("requirements", "")
    database_spec: dict = state.get("database_specification", {})
    api_spec: dict = state.get("api_specification", {})

    # ── Detect frontend framework ────────────────────────────────────────────
    frontend_framework = "react"
    if "frontend/package.json" in generated_files:
        pkg = generated_files["frontend/package.json"]
        if "vue" in pkg.lower():
            frontend_framework = "vue"
        elif "angular" in pkg.lower():
            frontend_framework = "angular"
        elif "svelte" in pkg.lower():
            frontend_framework = "svelte"

    # ── Detect backend framework / language ─────────────────────────────────
    backend_framework = "fastapi"
    backend_language = "python"
    if "backend/main.py" in generated_files:
        main_py = generated_files["backend/main.py"]
        if "flask" in main_py.lower():
            backend_framework = "flask"
        elif "django" in main_py.lower():
            backend_framework = "django"
    elif "backend/server.js" in generated_files or "package.json" in " ".join(generated_files.keys()):
        backend_framework = "express"
        backend_language = "nodejs"

    # ── Detect database engine ───────────────────────────────────────────────
    db_engine = "postgresql"
    req_lower = requirements.lower()
    if "mysql" in req_lower:
        db_engine = "mysql"
    elif "mongodb" in req_lower or "mongo" in req_lower:
        db_engine = "mongodb"
    elif "sqlite" in req_lower:
        db_engine = "sqlite"

    tables = database_spec.get("tables", [])
    table_names = [
        (t if isinstance(t, str) else t.get("name", ""))
        for t in tables
    ]

    # ── Detect auth ──────────────────────────────────────────────────────────
    has_auth = any(
        keyword in req_lower
        for keyword in ["login", "register", "auth", "jwt", "password", "user"]
    )

    # ── Detect scale targets ─────────────────────────────────────────────────
    target_users = 1000
    user_match = re.search(r"(\d[\d,]*)\s*users?", req_lower)
    if user_match:
        target_users = int(user_match.group(1).replace(",", ""))

    high_availability = any(
        kw in req_lower
        for kw in ["high availability", "ha", "multi-az", "multi az", "fault tolerant", "99.9"]
    )

    # ── Detect caching need ──────────────────────────────────────────────────
    needs_cache = (
        target_users >= 5000
        or "cache" in req_lower
        or "redis" in req_lower
        or "performance" in req_lower
    )

    # ── Detect file/object storage need ─────────────────────────────────────
    needs_storage = any(
        kw in req_lower
        for kw in ["upload", "file", "image", "attachment", "s3", "storage", "media"]
    )

    # ── Detect ports from generated Dockerfile / compose ────────────────────
    ports = [8000]
    if "docker-compose.yml" in generated_files:
        compose = generated_files["docker-compose.yml"]
        port_matches = re.findall(r'["\']?(\d{2,5}):(\d{2,5})["\']?', compose)
        ports = list({int(p[1]) for p in port_matches if int(p[1]) < 65535}) or [8000]

    # ── Detect API endpoints ─────────────────────────────────────────────────
    api_endpoints = []
    if api_spec:
        api_endpoints = api_spec.get("endpoints", [])

    # ── Compute recommended instance tier ───────────────────────────────────
    if target_users < 1000:
        instance_tier = "small"       # t3.micro / db.t4g.micro
    elif target_users < 10000:
        instance_tier = "medium"      # t3.medium / db.t3.medium
    else:
        instance_tier = "large"       # m5.large / db.r5.large

    product_metadata = {
        "frontend": {
            "framework": frontend_framework,
            "port": 3000,
            "build_tool": "npm",
            "static_hosting": True,
        },
        "backend": {
            "framework": backend_framework,
            "language": backend_language,
            "port": ports[0] if ports else 8000,
            "ports": ports,
            "api_endpoints": len(api_endpoints),
        },
        "database": {
            "engine": db_engine,
            "tables": table_names,
            "table_count": len(table_names),
            "port": 5432 if db_engine == "postgresql" else 3306,
        },
        "authentication": {
            "required": has_auth,
            "mechanism": "jwt" if has_auth else "none",
        },
        "scalability": {
            "target_users": target_users,
            "high_availability": high_availability,
            "instance_tier": instance_tier,
            "needs_cache": needs_cache,
            "needs_storage": needs_storage,
        },
        "containerization": {
            "docker": "Dockerfile" in generated_files,
            "compose": "docker-compose.yml" in generated_files,
        },
        "generated_files_count": len(generated_files),
    }

    state["product_metadata"] = product_metadata

    # Also surface into architecture dict for backward-compat
    arch = state.get("architecture", {})
    arch["product_metadata"] = product_metadata
    state["architecture"] = arch

    return state
