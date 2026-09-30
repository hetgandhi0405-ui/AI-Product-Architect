"""
Phase 4 — Infrastructure State Agent
=======================================
Produces the canonical machine-readable infrastructure_state.json from
cloud_architecture_spec. This file is the single source of truth for:
- Phase 5 (Architecture Diagram)
- Phase 6 (Terraform generation)
- Phase 12 (RL environment state)
- Phase 13 (Self-evolution loop)

Schema:
{
  "architecture_id": "ARCH-XXXXXXXX",
  "version": "1.0",
  "project_name": "...",
  "resources": [...],
  "relationships": [...],
  "expected_metrics": {...}
}
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from backend.agents.state import AgentState


def infrastructure_state_agent(state: AgentState) -> AgentState:
    """
    Build infrastructure_state.json from cloud_architecture_spec and write it
    alongside the assembled project directory.
    """
    spec: dict = state.get("cloud_architecture_spec", {})
    project_id: str = state.get("project_id", "unknown")
    project_name: str = state.get("project_name", "generated-app")
    assembled_path: str = state.get("assembled_project_path", "")

    if not spec:
        # Graceful degradation — produce minimal stub
        state["infrastructure_state"] = {"error": "cloud_architecture_spec missing"}
        return state

    arch_id = spec.get("architecture_id", f"ARCH-{project_id[:8].upper()}")
    region = spec.get("region", "ap-south-1")
    compute = spec.get("compute", {})
    database = spec.get("database", {})
    network = spec.get("network", {})
    cache = spec.get("cache", {})
    storage = spec.get("storage", {})
    lb = spec.get("load_balancer", {})
    monitoring = spec.get("monitoring", {})
    security = spec.get("security", {})
    auth = spec.get("authentication", {})
    metrics = spec.get("estimated_metrics", {})

    # ── Build resource list ──────────────────────────────────────────────────
    resources = [
        {
            "id": "vpc-main",
            "type": "aws_vpc",
            "name": f"{project_name}-vpc",
            "config": {
                "cidr_block": "10.0.0.0/16",
                "enable_dns_hostnames": True,
                "public_subnets": network.get("public_subnets", 2),
                "private_subnets": network.get("private_subnets", 2),
                "region": region,
            },
        },
        {
            "id": "alb-main",
            "type": "aws_alb",
            "name": f"{project_name}-alb",
            "config": {
                "port": lb.get("port", 80),
                "ssl_port": lb.get("ssl_port", 443),
                "health_check_path": lb.get("health_check_path", "/health"),
                "scheme": "internet-facing",
            },
        },
        {
            "id": "compute-main",
            "type": f"aws_{compute.get('service', 'ecs_fargate')}",
            "name": f"{project_name}-app",
            "config": {
                "service": compute.get("service"),
                "instance_type": compute.get("instance_type"),
                "fargate_cpu": compute.get("fargate_cpu"),
                "fargate_memory": compute.get("fargate_memory"),
                "desired_count": compute.get("desired_count", 1),
                "autoscaling": compute.get("autoscaling", False),
                "min_count": compute.get("min_count", 1),
                "max_count": compute.get("max_count", 2),
                "port": compute.get("port", 8000),
            },
        },
        {
            "id": "rds-main",
            "type": "aws_rds",
            "name": f"{project_name}-db",
            "config": {
                "engine": database.get("engine", "postgres"),
                "instance_class": database.get("instance_class"),
                "allocated_storage_gb": database.get("allocated_storage_gb", 20),
                "multi_az": database.get("multi_az", False),
                "port": database.get("port", 5432),
                "tables": database.get("tables", []),
            },
        },
    ]

    # Optional resources
    if cache.get("enabled"):
        resources.append({
            "id": "cache-main",
            "type": "aws_elasticache",
            "name": f"{project_name}-cache",
            "config": {
                "engine": cache.get("engine", "redis"),
                "node_type": cache.get("node_type", "cache.t4g.micro"),
            },
        })

    if storage.get("enabled"):
        resources.append({
            "id": "s3-main",
            "type": "aws_s3_bucket",
            "name": f"{project_name}-assets",
            "config": {
                "purpose": storage.get("purpose", "User uploads"),
                "versioning": True,
            },
        })

    if security.get("waf"):
        resources.append({
            "id": "waf-main",
            "type": "aws_wafv2_web_acl",
            "name": f"{project_name}-waf",
            "config": {"scope": "REGIONAL"},
        })

    if auth.get("enabled"):
        resources.append({
            "id": "secrets-main",
            "type": "aws_secretsmanager_secret",
            "name": f"{project_name}-secrets",
            "config": {"purpose": "JWT secret and DB credentials"},
        })

    if monitoring.get("enabled"):
        resources.append({
            "id": "cloudwatch-main",
            "type": "aws_cloudwatch",
            "name": f"{project_name}-monitoring",
            "config": {"alarms": monitoring.get("alarms", [])},
        })

    # ── Build relationship graph ─────────────────────────────────────────────
    relationships = [
        {"from": "alb-main",     "to": "compute-main", "type": "routes_traffic_to"},
        {"from": "compute-main", "to": "rds-main",     "type": "reads_writes"},
        {"from": "vpc-main",     "to": "alb-main",     "type": "contains"},
        {"from": "vpc-main",     "to": "compute-main", "type": "contains"},
        {"from": "vpc-main",     "to": "rds-main",     "type": "contains"},
    ]
    if cache.get("enabled"):
        relationships.append({"from": "compute-main", "to": "cache-main", "type": "caches_via"})
    if storage.get("enabled"):
        relationships.append({"from": "compute-main", "to": "s3-main", "type": "stores_to"})
    if security.get("waf"):
        relationships.append({"from": "waf-main", "to": "alb-main", "type": "protects"})
    if auth.get("enabled"):
        relationships.append({"from": "compute-main", "to": "secrets-main", "type": "reads_secrets_from"})

    # ── Build canonical infrastructure_state ────────────────────────────────
    infrastructure_state = {
        "architecture_id": arch_id,
        "version": "1.0",
        "project_id": project_id,
        "project_name": project_name,
        "cloud_provider": spec.get("cloud_provider", "aws"),
        "region": region,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "resources": resources,
        "relationships": relationships,
        "expected_metrics": {
            "monthly_cost_usd": metrics.get("monthly_cost_usd", 0),
            "availability_sla": metrics.get("availability_sla", "99.9%"),
            "latency_p95_ms": metrics.get("latency_p95_ms", 250),
            "target_users": metrics.get("target_users", 1000),
        },
        "scaling_policy": {
            "autoscaling_enabled": compute.get("autoscaling", False),
            "min_instances": compute.get("min_count", 1),
            "max_instances": compute.get("max_count", 2),
            "target_cpu_percent": 70,
        },
        "security_policy": {
            "waf_enabled": security.get("waf", False),
            "tls_enabled": security.get("tls", True),
            "secrets_manager": security.get("secrets_manager", True),
        },
    }

    state["infrastructure_state"] = infrastructure_state

    # ── Write to disk alongside assembled project ────────────────────────────
    infra_path = None
    if assembled_path and os.path.isdir(assembled_path):
        infra_dir = Path(assembled_path) / "infrastructure"
        infra_dir.mkdir(parents=True, exist_ok=True)
        infra_file = infra_dir / "infrastructure_state.json"
        infra_file.write_text(json.dumps(infrastructure_state, indent=2), encoding="utf-8")
        infra_path = str(infra_file)

    state["infrastructure_state_path"] = infra_path

    # Surface into architecture dict for backward compat
    arch = state.get("architecture", {})
    arch["infrastructure_state"] = infrastructure_state
    state["architecture"] = arch

    return state
