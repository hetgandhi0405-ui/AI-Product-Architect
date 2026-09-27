from backend.agents.release_gate_agent import release_gate_agent


def test_release_gate_approves_valid_project():
    state = {
        "generated_code_validation": {"status": "VALID"},
        "project_build": {"status": "PASSED"},
        "api_contract_validation": {"status": "VALID"},
        "database_integration_validation": {"status": "VALID"},
        "docker_runtime_validation": {"status": "VALID"},
    }
    result = release_gate_agent(state)
    assert result["release_gate"]["status"] == "APPROVED"
    assert result["release_gate"]["is_releasable"] is True


def test_release_gate_blocks_invalid_project():
    state = {
        "generated_code_validation": {"status": "VALID"},
        "project_build": {"status": "PASSED"},
        "api_contract_validation": {"status": "INVALID", "issues": ["route mismatch"]},
        "database_integration_validation": {"status": "VALID"},
        "docker_runtime_validation": {"status": "VALID"},
    }
    result = release_gate_agent(state)
    assert result["release_gate"]["status"] == "BLOCKED"
    assert result["release_gate"]["is_releasable"] is False
    assert result["release_gate"]["failures"][0]["stage"] == "api_contract"
