from typing import Any, Dict

from backend.agents.state import AgentState


def _add_failure(
    failures: list,
    failure_type: str,
    severity: str,
    component: str,
    evidence: Dict[str, Any],
    recommended_action: str,
) -> None:
    failures.append(
        {
            "failure_type": failure_type,
            "severity": severity,
            "affected_component": component,
            "evidence": evidence,
            "recommended_action": recommended_action,
        }
    )


def failure_detection_agent(state: AgentState) -> AgentState:
    """
    Detect infrastructure failures from the monitoring report.

    This agent is analysis-only:
    it detects problems and recommends a recovery action,
    but it never modifies real infrastructure.
    """

    architecture = state.get("architecture", {})
    monitoring = architecture.get("monitoring", {})
    metrics = monitoring.get("metrics", {})

    failures = []

    cpu = metrics.get("cpu_utilization")
    memory = metrics.get("memory_utilization")
    disk = metrics.get("disk_utilization")
    network = metrics.get("network_utilization")
    latency = metrics.get("latency_ms")
    error_rate = metrics.get("error_rate")
    database = metrics.get("database_utilization")

    if cpu is not None and cpu >= 90:
        _add_failure(
            failures,
            "cpu_overload",
            "high" if cpu < 97 else "critical",
            "compute",
            {"cpu_utilization": cpu},
            "scale_compute",
        )

    if memory is not None and memory >= 90:
        _add_failure(
            failures,
            "memory_exhaustion",
            "high" if memory < 97 else "critical",
            "compute",
            {"memory_utilization": memory},
            "increase_memory_or_scale",
        )

    if disk is not None and disk >= 90:
        _add_failure(
            failures,
            "disk_saturation",
            "high" if disk < 97 else "critical",
            "storage",
            {"disk_utilization": disk},
            "increase_storage_or_cleanup",
        )

    if network is not None and network >= 90:
        _add_failure(
            failures,
            "network_saturation",
            "high" if network < 97 else "critical",
            "networking",
            {"network_utilization": network},
            "scale_network_capacity",
        )

    if latency is not None and latency >= 500:
        _add_failure(
            failures,
            "high_latency",
            "high" if latency < 1000 else "critical",
            "backend",
            {"latency_ms": latency},
            "scale_backend_or_optimize_bottleneck",
        )

    if error_rate is not None and error_rate >= 5:
        _add_failure(
            failures,
            "high_error_rate",
            "high" if error_rate < 10 else "critical",
            "backend",
            {"error_rate": error_rate},
            "investigate_service_and_dependencies",
        )

    if database is not None and database >= 90:
        _add_failure(
            failures,
            "database_saturation",
            "high" if database < 97 else "critical",
            "database",
            {"database_utilization": database},
            "scale_database_or_add_replica",
        )

    failure_detected = bool(failures)

    detection = {
        "failure_detected": failure_detected,
        "failure_count": len(failures),
        "failures": failures,
        "status": "failure_detected" if failure_detected else "healthy",
    }

    architecture["failure_detection"] = detection
    state["architecture"] = architecture

    return state
