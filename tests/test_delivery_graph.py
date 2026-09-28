from backend.agents.graph import build_agent_graph


def test_delivery_graph_contains_release_pipeline():
    graph = build_agent_graph()
    nodes = set(graph.nodes)

    required = {
        "file_manifest",
        "code_generation",
        "file_assembler",
        "generated_code_validation",
        "project_build",
        "api_contract_testing",
        "database_integration_testing",
        "docker_runtime_testing",
        "integration_self_correction",
        "release_gate",
        "project_export",
    }

    assert required.issubset(nodes)
