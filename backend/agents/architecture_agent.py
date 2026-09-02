from backend.agents.state import AgentState


def architecture_agent(state: AgentState) -> AgentState:
    """
    Create an initial cloud architecture
    based on the project requirements.
    """

    state["architecture"] = {
        "frontend": "Web Application",
        "backend": "API Server",
        "database": "Managed Database",
        "storage": "Cloud Object Storage",
        "authentication": "User Authentication",
        "monitoring": "Cloud Monitoring"
    }

    return state