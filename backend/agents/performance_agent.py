from typing import Any, Dict, List
from backend.agents.state import AgentState

PERFORMANCE_THRESHOLDS = {
    "cpu_degraded": 80.0,
    "cpu_unhealthy": 95.0,
    "memory_degraded": 80.0,
    "memory_unhealthy": 95.0,
    "p95_latency_degraded_ms": 1000.0,
    "p95_latency_unhealthy_ms": 3000.0,
    "error_rate_degraded_pct": 5.0,
    "error_rate_unhealthy_pct": 20.0,
}


def performance_agent(state: AgentState) -> AgentState:
    """
    Evaluates runtime performance metrics against configured thresholds.
    Vocabulary: HEALTHY | DEGRADED | UNHEALTHY | INSUFFICIENT_DATA
    """
    telemetry = state.get("telemetry_data", {})
    metrics = telemetry.get("metrics", {})

    # If no runtime data is available
    if not metrics or telemetry.get("status") in ("SKIPPED", "UNAVAILABLE"):
        state["performance_analysis"] = {
            "status": "INSUFFICIENT_DATA",
            "source": "static_spec",
            "detected_problems": [],
            "recommendations": [
                "Deploy with real runtime traffic to collect actual latency and CPU metrics."
            ],
            "metrics_evaluated": {},
            "note": "no runtime data",
        }
        return state

    detected_problems: List[Dict[str, Any]] = []
    recommendations: List[str] = []

    cpu = metrics.get("cpu_utilization")
    mem = metrics.get("memory_utilization")
    latency_p95 = metrics.get("latency_p95_ms")
    error_rate = metrics.get("error_rate")

    status = "HEALTHY"

    # CPU Check
    if cpu is not None:
        if cpu >= PERFORMANCE_THRESHOLDS["cpu_unhealthy"]:
            status = "UNHEALTHY"
            detected_problems.append({
                "problem": "critical_cpu_saturation",
                "evidence": f"CPU utilization is {cpu}% (>= {PERFORMANCE_THRESHOLDS['cpu_unhealthy']}%)",
                "severity": "critical",
            })
            recommendations.append("Scale out ECS task count or increase vCPU allocation.")
        elif cpu >= PERFORMANCE_THRESHOLDS["cpu_degraded"]:
            if status != "UNHEALTHY":
                status = "DEGRADED"
            detected_problems.append({
                "problem": "high_cpu_utilization",
                "evidence": f"CPU utilization is {cpu}% (>= {PERFORMANCE_THRESHOLDS['cpu_degraded']}%)",
                "severity": "warning",
            })
            recommendations.append("Increase ECS task CPU or enable auto-scaling.")

    # Memory Check
    if mem is not None:
        if mem >= PERFORMANCE_THRESHOLDS["memory_unhealthy"]:
            status = "UNHEALTHY"
            detected_problems.append({
                "problem": "critical_memory_exhaustion",
                "evidence": f"Memory utilization is {mem}% (>= {PERFORMANCE_THRESHOLDS['memory_unhealthy']}%)",
                "severity": "critical",
            })
            recommendations.append("Increase Fargate container memory limit to prevent OOM kills.")
        elif mem >= PERFORMANCE_THRESHOLDS["memory_degraded"]:
            if status != "UNHEALTHY":
                status = "DEGRADED"
            detected_problems.append({
                "problem": "high_memory_utilization",
                "evidence": f"Memory utilization is {mem}% (>= {PERFORMANCE_THRESHOLDS['memory_degraded']}%)",
                "severity": "warning",
            })
            recommendations.append("Optimize application memory caching or increase task memory.")

    # Latency Check
    if latency_p95 is not None:
        if latency_p95 >= PERFORMANCE_THRESHOLDS["p95_latency_unhealthy_ms"]:
            status = "UNHEALTHY"
            detected_problems.append({
                "problem": "severe_latency_degradation",
                "evidence": f"p95 latency is {latency_p95}ms (>= {PERFORMANCE_THRESHOLDS['p95_latency_unhealthy_ms']}ms)",
                "severity": "critical",
            })
            recommendations.append("Profile database query bottlenecks and add caching.")
        elif latency_p95 >= PERFORMANCE_THRESHOLDS["p95_latency_degraded_ms"]:
            if status != "UNHEALTHY":
                status = "DEGRADED"
            detected_problems.append({
                "problem": "elevated_response_latency",
                "evidence": f"p95 latency is {latency_p95}ms (>= {PERFORMANCE_THRESHOLDS['p95_latency_degraded_ms']}ms)",
                "severity": "warning",
            })
            recommendations.append("Review slow endpoint execution times and connection pooling.")

    # Error Rate Check
    if error_rate is not None:
        if error_rate >= PERFORMANCE_THRESHOLDS["error_rate_unhealthy_pct"]:
            status = "UNHEALTHY"
            detected_problems.append({
                "problem": "critical_error_rate",
                "evidence": f"HTTP error rate is {error_rate}% (>= {PERFORMANCE_THRESHOLDS['error_rate_unhealthy_pct']}%)",
                "severity": "critical",
            })
            recommendations.append("Inspect application crash logs and database connection limits.")
        elif error_rate >= PERFORMANCE_THRESHOLDS["error_rate_degraded_pct"]:
            if status != "UNHEALTHY":
                status = "DEGRADED"
            detected_problems.append({
                "problem": "elevated_error_rate",
                "evidence": f"HTTP error rate is {error_rate}% (>= {PERFORMANCE_THRESHOLDS['error_rate_degraded_pct']}%)",
                "severity": "warning",
            })
            recommendations.append("Check upstream service dependencies and request validation.")

    state["performance_analysis"] = {
        "status": status,
        "source": "telemetry",
        "detected_problems": detected_problems,
        "recommendations": recommendations or ["Performance metrics within normal operating thresholds."],
        "metrics_evaluated": {
            "cpu_utilization": cpu,
            "memory_utilization": mem,
            "latency_p95_ms": latency_p95,
            "error_rate": error_rate,
        },
    }

    return state
