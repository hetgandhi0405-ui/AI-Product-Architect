from langgraph.graph import END, StateGraph

from backend.agents.api_spec_agent import api_spec_agent
from backend.agents.architecture_agent import architecture_agent
from backend.agents.architecture_alternatives_agent import architecture_alternatives_agent
from backend.agents.architecture_evaluator_agent import architecture_evaluator_agent
from backend.agents.architecture_knowledge_graph_agent import architecture_knowledge_graph_agent
from backend.agents.code_generation_contract_agent import (
    code_generation_contract_agent,
)
from backend.agents.code_quality_agent import code_quality_agent
from backend.agents.database_spec_agent import database_spec_agent
from backend.agents.dependency_agent import dependency_agent
from backend.agents.diagram_agent import diagram_agent
from backend.agents.dynamic_router_agent import dynamic_router_agent
from backend.agents.digital_twin_agent import digital_twin_agent
from backend.agents.what_if_engine_agent import what_if_engine_agent
from backend.agents.architecture_simulator_agent import architecture_simulator_agent
from backend.agents.environment_config_agent import environment_config_agent
from backend.agents.infrastructure_agent import infrastructure_agent
from backend.agents.integration_agent import integration_agent
from backend.agents.integration_validation_agent import (
    integration_validation_agent,
)
from backend.agents.monitoring_agent import monitoring_agent
from backend.agents.failure_detection_agent import failure_detection_agent
from backend.agents.memory_manager import (
    create_project_memory,
    sync_project_memory,
)
from backend.agents.plugin_tool_agent import plugin_tool_agent
from backend.agents.product_planner_agent import product_planner_agent
from backend.agents.requirement_agent import requirement_agent
from backend.agents.self_correction_agent import self_correction_agent
from backend.agents.security_agent import security_agent
from backend.agents.suggestion_agent import suggestion_agent
from backend.agents.terraform_agent import terraform_agent
from backend.agents.testing_agent import test_agent
from backend.agents.ui_ux_spec_agent import ui_ux_spec_agent
from backend.agents.file_manifest_agent import file_manifest_agent
from backend.agents.code_generation_agent import code_generation_agent
from backend.agents.file_assembler_agent import file_assembler_agent
from backend.agents.generated_code_validator_agent import (
    generated_code_validator_agent,
)
from backend.agents.generated_code_self_correction_agent import (
    generated_code_self_correction_agent,
)
from backend.agents.project_build_agent import project_build_agent
from backend.agents.api_contract_testing_agent import (
    api_contract_testing_agent,
)
from backend.agents.database_integration_testing_agent import (
    database_integration_testing_agent,
)
from backend.agents.docker_runtime_testing_agent import (
    docker_runtime_testing_agent,
)
from backend.agents.integration_self_correction_agent import (
    integration_self_correction_agent,
)
from backend.agents.release_gate_agent import release_gate_agent
from backend.agents.project_export_agent import project_export_agent
from backend.agents.validation_agent import validation_agent

from backend.agents.docker_build_agent import docker_build_agent
from backend.agents.container_registry_agent import container_registry_agent
from backend.agents.cloud_deployment_agent import cloud_deployment_agent
from backend.agents.deployment_validation_agent import deployment_validation_agent
from backend.agents.telemetry_agent import telemetry_agent
from backend.agents.performance_agent import performance_agent
from backend.agents.cost_agent import cost_agent
from backend.agents.reliability_agent import reliability_agent
from backend.agents.architecture_analysis_agent import architecture_analysis_agent
from backend.agents.candidate_generation_agent import candidate_generation_agent
from backend.agents.candidate_evaluation_agent import candidate_evaluation_agent
from backend.agents.optimization_recommendation_agent import optimization_recommendation_agent

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

    state["tool_registry"] = state.get(
        "tool_registry",
        {},
    )

    state["selected_tools"] = state.get(
        "selected_tools",
        {},
    )

    state["code_correction_attempts"] = state.get(
        "code_correction_attempts",
        0,
    )

    state["max_code_correction_attempts"] = state.get(
        "max_code_correction_attempts",
        3,
    )

    state["integration_correction_attempts"] = state.get(
        "integration_correction_attempts",
        0,
    )

    state["max_integration_correction_attempts"] = state.get(
        "max_integration_correction_attempts",
        2,
    )

    state["generated_files"] = state.get(
        "generated_files",
        {},
    )

    state["file_manifest"] = state.get(
        "file_manifest",
        {},
    )

    state["deploy_mode"] = state.get("deploy_mode", "dry-run")
    state["docker_status"] = state.get("docker_status", "SKIPPED")
    state["registry_status"] = state.get("registry_status", "SKIPPED")
    state["deployment_status"] = state.get("deployment_status", "SKIPPED")
    state["terraform_status"] = state.get("terraform_status", "SKIPPED")
    state["deployment_validation_status"] = state.get("deployment_validation_status", "SKIPPED")
    state["health_status"] = state.get("health_status", "INSUFFICIENT_DATA")
    state["telemetry_status"] = state.get("telemetry_status", "SKIPPED")
    state["service_url"] = state.get("service_url", None)

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
        return "monitoring"

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


def code_validation_router(state: AgentState):
    """
    Decide whether to self-correct code syntax/structure errors
    or proceed to build validation.
    """
    val = state.get("code_validation", {})
    if val.get("status") == "PASS":
        return "project_build"

    attempts = state.get("code_correction_attempts", 0)
    max_attempts = state.get("max_code_correction_attempts", 3)

    if attempts < max_attempts:
        return "generated_code_self_correction"

    return "project_build"


def integration_validation_router(state: AgentState):
    """
    Decide whether to repair API/DB/Docker integration mismatches
    or proceed to the release gate.
    """
    api_val = state.get("api_validation", {})
    db_val = state.get("database_validation", {})
    docker_val = state.get("docker_validation", {})

    all_passed = (
        api_val.get("status") in ("PASS", "WARN") and
        db_val.get("status") in ("PASS", "WARN") and
        docker_val.get("status") == "PASS"
    )

    if all_passed:
        return "release_gate"

    attempts = state.get("integration_correction_attempts", 0)
    max_attempts = state.get("max_integration_correction_attempts", 2)

    if attempts < max_attempts:
        return "integration_self_correction"

    return "release_gate"


def release_gate_router(state: AgentState):
    """
    If release gate approved, proceed to docker build; otherwise skip to project export.
    """
    gate = state.get("release_gate", {})
    if gate.get("status") == "APPROVED" and gate.get("approved"):
        return "docker_build"
    return "project_export"


def docker_build_router(state: AgentState):
    """
    If docker build failed, abort deployment pipeline and summarize; else proceed to container registry.
    """
    if state.get("docker_status") == "FAILED":
        return "deployment_failed_summary"
    return "container_registry"


def container_registry_router(state: AgentState):
    """
    If container registry push failed, abort deployment pipeline and summarize; else proceed to cloud deployment.
    """
    if state.get("registry_status") == "FAILED":
        return "deployment_failed_summary"
    return "cloud_deployment"


def cloud_deployment_router(state: AgentState):
    """
    If cloud deployment failed, abort to summary; else proceed to deployment validation.
    """
    if state.get("deployment_status") == "FAILED":
        return "deployment_failed_summary"
    return "deployment_validation"


def deployment_failed_summary_agent(state: AgentState) -> AgentState:
    """
    Record deployment failure summary without crashing, ensuring export continues.
    """
    state["deployment_status"] = "FAILED"
    state["service_url"] = None
    state["deployment_validation_status"] = "FAILED"
    state["health_status"] = "UNHEALTHY"
    return state


from backend.core.execution_config import get_execution_config
from backend.core.pipeline_metrics import (
    create_metrics,
    finish_node,
    skip_node,
    start_node,
)


def timed_conditional_node(node_name, node_fn):
    def wrapped(state: AgentState):
        execution_mode = state.get("execution_mode", "FULL")
        metrics = state.get("pipeline_metrics") or create_metrics()
        state["execution_mode"] = execution_mode
        state["pipeline_metrics"] = metrics
        config = get_execution_config(execution_mode)
        if not config.should_run(node_name):
            skip_node(metrics, node_name)
            return state
        routing = state.get("dynamic_routing") or {}
        skipped_agents = set(routing.get("skipped_agents", []) if isinstance(routing, dict) else [])
        if node_name in config.dynamically_routable_nodes and node_name in skipped_agents:
            skip_node(metrics, node_name)
            return state
        started = start_node(metrics, node_name)
        try:
            output = node_fn(state)
        except Exception:
            finish_node(metrics, node_name, started, status="FAILED")
            raise
        finish_node(metrics, node_name, started)
        if output is None:
            output = state
        output["execution_mode"] = execution_mode
        output["pipeline_metrics"] = metrics
        return output
    return wrapped


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
        "architecture_alternatives",
        architecture_alternatives_agent,
    )

    graph_builder.add_node(
        "architecture_evaluator",
        architecture_evaluator_agent,
    )

    graph_builder.add_node(
        "architecture_knowledge_graph",
        architecture_knowledge_graph_agent,
    )

    graph_builder.add_node(
        "digital_twin",
        digital_twin_agent,
    )

    graph_builder.add_node(
        "what_if_engine",
        what_if_engine_agent,
    )

    graph_builder.add_node(
        "architecture_simulator",
        architecture_simulator_agent,
    )

    graph_builder.add_node(
        "security",
        security_agent,
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
    # DAY 32 - INFRASTRUCTURE MONITORING
    # =========================================================

    graph_builder.add_node(
        "monitoring",
        monitoring_agent,
    )

    graph_builder.add_node(
        "failure_detection",
        failure_detection_agent,
    )

    # =========================================================
    # CODE DELIVERY PIPELINE NODES
    # =========================================================

    graph_builder.add_node(
        "file_manifest",
        file_manifest_agent,
    )

    graph_builder.add_node(
        "code_generation",
        code_generation_agent,
    )

    graph_builder.add_node(
        "file_assembler",
        file_assembler_agent,
    )

    graph_builder.add_node(
        "generated_code_validator",
        generated_code_validator_agent,
    )

    graph_builder.add_node(
        "generated_code_self_correction",
        generated_code_self_correction_agent,
    )

    graph_builder.add_node(
        "project_build",
        project_build_agent,
    )

    graph_builder.add_node(
        "api_contract_testing",
        api_contract_testing_agent,
    )

    graph_builder.add_node(
        "database_integration_testing",
        database_integration_testing_agent,
    )

    graph_builder.add_node(
        "docker_runtime_testing",
        docker_runtime_testing_agent,
    )

    graph_builder.add_node(
        "integration_self_correction",
        integration_self_correction_agent,
    )

    graph_builder.add_node(
        "release_gate",
        release_gate_agent,
    )

    graph_builder.add_node(
        "project_export",
        project_export_agent,
    )

    # =========================================================
    # DEPLOYMENT, TELEMETRY, AND OPTIMIZATION NODES
    # =========================================================

    graph_builder.add_node(
        "docker_build",
        docker_build_agent,
    )

    graph_builder.add_node(
        "container_registry",
        container_registry_agent,
    )

    graph_builder.add_node(
        "cloud_deployment",
        cloud_deployment_agent,
    )

    graph_builder.add_node(
        "deployment_validation",
        deployment_validation_agent,
    )

    graph_builder.add_node(
        "telemetry",
        telemetry_agent,
    )

    graph_builder.add_node(
        "performance",
        performance_agent,
    )

    graph_builder.add_node(
        "cost",
        cost_agent,
    )

    graph_builder.add_node(
        "reliability",
        reliability_agent,
    )

    graph_builder.add_node(
        "architecture_analysis",
        architecture_analysis_agent,
    )

    graph_builder.add_node(
        "candidate_generation",
        candidate_generation_agent,
    )

    graph_builder.add_node(
        "candidate_evaluation",
        candidate_evaluation_agent,
    )

    graph_builder.add_node(
        "optimization_recommendation",
        optimization_recommendation_agent,
    )

    graph_builder.add_node(
        "deployment_failed_summary",
        deployment_failed_summary_agent,
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
        "architecture_alternatives",
    )

    graph_builder.add_edge(
        "architecture_alternatives",
        "architecture_evaluator",
    )

    graph_builder.add_edge(
        "architecture_evaluator",
        "architecture_knowledge_graph",
    )

    graph_builder.add_edge(
        "architecture_knowledge_graph",
        "digital_twin",
    )

    graph_builder.add_edge(
        "digital_twin",
        "what_if_engine",
    )

    graph_builder.add_edge(
        "what_if_engine",
        "architecture_simulator",
    )

    graph_builder.add_edge(
        "architecture_simulator",
        "security",
    )

    graph_builder.add_edge(
        "security",
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
    # DAY 32 - INFRASTRUCTURE MONITORING PIPELINE
    # =========================================================

    graph_builder.add_edge(
        "monitoring",
        "failure_detection",
    )

    # =========================================================
    # VALIDATION LOOP
    # =========================================================

    graph_builder.add_conditional_edges(
        "validation",
        validation_router,
        {
            "self_correction": "self_correction",
            "monitoring": "monitoring",
            "memory_sync": "memory_sync",
        },
    )

    graph_builder.add_edge(
        "self_correction",
        "validation",
    )

    graph_builder.add_edge(
        "failure_detection",
        "memory_sync",
    )
    # =========================================================
    # CODE DELIVERY PIPELINE EDGES
    # =========================================================

    graph_builder.add_edge(
        "memory_sync",
        "file_manifest",
    )

    graph_builder.add_edge(
        "file_manifest",
        "code_generation",
    )

    graph_builder.add_edge(
        "code_generation",
        "file_assembler",
    )

    graph_builder.add_edge(
        "file_assembler",
        "generated_code_validator",
    )

    graph_builder.add_conditional_edges(
        "generated_code_validator",
        code_validation_router,
        {
            "generated_code_self_correction": "generated_code_self_correction",
            "project_build": "project_build",
        },
    )

    graph_builder.add_edge(
        "generated_code_self_correction",
        "project_build",
    )

    graph_builder.add_edge(
        "project_build",
        "api_contract_testing",
    )

    graph_builder.add_edge(
        "api_contract_testing",
        "database_integration_testing",
    )

    graph_builder.add_edge(
        "database_integration_testing",
        "docker_runtime_testing",
    )

    graph_builder.add_conditional_edges(
        "docker_runtime_testing",
        integration_validation_router,
        {
            "integration_self_correction": "integration_self_correction",
            "release_gate": "release_gate",
        },
    )

    graph_builder.add_edge(
        "integration_self_correction",
        "release_gate",
    )

    # =========================================================
    # DEPLOYMENT, MONITORING, AND OPTIMIZATION PIPELINE EDGES
    # =========================================================

    graph_builder.add_conditional_edges(
        "release_gate",
        release_gate_router,
        {
            "docker_build": "docker_build",
            "project_export": "project_export",
        },
    )

    graph_builder.add_conditional_edges(
        "docker_build",
        docker_build_router,
        {
            "container_registry": "container_registry",
            "deployment_failed_summary": "deployment_failed_summary",
        },
    )

    graph_builder.add_conditional_edges(
        "container_registry",
        container_registry_router,
        {
            "cloud_deployment": "cloud_deployment",
            "deployment_failed_summary": "deployment_failed_summary",
        },
    )

    graph_builder.add_conditional_edges(
        "cloud_deployment",
        cloud_deployment_router,
        {
            "deployment_validation": "deployment_validation",
            "deployment_failed_summary": "deployment_failed_summary",
        },
    )

    graph_builder.add_edge(
        "deployment_validation",
        "telemetry",
    )

    graph_builder.add_edge(
        "telemetry",
        "performance",
    )

    graph_builder.add_edge(
        "performance",
        "cost",
    )

    graph_builder.add_edge(
        "cost",
        "reliability",
    )

    graph_builder.add_edge(
        "reliability",
        "architecture_analysis",
    )

    graph_builder.add_edge(
        "architecture_analysis",
        "candidate_generation",
    )

    graph_builder.add_edge(
        "candidate_generation",
        "candidate_evaluation",
    )

    graph_builder.add_edge(
        "candidate_evaluation",
        "optimization_recommendation",
    )

    graph_builder.add_edge(
        "optimization_recommendation",
        "project_export",
    )

    graph_builder.add_edge(
        "deployment_failed_summary",
        "project_export",
    )

    graph_builder.add_edge(
        "project_export",
        END,
    )

    return graph_builder.compile()


# Compiled LangGraph application instance
app = build_agent_graph()