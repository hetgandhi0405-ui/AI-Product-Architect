from datetime import datetime, timezone
from typing import Any, Dict

from backend.agents.state import AgentState


def monitoring_agent(state: AgentState) -> AgentState:
    """
    Collect and normalize infrastructure monitoring metrics.

    The agent accepts optional runtime metrics from:
        state["architecture"]["monitoring_metrics"]

    If metrics are not supplied, it records a safe baseline state.
    No real infrastructure is modified by this agent.
    """

    architecture = state.get("architecture", {})
    infrastructure = architecture.get("infrastructure", {})

    metrics = architecture.get("monitoring_metrics", {})

    monitoring = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": infrastructure.get("provider", "AWS"),
        "status": "healthy",
        "metrics": {
            "cpu_utilization": metrics.get("cpu_utilization"),
            "memory_utilization": metrics.get("memory_utilization"),
            "disk_utilization": metrics.get("disk_utilization"),
            "network_utilization": metrics.get("network_utilization"),
            "request_rate": metrics.get("request_rate"),
            "latency_ms": metrics.get("latency_ms"),
            "error_rate": metrics.get("error_rate"),
            "database_utilization": metrics.get("database_utilization"),
        },
        "resources_monitored": [
            resource.get("type")
            for resource in infrastructure.get("resources", [])
            if resource.get("type")
        ],
        "data_source": (
            "runtime_metrics"
            if metrics
            else "baseline"
        ),
    }

    architecture["monitoring"] = monitoring
    state["architecture"] = architecture

    return state
