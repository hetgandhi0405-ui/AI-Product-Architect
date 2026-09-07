from langgraph.graph import StateGraph, END

from backend.agents.state import AgentState
from backend.agents.requirement_agent import requirement_agent
from backend.agents.suggestion_agent import suggestion_agent
from backend.agents.architecture_agent import architecture_agent
from backend.agents.diagram_agent import diagram_agent
from backend.agents.infrastructure_agent import infrastructure_agent
from backend.agents.terraform_agent import terraform_agent
from backend.agents.validation_agent import validation_agent
from backend.agents.self_correction_agent import self_correction_agent


def initialize_state(state: AgentState) -> AgentState:
    """
    Initialize validation loop counters.
    """

    state["correction_attempts"] = 0
    state["max_correction_attempts"] = 3

    return state


def validation_router(state: AgentState) -> str:
    """
    Decide whether the workflow should end
    or perform self-correction.
    """

    validation = state.get("architecture", {}).get("validation", {})

    # Architecture is valid
    if validation.get("is_valid", False):
        return "end"

    # Stop after maximum correction attempts
    attempts = state.get("correction_attempts", 0)
    max_attempts = state.get("max_correction_attempts", 3)

    if attempts >= max_attempts:
        return "end"

    # Architecture is invalid and correction is allowed
    return "correct"


# Create workflow
graph_builder = StateGraph(AgentState)


# Add agents
graph_builder.add_node("initialize", initialize_state)
graph_builder.add_node("requirement", requirement_agent)
graph_builder.add_node("suggestion", suggestion_agent)
graph_builder.add_node("architecture", architecture_agent)
graph_builder.add_node("diagram", diagram_agent)
graph_builder.add_node("infrastructure", infrastructure_agent)
graph_builder.add_node("terraform", terraform_agent)
graph_builder.add_node("validation", validation_agent)
graph_builder.add_node("self_correction", self_correction_agent)


# Starting point
graph_builder.set_entry_point("initialize")


# Main workflow
graph_builder.add_edge("initialize", "requirement")
graph_builder.add_edge("requirement", "suggestion")
graph_builder.add_edge("suggestion", "architecture")
graph_builder.add_edge("architecture", "diagram")
graph_builder.add_edge("diagram", "infrastructure")
graph_builder.add_edge("infrastructure", "terraform")
graph_builder.add_edge("terraform", "validation")


# Validation decision
graph_builder.add_conditional_edges(
    "validation",
    validation_router,
    {
        "end": END,
        "correct": "self_correction"
    }
)


# Self-correction goes back to validation
graph_builder.add_edge(
    "self_correction",
    "validation"
)


# Compile workflow
graph = graph_builder.compile()


def build_agent_graph():
    """
    Return the compiled AI Product Architect workflow.
    """
    return graph