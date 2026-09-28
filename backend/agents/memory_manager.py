from typing import Any, Dict


def create_project_memory(
    state: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create the initial structured memory for a project.
    """

    architecture = state.get(
        "architecture",
        {}
    )

    memory = {
        "project": {
            "project_id": state.get(
                "project_id",
                ""
            ),
            "project_name": state.get(
                "project_name",
                ""
            ),
            "requirements": state.get(
                "requirements",
                ""
            )
        },

        "product_plan": state.get(
            "product_plan",
            {}
        ),

        "ui_specification": state.get(
            "ui_specification",
            {}
        ),

        "api_specification": state.get(
            "api_specification",
            {}
        ),

        "database_specification": state.get(
            "database_specification",
            {}
        ),

        "architecture": architecture,

        "dependencies": architecture.get(
            "dependency_specification",
            {}
        ),

        "environment_configuration": architecture.get(
            "environment_configuration",
            {}
        ),

        "history": []
    }

    return memory


def sync_project_memory(
    state: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Synchronize project memory with the latest
    generated specifications in AgentState.
    """

    memory = state.get(
        "project_memory",
        {}
    )

    if not memory:
        memory = create_project_memory(
            state
        )

    architecture = state.get(
        "architecture",
        {}
    )

    memory["project"] = {
        "project_id": state.get(
            "project_id",
            ""
        ),
        "project_name": state.get(
            "project_name",
            ""
        ),
        "requirements": state.get(
            "requirements",
            ""
        )
    }

    memory["product_plan"] = state.get(
        "product_plan",
        {}
    )

    memory["ui_specification"] = state.get(
        "ui_specification",
        {}
    )

    memory["api_specification"] = state.get(
        "api_specification",
        {}
    )

    memory["database_specification"] = state.get(
        "database_specification",
        {}
    )

    memory["architecture"] = architecture

    memory["dependencies"] = architecture.get(
        "dependency_specification",
        {}
    )

    memory["environment_configuration"] = architecture.get(
        "environment_configuration",
        {}
    )

    state["project_memory"] = memory

    return state


def update_project_memory(
    state: Dict[str, Any],
    event: str,
    details: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """
    Add an event to the project's memory history.
    """

    memory = state.get(
        "project_memory",
        {}
    )

    if not memory:
        memory = create_project_memory(
            state
        )

    history = memory.setdefault(
        "history",
        []
    )

    history.append(
        {
            "event": event,
            "details": details or {}
        }
    )

    state["project_memory"] = memory

    return state