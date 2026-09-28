from backend.agents.docker_runtime_testing_agent import docker_runtime_testing_agent


def test_docker_runtime_configuration_passes(tmp_path, monkeypatch):
    monkeypatch.delenv("AI_PRODUCT_ARCHITECT_RUN_DOCKER_TESTS", raising=False)
    (tmp_path / "docker-compose.yml").write_text(
        "services:\n  backend:\n    build: .\n",
        encoding="utf-8",
    )
    (tmp_path / "Dockerfile").write_text(
        "FROM python:3.12-slim\n",
        encoding="utf-8",
    )
    result = docker_runtime_testing_agent({"generated_project_path": str(tmp_path)})
    assert result["docker_runtime_validation"]["status"] == "VALID"
    assert result["docker_runtime_validation"]["executed_docker_command"] is False


def test_docker_runtime_detects_invalid_compose(tmp_path, monkeypatch):
    monkeypatch.delenv("AI_PRODUCT_ARCHITECT_RUN_DOCKER_TESTS", raising=False)
    (tmp_path / "docker-compose.yml").write_text("version: '3'\n", encoding="utf-8")
    result = docker_runtime_testing_agent({"generated_project_path": str(tmp_path)})
    assert result["docker_runtime_validation"]["status"] == "INVALID"
    assert any("services" in item for item in result["docker_runtime_validation"]["issues"])
