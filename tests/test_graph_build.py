from backend.agents.graph import build_agent_graph


def test_agent_graph_builds():
    graph = build_agent_graph()
    assert graph is not None
    assert "__start__" in graph.nodes
    assert "validation" in graph.nodes
    assert "self_correction" in graph.nodes
    assert "memory_sync" in graph.nodes
