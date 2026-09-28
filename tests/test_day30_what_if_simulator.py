from backend.agents.architecture_simulator_agent import architecture_simulator_agent
from backend.agents.what_if_engine_agent import what_if_engine_agent


def test_what_if_engine():
    state = {"what_if_request": "Increase traffic to 100,000 users", "architecture": {"digital_twin": {"components": [{"name": "Frontend"}, {"name": "Backend"}, {"name": "Database"}], "connections": [{"source": "Frontend", "target": "Backend"}, {"source": "Backend", "target": "Database"}]}, "knowledge_graph": {"statistics": {"nodes": 3, "relationships": 2}}}}
    result = what_if_engine_agent(state)
    assert "what_if" in result["architecture"]
    assert result["architecture"]["what_if"]["request"] == "Increase traffic to 100,000 users"


def test_architecture_simulator():
    state = {"architecture": {"what_if": {"request": "Increase traffic to 100,000 users", "baseline": {"component_count": 3, "connection_count": 2, "architecture": {}, "digital_twin_available": True, "knowledge_graph_available": True}}}}
    result = architecture_simulator_agent(state)
    simulation = result["architecture"]["simulation"]
    assert simulation["status"] == "completed"
    assert "impact" in simulation
    assert simulation["impact"]["scalability"] > 0
    assert simulation["impact"]["cost"] > 0
    assert simulation["impact"]["performance"] > 0
