from langgraph.graph import StateGraph, START, END

from backend.agents.state import AgentState
from backend.agents.requirement_agent import requirement_agent
from backend.agents.suggestion_agent import suggestion_agent
from backend.agents.architecture_agent import architecture_agent
from backend.agents.diagram_agent import diagram_agent
from backend.agents.infrastructure_agent import infrastructure_agent
from backend.agents.terraform_agent import terraform_agent
from backend.agents.validation_agent import validation_agent
from backend.agents.self_correction_agent import self_correction_agent


def build_agent_graph():
    """
    Build the AI Product Architect agent workflow.
    """

    graph = StateGraph(AgentState)

    # Register agents
    graph.add_node("requirement_agent", requirement_agent)
    graph.add_node("suggestion_agent", suggestion_agent)
    graph.add_node("architecture_agent", architecture_agent)
    graph.add_node("diagram_agent", diagram_agent)
    graph.add_node("infrastructure_agent", infrastructure_agent)
    graph.add_node("terraform_agent", terraform_agent)
    graph.add_node("validation_agent", validation_agent)
    graph.add_node("self_correction_agent", self_correction_agent)

    # Connect workflow
    graph.add_edge(START, "requirement_agent")
    graph.add_edge("requirement_agent", "suggestion_agent")
    graph.add_edge("suggestion_agent", "architecture_agent")
    graph.add_edge("architecture_agent", "diagram_agent")
    graph.add_edge("diagram_agent", "infrastructure_agent")
    graph.add_edge("infrastructure_agent", "terraform_agent")
    graph.add_edge("terraform_agent", "validation_agent")
    graph.add_edge("validation_agent", "self_correction_agent")
    graph.add_edge("self_correction_agent", END)

    return graph.compile()