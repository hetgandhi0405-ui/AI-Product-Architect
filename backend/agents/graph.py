from langgraph.graph import END, StateGraph

from backend.agents.api_spec_agent import api_spec_agent
from backend.agents.architecture_agent import architecture_agent
from backend.agents.architecture_alternatives_agent import architecture_alternatives_agent
from backend.agents.architecture_evaluator_agent import architecture_evaluator_agent
from backend.agents.architecture_knowledge_graph_agent import architecture_knowledge_graph_agent
from backend.agents.architecture_recommendation_agent import architecture_recommendation_agent
from backend.agents.code_generation_contract_agent import code_generation_contract_agent
from backend.agents.file_manifest_agent import file_manifest_agent
from backend.agents.code_generation_agent import code_generation_agent
from backend.agents.file_assembler_agent import file_assembler_agent
from backend.agents.generated_code_validator_agent import generated_code_validator_agent
from backend.agents.generated_code_self_correction_agent import generated_code_self_correction_agent
from backend.agents.project_export_agent import project_export_agent
from backend.agents.project_build_agent import project_build_agent
from backend.agents.api_contract_testing_agent import api_contract_testing_agent
from backend.agents.database_integration_testing_agent import database_integration_testing_agent
from backend.agents.docker_runtime_testing_agent import docker_runtime_testing_agent
from backend.agents.integration_self_correction_agent import integration_self_correction_agent
from backend.agents.release_gate_agent import release_gate_agent
from backend.agents.code_quality_agent import code_quality_agent
from backend.agents.cost_intelligence_agent import cost_intelligence_agent
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
from backend.agents.integration_validation_agent import integration_validation_agent
from backend.agents.monitoring_agent import monitoring_agent
from backend.agents.failure_detection_agent import failure_detection_agent
from backend.agents.memory_manager import create_project_memory, sync_project_memory
from backend.agents.plugin_tool_agent import plugin_tool_agent
from backend.agents.product_planner_agent import product_planner_agent
from backend.agents.requirement_agent import requirement_agent
from backend.agents.requirement_traceability_agent import requirement_traceability_agent
from backend.agents.self_correction_agent import self_correction_agent
from backend.agents.security_agent import security_agent
from backend.agents.suggestion_agent import suggestion_agent
from backend.agents.terraform_agent import terraform_agent
from backend.agents.testing_agent import test_agent
from backend.agents.ui_ux_spec_agent import ui_ux_spec_agent
from backend.agents.validation_agent import validation_agent
from backend.agents.state import AgentState
from backend.core.execution_config import get_execution_config
from backend.core.pipeline_metrics import create_metrics, finish_node, finish_pipeline, skip_node, start_node


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
        if node_name == "memory_sync":
            finish_pipeline(metrics)
        return output

    return wrapped


def initialize_node(state: AgentState):
    state["correction_attempts"] = state.get("correction_attempts", 0)
    state["max_correction_attempts"] = state.get("max_correction_attempts", 3)
    state["suggestions"] = state.get("suggestions", [])
    state["architecture"] = state.get("architecture", {})
    state["tool_registry"] = state.get("tool_registry", {})
    state["selected_tools"] = state.get("selected_tools", {})
    state["project_memory"] = create_project_memory(state)
    return state


def dynamic_router_node(state: AgentState):
    result = dynamic_router_agent(state)
    routing = result.get("dynamic_routing", {})
    state["dynamic_routing"] = routing
    architecture = state.get("architecture", {})
    architecture["dynamic_routing"] = routing
    state["architecture"] = architecture
    return state


def memory_sync_node(state: AgentState):
    state = sync_project_memory(state)
    memory = state.get("project_memory", {})
    history = memory.setdefault("history", [])
    validation = state.get("architecture", {}).get("validation", {})
    history.append({"event": "Project Validation Completed", "details": {"status": validation.get("status", "UNKNOWN"), "summary": validation.get("summary", "")}})
    state["project_memory"] = memory
    return state


def validation_router(state: AgentState):
    validation = state.get("architecture", {}).get("validation", {})
    if validation.get("status", "INVALID") == "VALID":
        return "file_manifest"
    attempts = state.get("correction_attempts", 0)
    if attempts >= state.get("max_correction_attempts", 3):
        return "file_manifest"
    return "self_correction"


def generated_code_validation_router(state: AgentState):
    validation = state.get("generated_code_validation", {})
    if validation.get("status") == "VALID":
        return "project_build"
    attempts = state.get("generated_code_correction_attempts", 0)
    if attempts >= state.get("max_generated_code_correction_attempts", 3):
        return "project_build"
    return "generated_code_self_correction"


def integration_validation_router(state: AgentState):
    validations = [state.get("project_build", {}), state.get("api_contract_validation", {}), state.get("database_integration_validation", {}), state.get("docker_runtime_validation", {})]
    if all(item.get("status") in ("PASSED", "VALID") for item in validations):
        return "release_gate"
    attempts = state.get("integration_correction_attempts", 0)
    if attempts >= state.get("max_integration_correction_attempts", 2):
        return "release_gate"
    return "integration_self_correction"


def release_gate_router(state: AgentState):
    if state.get("release_gate", {}).get("status") == "APPROVED":
        return "project_export"
    return "memory_sync"


def build_agent_graph():
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("initialize", timed_conditional_node("initialize", initialize_node))
    graph_builder.add_node("dynamic_router", timed_conditional_node("dynamic_router", dynamic_router_node))
    graph_builder.add_node("requirement", timed_conditional_node("requirement", requirement_agent))
    graph_builder.add_node("suggestion", timed_conditional_node("suggestion", suggestion_agent))
    graph_builder.add_node("product_planner", timed_conditional_node("product_planner", product_planner_agent))
    graph_builder.add_node("ui_ux_spec", timed_conditional_node("ui_ux_spec", ui_ux_spec_agent))
    graph_builder.add_node("api_spec", timed_conditional_node("api_spec", api_spec_agent))
    graph_builder.add_node("database_spec", timed_conditional_node("database_spec", database_spec_agent))
    graph_builder.add_node("architecture", timed_conditional_node("architecture", architecture_agent))
    graph_builder.add_node("architecture_alternatives", timed_conditional_node("architecture_alternatives", architecture_alternatives_agent))
    graph_builder.add_node("architecture_evaluator", timed_conditional_node("architecture_evaluator", architecture_evaluator_agent))
    graph_builder.add_node("architecture_knowledge_graph", timed_conditional_node("architecture_knowledge_graph", architecture_knowledge_graph_agent))
    graph_builder.add_node("digital_twin", timed_conditional_node("digital_twin", digital_twin_agent))
    graph_builder.add_node("what_if_engine", timed_conditional_node("what_if_engine", what_if_engine_agent))
    graph_builder.add_node("architecture_simulator", timed_conditional_node("architecture_simulator", architecture_simulator_agent))
    graph_builder.add_node("security", timed_conditional_node("security", security_agent))
    graph_builder.add_node("cost_intelligence", timed_conditional_node("cost_intelligence", cost_intelligence_agent))
    graph_builder.add_node("architecture_recommendation", timed_conditional_node("architecture_recommendation", architecture_recommendation_agent))
    graph_builder.add_node("integration", timed_conditional_node("integration", integration_agent))
    graph_builder.add_node("plugin_tool", timed_conditional_node("plugin_tool", plugin_tool_agent))
    graph_builder.add_node("code_generation_contract", timed_conditional_node("code_generation_contract", code_generation_contract_agent))
    graph_builder.add_node("file_manifest", timed_conditional_node("file_manifest", file_manifest_agent))
    graph_builder.add_node("code_generation", timed_conditional_node("code_generation", code_generation_agent))
    graph_builder.add_node("file_assembler", timed_conditional_node("file_assembler", file_assembler_agent))
    graph_builder.add_node("generated_code_validation", timed_conditional_node("generated_code_validation", generated_code_validator_agent))
    graph_builder.add_node("generated_code_self_correction", timed_conditional_node("generated_code_self_correction", generated_code_self_correction_agent))
    graph_builder.add_node("project_build", timed_conditional_node("project_build", project_build_agent))
    graph_builder.add_node("api_contract_testing", timed_conditional_node("api_contract_testing", api_contract_testing_agent))
    graph_builder.add_node("database_integration_testing", timed_conditional_node("database_integration_testing", database_integration_testing_agent))
    graph_builder.add_node("docker_runtime_testing", timed_conditional_node("docker_runtime_testing", docker_runtime_testing_agent))
    graph_builder.add_node("integration_self_correction", timed_conditional_node("integration_self_correction", integration_self_correction_agent))
    graph_builder.add_node("release_gate", timed_conditional_node("release_gate", release_gate_agent))
    graph_builder.add_node("project_export", timed_conditional_node("project_export", project_export_agent))
    graph_builder.add_node("code_quality", timed_conditional_node("code_quality", code_quality_agent))
    graph_builder.add_node("test", timed_conditional_node("test", test_agent))
    graph_builder.add_node("dependency", timed_conditional_node("dependency", dependency_agent))
    graph_builder.add_node("requirement_traceability", timed_conditional_node("requirement_traceability", requirement_traceability_agent))
    graph_builder.add_node("environment_config", timed_conditional_node("environment_config", environment_config_agent))
    graph_builder.add_node("integration_validation", timed_conditional_node("integration_validation", integration_validation_agent))
    graph_builder.add_node("diagram", timed_conditional_node("diagram", diagram_agent))
    graph_builder.add_node("infrastructure", timed_conditional_node("infrastructure", infrastructure_agent))
    graph_builder.add_node("terraform", timed_conditional_node("terraform", terraform_agent))
    graph_builder.add_node("validation", timed_conditional_node("validation", validation_agent))
    graph_builder.add_node("self_correction", timed_conditional_node("self_correction", self_correction_agent))
    graph_builder.add_node("memory_sync", timed_conditional_node("memory_sync", memory_sync_node))
    graph_builder.add_node("monitoring", timed_conditional_node("monitoring", monitoring_agent))
    graph_builder.add_node("failure_detection", timed_conditional_node("failure_detection", failure_detection_agent))

    edges = [
        ("initialize", "dynamic_router"), ("dynamic_router", "requirement"), ("requirement", "suggestion"),
        ("suggestion", "product_planner"), ("product_planner", "ui_ux_spec"), ("ui_ux_spec", "api_spec"),
        ("api_spec", "database_spec"), ("database_spec", "architecture"), ("architecture", "architecture_alternatives"),
        ("architecture_alternatives", "architecture_evaluator"), ("architecture_evaluator", "architecture_knowledge_graph"),
        ("architecture_knowledge_graph", "digital_twin"), ("digital_twin", "what_if_engine"), ("what_if_engine", "architecture_simulator"),
        ("architecture_simulator", "security"), ("security", "cost_intelligence"), ("cost_intelligence", "architecture_recommendation"),
        ("architecture_recommendation", "integration"), ("integration", "plugin_tool"), ("plugin_tool", "code_generation_contract"),
        ("code_generation_contract", "code_quality"), ("code_quality", "test"), ("test", "requirement_traceability"),
        ("requirement_traceability", "dependency"), ("dependency", "environment_config"), ("environment_config", "integration_validation"),
        ("integration_validation", "diagram"), ("diagram", "infrastructure"), ("infrastructure", "terraform"), ("terraform", "validation"),
        ("file_manifest", "code_generation"), ("code_generation", "file_assembler"), ("file_assembler", "generated_code_validation"),
        ("generated_code_self_correction", "file_assembler"), ("project_build", "api_contract_testing"),
        ("api_contract_testing", "database_integration_testing"), ("database_integration_testing", "docker_runtime_testing"),
        ("integration_self_correction", "file_assembler"), ("project_export", "monitoring"),
        ("monitoring", "failure_detection"), ("failure_detection", "memory_sync"), ("self_correction", "validation"), ("memory_sync", END),
    ]
    for source, target in edges:
        graph_builder.add_edge(source, target)

    graph_builder.add_conditional_edges("validation", validation_router, {"self_correction": "self_correction", "file_manifest": "file_manifest"})
    graph_builder.add_conditional_edges("generated_code_validation", generated_code_validation_router, {"generated_code_self_correction": "generated_code_self_correction", "project_build": "project_build"})
    graph_builder.add_conditional_edges("docker_runtime_testing", integration_validation_router, {"integration_self_correction": "integration_self_correction", "release_gate": "release_gate"})
    graph_builder.add_conditional_edges("release_gate", release_gate_router, {"project_export": "project_export", "memory_sync": "memory_sync"})

    return graph_builder.compile()
