from langgraph.graph import StateGraph, START, END

from backend.agents.state import AgentState
from backend.agents.requirement_agent import requirement_agent
from backend.agents.suggestion_agent import suggestion_agent
from backend.agents.architecture_agent import architecture_agent


def build_agent_graph():
    """
    Build the AI Product Architect agent workflow.
    """

    graph = StateGraph(AgentState)

    # Add agents as graph nodes
    graph.add_node("requirement_agent", requirement_agent)
    graph.add_node("suggestion_agent", suggestion_agent)
    graph.add_node("architecture_agent", architecture_agent)

    # Connect the workflow
    graph.add_edge(START, "requirement_agent")
    graph.add_edge("requirement_agent", "suggestion_agent")
    graph.add_edge("suggestion_agent", "architecture_agent")
    graph.add_edge("architecture_agent", END)

    return graph.compile()