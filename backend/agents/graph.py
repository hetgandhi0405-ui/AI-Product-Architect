from langgraph.graph import StateGraph, START, END

from backend.agents.state import AgentState

from backend.agents.requirement_agent import requirement_agent
from backend.agents.suggestion_agent import suggestion_agent
from backend.agents.product_planner_agent import product_planner_agent
from backend.agents.ui_ux_spec_agent import ui_ux_spec_agent
from backend.agents.api_spec_agent import api_spec_agent
from backend.agents.database_spec_agent import database_spec_agent
from backend.agents.architecture_agent import architecture_agent
from backend.agents.integration_agent import integration_agent
from backend.agents.code_generation_contract_agent import (
    code_generation_contract_agent
)
from backend.agents.code_quality_agent import code_quality_agent
from backend.agents.diagram_agent import diagram_agent
from backend.agents.infrastructure_agent import infrastructure_agent
from backend.agents.terraform_agent import terraform_agent
from backend.agents.validation_agent import validation_agent
from backend.agents.self_correction_agent import self_correction_agent


def validation_router(state: AgentState):
    """
    Decide whether the workflow should finish or
    go through the self-correction process.
    """

    architecture = state.get("architecture", {})
    validation = architecture.get("validation", {})

    status = validation.get("status", "INVALID")

    if status == "VALID":
        return "end"

    correction_attempts = state.get("correction_attempts", 0)
    max_correction_attempts = state.get(
        "max_correction_attempts",
        3
    )

    if correction_attempts < max_correction_attempts:
        return "self_correction"

    return "end"


def build_agent_graph():
    """
    Build the complete AI Product Architect agent workflow.
    """

    graph_builder = StateGraph(AgentState)

    # --------------------------------------------------
    # Add Nodes
    # --------------------------------------------------

    graph_builder.add_node(
        "initialize",
        lambda state: state
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
        "api_spec",
        api_spec_agent
    )

    graph_builder.add_node(
        "database_spec",
        database_spec_agent
    )

    graph_builder.add_node(
        "architecture",
        architecture_agent
    )

    graph_builder.add_node(
        "integration",
        integration_agent
    )

    graph_builder.add_node(
        "code_generation_contract",
        code_generation_contract_agent
    )

    graph_builder.add_node(
        "code_quality",
        code_quality_agent
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

    # --------------------------------------------------
    # Main Workflow
    # --------------------------------------------------

    graph_builder.add_edge(
        START,
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
        "api_spec"
    )

    graph_builder.add_edge(
        "api_spec",
        "database_spec"
    )

    graph_builder.add_edge(
        "database_spec",
        "architecture"
    )

    graph_builder.add_edge(
        "architecture",
        "integration"
    )

    graph_builder.add_edge(
        "integration",
        "code_generation_contract"
    )

    # Day 19: Code Quality Agent
    graph_builder.add_edge(
        "code_generation_contract",
        "code_quality"
    )

    graph_builder.add_edge(
        "code_quality",
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

    # --------------------------------------------------
    # Validation / Self-Correction Loop
    # --------------------------------------------------

    graph_builder.add_conditional_edges(
        "validation",
        validation_router,
        {
            "self_correction": "self_correction",
            "end": END
        }
    )

    graph_builder.add_edge(
        "self_correction",
        "validation"
    )

    return graph_builder.compile()