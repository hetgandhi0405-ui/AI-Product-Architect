from langgraph.graph import StateGraph, START, END

from backend.agents.state import AgentState

from backend.agents.memory_manager import (
    create_project_memory,
    sync_project_memory
)

from backend.agents.requirement_agent import requirement_agent
from backend.agents.suggestion_agent import suggestion_agent
from backend.agents.product_planner_agent import product_planner_agent
from backend.agents.ui_ux_spec_agent import ui_ux_spec_agent
from backend.agents.api_spec_agent import api_spec_agent
from backend.agents.database_spec_agent import database_spec_agent
from backend.agents.architecture_agent import architecture_agent
from backend.agents.integration_agent import integration_agent
from backend.agents.plugin_tool_agent import plugin_tool_agent

from backend.agents.code_generation_contract_agent import (
    code_generation_contract_agent
)

from backend.agents.code_quality_agent import code_quality_agent
from backend.agents.testing_agent import test_agent
from backend.agents.dependency_agent import dependency_agent

from backend.agents.environment_config_agent import (
    environment_config_agent
)

from backend.agents.integration_validation_agent import (
    integration_validation_agent
)

from backend.agents.diagram_agent import diagram_agent
from backend.agents.infrastructure_agent import infrastructure_agent
from backend.agents.terraform_agent import terraform_agent
from backend.agents.validation_agent import validation_agent
from backend.agents.self_correction_agent import self_correction_agent


def validation_router(state: AgentState):

    architecture = state.get(
        "architecture",
        {}
    )

    validation = architecture.get(
        "validation",
        {}
    )

    status = validation.get(
        "status",
        "INVALID"
    )

    if status == "VALID":
        return "memory_sync"

    correction_attempts = state.get(
        "correction_attempts",
        0
    )

    max_correction_attempts = state.get(
        "max_correction_attempts",
        3
    )

    if correction_attempts < max_correction_attempts:
        return "self_correction"

    return "memory_sync"


def memory_sync_node(state: AgentState):
    """
    Synchronize the complete generated project
    into Project Memory after final validation.
    """

    state = sync_project_memory(state)

    memory = state.get(
        "project_memory",
        {}
    )

    history = memory.setdefault(
        "history",
        []
    )

    validation = state.get(
        "architecture",
        {}
    ).get(
        "validation",
        {}
    )

    history.append(
        {
            "event": "Project Validation Completed",
            "details": {
                "status": validation.get(
                    "status",
                    "UNKNOWN"
                ),
                "summary": validation.get(
                    "summary",
                    ""
                )
            }
        }
    )

    state["project_memory"] = memory

    return state


def build_agent_graph():

    graph_builder = StateGraph(AgentState)

    # --------------------------------------------------
    # Initialize Project Memory
    # --------------------------------------------------

    graph_builder.add_node(
        "initialize",
        lambda state: {
            **state,
            "project_memory": create_project_memory(state)
        }
    )

    # --------------------------------------------------
    # Core Agents
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Plugin / Tool Agent
    # --------------------------------------------------

    graph_builder.add_node(
        "plugin_tool",
        plugin_tool_agent
    )

    # --------------------------------------------------
    # Code Generation Contract
    # --------------------------------------------------

    graph_builder.add_node(
        "code_generation_contract",
        code_generation_contract_agent
    )

    graph_builder.add_node(
        "code_quality",
        code_quality_agent
    )

    graph_builder.add_node(
        "test",
        test_agent
    )

    # --------------------------------------------------
    # Dependency Agent
    # --------------------------------------------------

    graph_builder.add_node(
        "dependency",
        dependency_agent
    )

    # --------------------------------------------------
    # Environment Configuration Agent
    # --------------------------------------------------

    graph_builder.add_node(
        "environment_config",
        environment_config_agent
    )

    # --------------------------------------------------
    # Integration Validation
    # --------------------------------------------------

    graph_builder.add_node(
        "integration_validation",
        integration_validation_agent
    )

    # --------------------------------------------------
    # Diagram / Infrastructure / Terraform
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Final Validation
    # --------------------------------------------------

    graph_builder.add_node(
        "validation",
        validation_agent
    )

    # --------------------------------------------------
    # Self-Correction
    # --------------------------------------------------

    graph_builder.add_node(
        "self_correction",
        self_correction_agent
    )

    # --------------------------------------------------
    # Project Memory Synchronization
    # --------------------------------------------------

    graph_builder.add_node(
        "memory_sync",
        memory_sync_node
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

    # --------------------------------------------------
    # Plugin / Tool Agent
    # --------------------------------------------------

    graph_builder.add_edge(
        "integration",
        "plugin_tool"
    )

    # --------------------------------------------------
    # Code Generation Contract
    # --------------------------------------------------

    graph_builder.add_edge(
        "plugin_tool",
        "code_generation_contract"
    )

    graph_builder.add_edge(
        "code_generation_contract",
        "code_quality"
    )

    graph_builder.add_edge(
        "code_quality",
        "test"
    )

    # --------------------------------------------------
    # Dependency
    # --------------------------------------------------

    graph_builder.add_edge(
        "test",
        "dependency"
    )

    # --------------------------------------------------
    # Environment Configuration
    # --------------------------------------------------

    graph_builder.add_edge(
        "dependency",
        "environment_config"
    )

    # --------------------------------------------------
    # Cross-Agent Validation
    # --------------------------------------------------

    graph_builder.add_edge(
        "environment_config",
        "integration_validation"
    )

    # --------------------------------------------------
    # Diagram
    # --------------------------------------------------

    graph_builder.add_edge(
        "integration_validation",
        "diagram"
    )

    # --------------------------------------------------
    # Infrastructure
    # --------------------------------------------------

    graph_builder.add_edge(
        "diagram",
        "infrastructure"
    )

    # --------------------------------------------------
    # Terraform
    # --------------------------------------------------

    graph_builder.add_edge(
        "infrastructure",
        "terraform"
    )

    # --------------------------------------------------
    # Final Validation
    # --------------------------------------------------

    graph_builder.add_edge(
        "terraform",
        "validation"
    )

    # --------------------------------------------------
    # Validation Routing
    # --------------------------------------------------

    graph_builder.add_conditional_edges(
        "validation",
        validation_router,
        {
            "self_correction": "self_correction",
            "memory_sync": "memory_sync"
        }
    )

    # --------------------------------------------------
    # Self-Correction → Validation
    # --------------------------------------------------

    graph_builder.add_edge(
        "self_correction",
        "validation"
    )

    # --------------------------------------------------
    # Memory Sync → End
    # --------------------------------------------------

    graph_builder.add_edge(
        "memory_sync",
        END
    )

    # --------------------------------------------------
    # Compile Graph
    # --------------------------------------------------

    return graph_builder.compile()