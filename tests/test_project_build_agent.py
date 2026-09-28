from pathlib import Path

from backend.agents.project_build_agent import project_build_agent


def test_project_build_agent_compiles_generated_python(tmp_path, monkeypatch):
    monkeypatch.delenv("AI_PRODUCT_ARCHITECT_RUN_GENERATED_BUILDS", raising=False)

    root = tmp_path / "project"
    (root / "backend").mkdir(parents=True)
    (root / "backend" / "main.py").write_text(
        "print('generated project')\n",
        encoding="utf-8",
    )

    state = {
        "project_id": "build-test",
        "generated_project_path": str(root),
        "file_manifest": {
            "files": [
                {"path": "backend/main.py", "kind": "source"},
            ]
        },
    }

    result = project_build_agent(state)

    assert result["project_build"]["status"] == "PASSED"
    assert result["project_build"]["executed_generated_builds"] is False


def test_project_build_agent_reports_missing_manifest_file(tmp_path, monkeypatch):
    monkeypatch.delenv("AI_PRODUCT_ARCHITECT_RUN_GENERATED_BUILDS", raising=False)

    root = tmp_path / "project"
    root.mkdir()

    state = {
        "project_id": "build-test",
        "generated_project_path": str(root),
        "file_manifest": {
            "files": [
                {"path": "backend/main.py", "kind": "source"},
            ]
        },
    }

    result = project_build_agent(state)

    assert result["project_build"]["status"] == "FAILED"
    assert "backend/main.py" in result["project_build"]["issues"][0]
