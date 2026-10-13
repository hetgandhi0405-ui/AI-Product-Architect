from typing import Any, Dict, List, Optional
from backend.agents.state import AgentState


def reliability_agent(state: AgentState) -> AgentState:
    """
    Evaluates system reliability from health checks, healthy host counts, and 5XX error rates.
    Rule: Availability is computed only if the observation window is sufficient;
    otherwise availability = null and status = INSUFFICIENT_DATA.

    Vocabulary: HEALTHY | DEGRADED | UNHEALTHY | INSUFFICIENT_DATA
    """
    deploy_mode = state.get("deploy_mode", "dry-run")
    telemetry = state.get("telemetry_data", {})
    metrics = telemetry.get("metrics", {})
    synthetic = telemetry.get("synthetic", {})
    cloudwatch = telemetry.get("cloudwatch", {})
    window = synthetic.get("window") or cloudwatch.get("window") or "none"

    deployment_val_status = state.get("deployment_validation_status", "SKIPPED")
    health_status = state.get("health_status", "INSUFFICIENT_DATA")

    # In dry-run or if deployment validation was not performed
    if deploy_mode == "dry-run" or deployment_val_status in ("SKIPPED", "UNAVAILABLE"):
        state["reliability_analysis"] = {
            "status": "INSUFFICIENT_DATA",
            "availability": None,
            "observation_window": "none",
            "detected_issues": [],
            "healthy_hosts": 0,
            "http_5xx_count": 0,
            "note": "no runtime observation window (dry-run or unvalidated)",
        }
        return state

    if deployment_val_status == "FAILED":
        state["reliability_analysis"] = {
            "status": "UNHEALTHY",
            "availability": 0.0,
            "observation_window": window,
            "detected_issues": state.get("validation_errors", ["Deployment health check failed"]),
            "healthy_hosts": 0,
            "http_5xx_count": metrics.get("error_count", 1),
            "note": "Deployment validation failed",
        }
        return state

    # If window is insufficient
    if window in ("none", "instant", "") or not metrics:
        state["reliability_analysis"] = {
            "status": "INSUFFICIENT_DATA",
            "availability": None,
            "observation_window": window,
            "detected_issues": [],
            "healthy_hosts": 1 if health_status == "HEALTHY" else 0,
            "http_5xx_count": 0,
            "note": "Observation window insufficient to calculate availability SLA",
        }
        return state

    # Calculate metrics with sufficient window
    total_reqs = metrics.get("total_requests", metrics.get("request_count", 0))
    err_count = metrics.get("error_count", metrics.get("http_5xx_count", 0))
    healthy_hosts = metrics.get("healthy_host_count", 1)

    detected_issues: List[str] = []
    status = "HEALTHY"

    if healthy_hosts == 0:
        status = "UNHEALTHY"
        detected_issues.append("Zero healthy targets registered in ALB target group.")

    if err_count > 0:
        status = "DEGRADED" if err_count < (0.05 * total_reqs if total_reqs else 1) else "UNHEALTHY"
        detected_issues.append(f"Recorded {err_count} errors during {window} observation window.")

    availability: Optional[float] = None
    if total_reqs > 0:
        availability = round(((total_reqs - err_count) / total_reqs) * 100.0, 3)

    state["reliability_analysis"] = {
        "status": status,
        "availability": availability,
        "observation_window": window,
        "healthy_hosts": healthy_hosts,
        "http_5xx_count": err_count,
        "detected_issues": detected_issues,
        "note": f"Evaluated from {window} observation window across {total_reqs} requests",
    }

    return state
