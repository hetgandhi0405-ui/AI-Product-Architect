from backend.agents.monitoring_agent import monitoring_agent
from backend.agents.failure_detection_agent import failure_detection_agent


def make_state(metrics):
    return {
        "architecture": {
            "infrastructure": {
                "provider": "AWS",
                "resources": [
                    {"type": "compute"},
                    {"type": "database"},
                ],
            },
            "monitoring_metrics": metrics,
        }
    }


def test_monitoring_collects_metrics():
    state = make_state(
        {
            "cpu_utilization": 82,
            "memory_utilization": 71,
            "latency_ms": 120,
            "error_rate": 1.2,
        }
    )

    result = monitoring_agent(state)
    monitoring = result["architecture"]["monitoring"]

    assert monitoring["data_source"] == "runtime_metrics"
    assert monitoring["metrics"]["cpu_utilization"] == 82
    assert monitoring["metrics"]["memory_utilization"] == 71
    assert monitoring["metrics"]["latency_ms"] == 120


def test_failure_detection_detects_multiple_failures():
    state = make_state(
        {
            "cpu_utilization": 96,
            "memory_utilization": 72,
            "latency_ms": 650,
            "error_rate": 2,
            "database_utilization": 94,
        }
    )

    state = monitoring_agent(state)
    result = failure_detection_agent(state)

    detection = result["architecture"]["failure_detection"]

    assert detection["failure_detected"] is True
    assert detection["failure_count"] == 3

    failure_types = {
        failure["failure_type"]
        for failure in detection["failures"]
    }

    assert "cpu_overload" in failure_types
    assert "high_latency" in failure_types
    assert "database_saturation" in failure_types


def test_failure_detection_reports_healthy_system():
    state = make_state(
        {
            "cpu_utilization": 40,
            "memory_utilization": 45,
            "disk_utilization": 50,
            "network_utilization": 35,
            "latency_ms": 100,
            "error_rate": 0.5,
            "database_utilization": 50,
        }
    )

    state = monitoring_agent(state)
    result = failure_detection_agent(state)

    detection = result["architecture"]["failure_detection"]

    assert detection["failure_detected"] is False
    assert detection["failure_count"] == 0
    assert detection["status"] == "healthy"
