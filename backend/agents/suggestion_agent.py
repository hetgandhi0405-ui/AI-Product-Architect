from backend.agents.state import AgentState


def suggestion_agent(state: AgentState) -> AgentState:
    """
    Generate initial suggestions based on the
    customer's requirements.
    """

    requirements = state["requirements"]

    suggestions = state.get("suggestions", [])

    suggestions.extend([
        f"Application type identified from: {requirements}",
        "Use a scalable cloud-based architecture",
        "Include secure user authentication",
        "Use a managed database for application data",
        "Include monitoring and logging"
    ])

    state["suggestions"] = suggestions

    return state