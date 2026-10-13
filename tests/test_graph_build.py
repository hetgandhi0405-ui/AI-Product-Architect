from backend.agents.graph import build_agent_graph


def test_agent_graph_builds():
    graph = build_agent_graph()
    assert graph is not None
    assert "__start__" in graph.nodes
    assert "validation" in graph.nodes
    assert "self_correction" in graph.nodes
    assert "memory_sync" in graph.nodes


def test_graph_protects_core_nodes_from_dynamic_skips():
    from backend.agents.graph import timed_conditional_node

    calls = []

    def core_node(state):
        calls.append("executed")
        return state

    wrapped = timed_conditional_node("architecture", core_node)
    state = {
        "execution_mode": "FULL",
        "pipeline_metrics": {},
        "dynamic_routing": {"skipped_agents": ["architecture"]},
        "architecture": {},
    }

    result = wrapped(state)

    assert calls == ["executed"]
    assert result["pipeline_metrics"]["nodes"]["architecture"]["status"] == "EXECUTED"
