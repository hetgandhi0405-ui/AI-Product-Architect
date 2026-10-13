import time
from typing import Any, Dict


def create_metrics() -> Dict[str, Any]:
    return {
        "started_at": time.time(),
        "completed_at": None,
        "total_seconds": None,
        "nodes": {},
    }


def start_node(metrics: Dict[str, Any], node_name: str) -> float:
    return time.perf_counter()


def finish_node(
    metrics: Dict[str, Any],
    node_name: str,
    start_time: float,
    status: str = "EXECUTED",
) -> None:
    metrics.setdefault("nodes", {})[node_name] = {
        "seconds": round(time.perf_counter() - start_time, 3),
        "status": status,
    }


def skip_node(metrics: Dict[str, Any], node_name: str) -> None:
    metrics.setdefault("nodes", {})[node_name] = {
        "seconds": 0.0,
        "status": "SKIPPED",
    }


def finish_pipeline(metrics: Dict[str, Any]) -> None:
    metrics["completed_at"] = time.time()
    metrics["total_seconds"] = round(
        metrics["completed_at"] - metrics["started_at"],
        3,
    )
