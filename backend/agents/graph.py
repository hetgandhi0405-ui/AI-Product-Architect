from langgraph.graph import StateGraph, END

from backend.agents.state import AgentState
from backend.agents.requirement_agent import requirement_agent
from backend.agents.suggestion_agent import suggestion_agent
from backend.agents.product_planner_agent import product_planner_agent
from backend.agents.ui_ux_spec_agent import ui_ux_spec_agent
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
    Decide whether the workflow should finish
    or run the self-correction process.
    """

    validation = state.get(
        "architecture",
        {}
    ).get(
        "validation",
        {}
    )

    if validation.get("is_valid", False):
        return "end"

    attempts = state.get(
        "correction_attempts",
        0
    )

    max_attempts = state.get(
        "max_correction_attempts",
        3
    )

    if attempts >= max_attempts:
        return "end"

    return "correct"


graph_builder = StateGraph(AgentState)


# -------------------------
# Add agents
# -------------------------

graph_builder.add_node(
    "initialize",
    initialize_state
)

graph_builder.add_node(
    "requirement",
    requirement_agent
)

graph_builder.add_node(
    "suggestion",
    suggestion_agent
)

graph_builder.add_node(
    "product_planner",
    product_planner_agent
)

graph_builder.add_node(
    "ui_ux_spec",
    ui_ux_spec_agent
)

graph_builder.add_node(
    "architecture",
    architecture_agent
)

graph_builder.add_node(
    "diagram",
    diagram_agent
)

graph_builder.add_node(
    "infrastructure",
    infrastructure_agent
)

graph_builder.add_node(
    "terraform",
    terraform_agent
)

graph_builder.add_node(
    "validation",
    validation_agent
)

graph_builder.add_node(
    "self_correction",
    self_correction_agent
)


# -------------------------
# Workflow
# -------------------------

graph_builder.set_entry_point(
    "initialize"
)

graph_builder.add_edge(
    "initialize",
    "requirement"
)

graph_builder.add_edge(
    "requirement",
    "suggestion"
)

graph_builder.add_edge(
    "suggestion",
    "product_planner"
)

graph_builder.add_edge(
    "product_planner",
    "ui_ux_spec"
)

graph_builder.add_edge(
    "ui_ux_spec",
    "architecture"
)

graph_builder.add_edge(
    "architecture",
    "diagram"
)

graph_builder.add_edge(
    "diagram",
    "infrastructure"
)

graph_builder.add_edge(
    "infrastructure",
    "terraform"
)

graph_builder.add_edge(
    "terraform",
    "validation"
)


# -------------------------
# Validation loop
# -------------------------

graph_builder.add_conditional_edges(
    "validation",
    validation_router,
    {
        "end": END,
        "correct": "self_correction"
    }
)

graph_builder.add_edge(
    "self_correction",
    "validation"
)


# Compile graph
graph = graph_builder.compile()


def build_agent_graph():
    """
    Return the compiled AI Product Architect workflow.
    """
    return graph
