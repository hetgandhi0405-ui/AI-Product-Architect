import time

from backend.core.pipeline_metrics import (
    create_metrics,
    finish_node,
    finish_pipeline,
    skip_node,
    start_node,
)


def test_pipeline_metrics():
    metrics = create_metrics()

    started = start_node(metrics, "demo")
    time.sleep(0.001)
    finish_node(metrics, "demo", started)

    skip_node(metrics, "skipped")
    finish_pipeline(metrics)

    assert metrics["nodes"]["demo"]["status"] == "EXECUTED"
    assert metrics["nodes"]["demo"]["seconds"] >= 0
    assert metrics["nodes"]["skipped"]["status"] == "SKIPPED"
    assert metrics["nodes"]["skipped"]["seconds"] == 0.0
    assert metrics["completed_at"] is not None
    assert metrics["total_seconds"] is not None
    assert metrics["total_seconds"] >= 0
