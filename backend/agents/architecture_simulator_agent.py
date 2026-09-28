from typing import Any, Dict


def architecture_simulator_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Day 30: AI Architecture Simulator

    Simulates the expected impact of a What-If architecture change.
    The current implementation provides a deterministic baseline model
    that can later be enhanced with an LLM-based simulation layer.
    """

    architecture = state.get("architecture", {})
    what_if = architecture.get("what_if", {})

    if not what_if:
        return state

    baseline = what_if.get("baseline", {})

    component_count = baseline.get("component_count", 0)
    connection_count = baseline.get("connection_count", 0)

    request = what_if.get("request", "").lower()

    cost = 50
    performance = 70
    scalability = 65
    security = 70
    complexity = 40

    if "traffic" in request or "users" in request or "scale" in request:
        cost += 15
        performance -= 5
        scalability += 20
        complexity += 10

    if "cache" in request or "redis" in request:
        cost += 5
        performance += 15
        scalability += 10
        complexity += 5

    if "load balancer" in request or "load balancing" in request:
        cost += 8
        performance += 10
        scalability += 15
        complexity += 8

    if "database" in request:
        cost += 10
        scalability += 8
        complexity += 8

    simulation = {
        "simulation_type": "Architecture What-If Simulation",
        "status": "completed",
        "scenario": what_if.get("request"),
        "baseline": {
            "components": component_count,
            "connections": connection_count,
        },
        "impact": {
            "cost": min(cost, 100),
            "performance": max(min(performance, 100), 0),
            "scalability": min(scalability, 100),
            "security": min(security, 100),
            "complexity": min(complexity, 100),
        },
        "recommendations": [
            "Review scalability requirements before deployment.",
            "Validate infrastructure capacity for the expected workload.",
            "Run automated architecture validation after applying the change.",
        ],
    }

    architecture["simulation"] = simulation
    state["architecture"] = architecture

    return state
