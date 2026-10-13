from backend.core.pipeline_metrics import (
    create_metrics,
    finish_node,
    finish_pipeline,
    skip_node,
    start_node,
)


def test_executed_node_metrics():
    metrics = create_metrics()

    started = start_node(metrics, "test_agent")
    finish_node(metrics, "test_agent", started)

    node = metrics["nodes"]["test_agent"]

    assert node["status"] == "EXECUTED"
    assert node["seconds"] >= 0


def test_skipped_node_metrics():
    metrics = create_metrics()

    skip_node(metrics, "optional_agent")

    node = metrics["nodes"]["optional_agent"]

    assert node["status"] == "SKIPPED"
    assert node["seconds"] == 0.0


def test_pipeline_completion_metrics():
    metrics = create_metrics()

    finish_pipeline(metrics)

    assert metrics["completed_at"] is not None
    assert metrics["total_seconds"] is not None
    assert metrics["total_seconds"] >= 0
