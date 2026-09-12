from langgraph.graph import END, StateGraph

from backend.agents.api_spec_agent import api_spec_agent
from backend.agents.architecture_agent import architecture_agent
from backend.agents.code_generation_contract_agent import (
    code_generation_contract_agent,
)
from backend.agents.code_quality_agent import code_quality_agent
from backend.agents.database_spec_agent import database_spec_agent
from backend.agents.dependency_agent import dependency_agent
from backend.agents.diagram_agent import diagram_agent
from backend.agents.dynamic_router_agent import dynamic_router_agent
from backend.agents.environment_config_agent import environment_config_agent
from backend.agents.infrastructure_agent import infrastructure_agent
from backend.agents.integration_agent import integration_agent
from backend.agents.integration_validation_agent import (
    integration_validation_agent,
)
from backend.agents.memory_manager import (
    create_project_memory,
    sync_project_memory,
)
from backend.agents.plugin_tool_agent import plugin_tool_agent
from backend.agents.product_planner_agent import product_planner_agent
from backend.agents.requirement_agent import requirement_agent
from backend.agents.self_correction_agent import self_correction_agent
from backend.agents.suggestion_agent import suggestion_agent
from backend.agents.terraform_agent import terraform_agent
from backend.agents.testing_agent import test_agent
from backend.agents.ui_ux_spec_agent import ui_ux_spec_agent
from backend.agents.validation_agent import validation_agent

from backend.agents.state import AgentState


def initialize_node(state: AgentState):
    """
    Initialize default project state and create project memory.
    """

    state["correction_attempts"] = state.get(
        "correction_attempts",
        0,
    )

    state["max_correction_attempts"] = state.get(
        "max_correction_attempts",
        3,
    )

    state["suggestions"] = state.get(
        "suggestions",
        [],
    )

    state["architecture"] = state.get(
        "architecture",
        {},
    )

    state["project_memory"] = create_project_memory(
        state
    )

    return state


def dynamic_router_node(state: AgentState):
    """
    Analyze the project and determine which agents are
    required, optional, or unnecessary.
    """

    result = dynamic_router_agent(state)

    routing = result.get(
        "dynamic_routing",
        {},
    )

    state["dynamic_routing"] = routing

    architecture = state.get(
        "architecture",
        {},
    )

    architecture["dynamic_routing"] = routing

    state["architecture"] = architecture

    return state


def memory_sync_node(state: AgentState):
    """
    Synchronize the final project state into project memory.
    """

    state = sync_project_memory(state)

    memory = state.get(
        "project_memory",
        {},
    )

    history = memory.setdefault(
        "history",
        [],
    )

    validation = state.get(
        "architecture",
        {},
    ).get(
        "validation",
        {},
    )

    history.append(
        {
            "event": "Project Validation Completed",
            "details": {
                "status": validation.get(
                    "status",
                    "UNKNOWN",
                ),
                "summary": validation.get(
                    "summary",
                    "",
                ),
            },
        }
    )

    state["project_memory"] = memory

    return state


def validation_router(state: AgentState):
    """
    Decide whether the project should be corrected
    or finalized.
    """

    validation = state.get(
        "architecture",
        {},
    ).get(
        "validation",
        {},
    )

    status = validation.get(
        "status",
        "INVALID",
    )

    if status == "VALID":
        return "memory_sync"

    attempts = state.get(
        "correction_attempts",
        0,
    )

    max_attempts = state.get(
        "max_correction_attempts",
        3,
    )

    if attempts >= max_attempts:
        return "memory_sync"

    return "self_correction"


def build_agent_graph():
    """
    Build the complete AI Product Architect agent graph.
    """

    graph_builder = StateGraph(AgentState)

    # =========================================================
    # INITIALIZATION
    # =========================================================

    graph_builder.add_node(
        "initialize",
        initialize_node,
    )

    # =========================================================
    # DAY 26 - DYNAMIC AGENT ROUTER
    # =========================================================

    graph_builder.add_node(
        "dynamic_router",
        dynamic_router_node,
    )

    # =========================================================
    # REQUIREMENT ANALYSIS
    # =========================================================

    graph_builder.add_node(
        "requirement",
        requirement_agent,
    )

    graph_builder.add_node(
        "suggestion",
        suggestion_agent,
    )

    # =========================================================
    # PRODUCT SPECIFICATION
    # =========================================================

    graph_builder.add_node(
        "product_planner",
        product_planner_agent,
    )

    graph_builder.add_node(
        "ui_ux_spec",
        ui_ux_spec_agent,
    )

    graph_builder.add_node(
        "api_spec",
        api_spec_agent,
    )

    graph_builder.add_node(
        "database_spec",
        database_spec_agent,
    )

    # =========================================================
    # ARCHITECTURE
    # =========================================================

    graph_builder.add_node(
        "architecture",
        architecture_agent,
    )

    graph_builder.add_node(
        "integration",
        integration_agent,
    )

    graph_builder.add_node(
        "plugin_tool",
        plugin_tool_agent,
    )

    # =========================================================
    # CODE GENERATION PLANNING
    # =========================================================

    graph_builder.add_node(
        "code_generation_contract",
        code_generation_contract_agent,
    )

    graph_builder.add_node(
        "code_quality",
        code_quality_agent,
    )

    graph_builder.add_node(
        "test",
        test_agent,
    )

    # =========================================================
    # DEPENDENCIES AND ENVIRONMENT
    # =========================================================

    graph_builder.add_node(
        "dependency",
        dependency_agent,
    )

    graph_builder.add_node(
        "environment_config",
        environment_config_agent,
    )

    graph_builder.add_node(
        "integration_validation",
        integration_validation_agent,
    )

    # =========================================================
    # ARCHITECTURE / INFRASTRUCTURE OUTPUTS
    # =========================================================

    graph_builder.add_node(
        "diagram",
        diagram_agent,
    )

    graph_builder.add_node(
        "infrastructure",
        infrastructure_agent,
    )

    graph_builder.add_node(
        "terraform",
        terraform_agent,
    )

    # =========================================================
    # VALIDATION AND SELF-CORRECTION
    # =========================================================

    graph_builder.add_node(
        "validation",
        validation_agent,
    )

    graph_builder.add_node(
        "self_correction",
        self_correction_agent,
    )

    # =========================================================
    # PROJECT MEMORY
    # =========================================================

    graph_builder.add_node(
        "memory_sync",
        memory_sync_node,
    )

    # =========================================================
    # GRAPH ENTRY
    # =========================================================

    graph_builder.set_entry_point(
        "initialize"
    )

    # =========================================================
    # DYNAMIC ROUTER
    # =========================================================

    graph_builder.add_edge(
        "initialize",
        "dynamic_router",
    )

    # =========================================================
    # MAIN PIPELINE
    # =========================================================

    graph_builder.add_edge(
        "dynamic_router",
        "requirement",
    )

    graph_builder.add_edge(
        "requirement",
        "suggestion",
    )

    graph_builder.add_edge(
        "suggestion",
        "product_planner",
    )

    graph_builder.add_edge(
        "product_planner",
        "ui_ux_spec",
    )

    graph_builder.add_edge(
        "ui_ux_spec",
        "api_spec",
    )

    graph_builder.add_edge(
        "api_spec",
        "database_spec",
    )

    graph_builder.add_edge(
        "database_spec",
        "architecture",
    )

    graph_builder.add_edge(
        "architecture",
        "integration",
    )

    graph_builder.add_edge(
        "integration",
        "plugin_tool",
    )

    graph_builder.add_edge(
        "plugin_tool",
        "code_generation_contract",
    )

    graph_builder.add_edge(
        "code_generation_contract",
        "code_quality",
    )

    graph_builder.add_edge(
        "code_quality",
        "test",
    )

    graph_builder.add_edge(
        "test",
        "dependency",
    )

    graph_builder.add_edge(
        "dependency",
        "environment_config",
    )

    graph_builder.add_edge(
        "environment_config",
        "integration_validation",
    )

    graph_builder.add_edge(
        "integration_validation",
        "diagram",
    )

    graph_builder.add_edge(
        "diagram",
        "infrastructure",
    )

    graph_builder.add_edge(
        "infrastructure",
        "terraform",
    )

    graph_builder.add_edge(
        "terraform",
        "validation",
    )

    # =========================================================
    # VALIDATION LOOP
    # =========================================================

    graph_builder.add_conditional_edges(
        "validation",
        validation_router,
        {
            "self_correction": "self_correction",
            "memory_sync": "memory_sync",
        },
    )

    graph_builder.add_edge(
        "self_correction",
        "validation",
    )

    # =========================================================
    # FINAL MEMORY SYNC
    # =========================================================

    graph_builder.add_edge(
        "memory_sync",
        END,
    )

    return graph_builder.compile()