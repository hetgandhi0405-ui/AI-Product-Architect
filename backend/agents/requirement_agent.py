from backend.agents.state import AgentState


def requirement_agent(state: AgentState) -> AgentState:
    """
    Analyze the customer's requirements
    and prepare them for the next agent.
    """

    requirements = state["requirements"]

    state["suggestions"] = [
        f"Requirement received: {requirements}",
        "Analyze required application components",
        "Identify cloud services needed",
        "Prepare architecture recommendations"
    ]

    return state