from typing import Any, Dict


def what_if_engine_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Day 30: What-If Engineering Agent

    Takes the current architecture/digital twin and applies a requested
    hypothetical change so the Architecture Simulator can evaluate it.
    """

    architecture = state.get("architecture", {})
    digital_twin = architecture.get("digital_twin", {})
    knowledge_graph = architecture.get("knowledge_graph", {})

    what_if_request = state.get(
        "what_if_request",
        "Increase expected system traffic and evaluate scalability impact."
    )

    current_components = digital_twin.get("components", [])
    current_connections = digital_twin.get("connections", [])

    simulation_input = {
        "request": what_if_request,
        "baseline": {
            "component_count": len(current_components),
            "connection_count": len(current_connections),
            "architecture": architecture.get("selected", {}),
            "digital_twin_available": bool(digital_twin),
            "knowledge_graph_available": bool(knowledge_graph),
        },
        "changes": {
            "requested_change": what_if_request,
            "status": "pending_simulation",
        },
    }

    architecture["what_if"] = simulation_input
    state["architecture"] = architecture

    return state
