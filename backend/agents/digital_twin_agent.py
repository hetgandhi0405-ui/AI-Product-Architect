from typing import Any, Dict

from backend.agents.state import AgentState


def digital_twin_agent(state: AgentState) -> AgentState:
    """
    Build a structured Digital Twin of the generated software architecture.

    The Digital Twin represents:
    - Project identity
    - Architecture components
    - Architecture relationships
    - Infrastructure
    - Dependencies
    - Environment configuration
    - Architecture alternatives
    - Current system state

    This model is designed to support future
    What-If Engineering and Architecture Simulation.
    """

    project_id = state.get(
        "project_id",
        "project",
    )

    project_name = state.get(
        "project_name",
        "AI Product",
    )

    architecture = state.get(
        "architecture",
        {},
    )

    knowledge_graph = architecture.get(
        "knowledge_graph",
        {},
    )

    nodes = knowledge_graph.get(
        "nodes",
        [],
    )

    relationships = knowledge_graph.get(
        "relationships",
        [],
    )

    infrastructure = architecture.get(
        "infrastructure",
        {},
    )

    dependencies = architecture.get(
        "dependency_specification",
        state.get(
            "dependency_specification",
            {},
        ),
    )

    environment = architecture.get(
        "environment_configuration",
        state.get(
            "environment_configuration",
            {},
        ),
    )

    alternatives = architecture.get(
        "architecture_alternatives",
        {},
    )

    evaluation = architecture.get(
        "architecture_evaluation",
        {},
    )

    # =========================================================
    # COMPONENT STATE
    # =========================================================

    components = []

    for node in nodes:
        if not isinstance(node, dict):
            continue

        components.append(
            {
                "id": node.get("id", ""),
                "type": node.get("type", ""),
                "name": node.get("name", ""),
                "status": "ACTIVE",
                "properties": node.get(
                    "properties",
                    {},
                ),
            }
        )

    # =========================================================
    # RELATIONSHIP STATE
    # =========================================================

    connection_state = []

    for relationship in relationships:
        if not isinstance(
            relationship,
            dict,
        ):
            continue

        connection_state.append(
            {
                "source": relationship.get(
                    "source",
                    "",
                ),
                "target": relationship.get(
                    "target",
                    "",
                ),
                "relationship": relationship.get(
                    "relationship",
                    "",
                ),
                "status": "ACTIVE",
            }
        )

    # =========================================================
    # DIGITAL TWIN
    # =========================================================

    digital_twin = {
        "twin_type": "Software Architecture Digital Twin",
        "version": "1.0",
        "project": {
            "project_id": project_id,
            "project_name": project_name,
        },
        "system_state": {
            "status": "ACTIVE",
            "architecture_status": "GENERATED",
            "validation_status": architecture.get(
                "validation",
                {},
            ).get(
                "status",
                "UNKNOWN",
            ),
        },
        "components": components,
        "connections": connection_state,
        "infrastructure": infrastructure,
        "dependencies": dependencies,
        "environment": environment,
        "architecture_alternatives": alternatives,
        "architecture_evaluation": evaluation,
        "source_knowledge_graph": {
            "node_count": len(nodes),
            "relationship_count": len(
                relationships
            ),
        },
        "simulation_ready": True,
    }

    # Store Digital Twin in architecture state.
    architecture[
        "digital_twin"
    ] = digital_twin

    state[
        "architecture"
    ] = architecture

    return state
