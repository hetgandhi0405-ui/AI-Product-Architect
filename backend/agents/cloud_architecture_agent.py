"""
Phase 3 — Cloud Architecture Generation
==========================================
Generates a dynamic, structured cloud architecture specification
by analyzing the ACTUAL generated product metadata (not just the user prompt).

Output: cloud_architecture_spec — used by Phase 4 (Infrastructure State) and
        Phase 6 (Terraform generation).

Architecture is NOT hardcoded — it adapts to the product:
- Small apps → single t3.small + RDS t4g.micro
- Medium apps → ASG + multi-AZ RDS
- Large/HA apps → multi-AZ ECS Fargate + RDS r5 + ElastiCache Redis
"""
from __future__ import annotations

import uuid
from backend.agents.state import AgentState


def cloud_architecture_agent(state: AgentState) -> AgentState:
    """
    Analyze product_metadata and generate a canonical cloud_architecture_spec.
    """
    meta: dict = state.get("product_metadata", {})
    requirements: str = state.get("requirements", "")
    project_name: str = state.get("project_name", "generated-app")

    # Pull scalability settings
    scalability = meta.get("scalability", {})
    target_users: int = scalability.get("target_users", 1000)
    high_availability: bool = scalability.get("high_availability", False)
    instance_tier: str = scalability.get("instance_tier", "medium")
    needs_cache: bool = scalability.get("needs_cache", False)
    needs_storage: bool = scalability.get("needs_storage", False)

    # Pull component info
    backend = meta.get("backend", {})
    db = meta.get("database", {})
    auth = meta.get("authentication", {})
    containerized = meta.get("containerization", {}).get("docker", False)

    # ── Compute tier configuration ───────────────────────────────────────────
    TIERS = {
        "small":  {"ec2": "t3.small",  "fargate_cpu": 256,  "fargate_memory": 512,  "rds": "db.t4g.micro",  "desired_count": 1},
        "medium": {"ec2": "t3.medium", "fargate_cpu": 512,  "fargate_memory": 1024, "rds": "db.t3.medium",  "desired_count": 2},
        "large":  {"ec2": "m5.large",  "fargate_cpu": 1024, "fargate_memory": 2048, "rds": "db.r5.large",   "desired_count": 3},
    }
    tier = TIERS.get(instance_tier, TIERS["medium"])

    # ── Choose compute service ────────────────────────────────────────────────
    compute_service = "ecs_fargate" if containerized else "ec2"

    # ── DB engine mapping ──────────────────────────────────────────────────
    db_engine = db.get("engine", "postgresql")
    rds_engine_map = {
        "postgresql": "postgres",
        "mysql": "mysql",
        "sqlite": "postgres",   # sqlite → postgres in cloud
        "mongodb": "postgres",  # mongo → use postgres for RDS; note limitation
    }
    rds_engine = rds_engine_map.get(db_engine, "postgres")

    # ── Build cloud_architecture_spec ────────────────────────────────────────
    spec: dict = {
        "architecture_id": f"ARCH-{uuid.uuid4().hex[:8].upper()}",
        "cloud_provider": "aws",
        "region": "ap-south-1",
        "project_name": project_name.lower().replace(" ", "-"),

        "network": {
            "vpc": True,
            "public_subnets": 2,
            "private_subnets": 2 if high_availability else 1,
            "nat_gateway": True,
            "internet_gateway": True,
        },

        "compute": {
            "service": compute_service,
            "instance_type": tier["ec2"],
            "fargate_cpu": tier["fargate_cpu"],
            "fargate_memory": tier["fargate_memory"],
            "desired_count": tier["desired_count"],
            "autoscaling": high_availability or target_users >= 5000,
            "min_count": 1,
            "max_count": tier["desired_count"] * 2 if high_availability else tier["desired_count"],
            "port": backend.get("port", 8000),
        },

        "load_balancer": {
            "service": "alb",
            "enabled": True,
            "port": 80,
            "ssl_port": 443,
            "health_check_path": "/health",
        },

        "database": {
            "service": "rds",
            "engine": rds_engine,
            "instance_class": tier["rds"],
            "allocated_storage_gb": 20,
            "multi_az": high_availability,
            "port": db.get("port", 5432),
            "tables": db.get("tables", []),
        },

        "cache": {
            "service": "elasticache" if needs_cache else "none",
            "engine": "redis" if needs_cache else "none",
            "node_type": "cache.t4g.micro" if needs_cache else "none",
            "enabled": needs_cache,
        },

        "storage": {
            "service": "s3" if needs_storage else "none",
            "enabled": needs_storage,
            "purpose": "User uploads and static assets" if needs_storage else "none",
        },

        "authentication": {
            "service": "secrets_manager",
            "method": auth.get("mechanism", "jwt"),
            "enabled": auth.get("required", False),
        },

        "monitoring": {
            "service": "cloudwatch",
            "enabled": True,
            "alarms": ["CPUUtilization", "HTTPErrors", "DatabaseConnections"],
        },

        "security": {
            "waf": high_availability or target_users >= 10000,
            "security_groups": True,
            "secrets_manager": True,
            "tls": True,
        },

        "estimated_metrics": {
            "monthly_cost_usd": _estimate_cost(tier, needs_cache, needs_storage, high_availability),
            "availability_sla": "99.99%" if high_availability else "99.9%",
            "latency_p95_ms": 150 if needs_cache else 250,
            "target_users": target_users,
        },
    }

    state["cloud_architecture_spec"] = spec

    # Surface into architecture dict for backward compat
    arch = state.get("architecture", {})
    arch["cloud_architecture_spec"] = spec
    state["architecture"] = arch

    return state


def _estimate_cost(tier: dict, cache: bool, storage: bool, ha: bool) -> float:
    """Simple cost estimator based on selected tier."""
    base = {
        "t3.small":  25.0,
        "t3.medium": 40.0,
        "m5.large":  75.0,
    }.get(tier["ec2"], 40.0)

    rds = {
        "db.t4g.micro":  14.0,
        "db.t3.medium":  55.0,
        "db.r5.large":   120.0,
    }.get(tier["rds"], 14.0)

    alb = 20.0
    cache_cost = 15.0 if cache else 0.0
    storage_cost = 5.0 if storage else 0.0
    ha_multiplier = 1.8 if ha else 1.0

    return round((base + rds + alb + cache_cost + storage_cost) * ha_multiplier, 2)
