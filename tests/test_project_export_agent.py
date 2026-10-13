import os
import zipfile
import pytest
from pathlib import Path
from backend.agents.project_export_agent import project_export_agent
from backend.agents.state import AgentState


def test_project_export_excludes_secrets_and_terraform_state(tmp_path):
    project_dir = tmp_path / "my_project"
    project_dir.mkdir()

    # Valid files
    (project_dir / "main.py").write_text("print('hello')", encoding="utf-8")
    (project_dir / "README.md").write_text("# Project", encoding="utf-8")

    # Sensitive/state files that must be excluded
    (project_dir / ".env").write_text("SECRET=12345", encoding="utf-8")
    (project_dir / "terraform.tfstate").write_text("{\"version\": 4}", encoding="utf-8")
    (project_dir / "terraform.tfstate.backup").write_text("{}", encoding="utf-8")
    tf_dir = project_dir / ".terraform"
    tf_dir.mkdir()
    (tf_dir / "providers.bin").write_bytes(b"\x00\x01\x02")

    state = AgentState(
        project_id="test-exclusions-123",
        assembled_project_path=str(project_dir),
        release_gate={"status": "APPROVED", "approved": True},
    )

    result = project_export_agent(state)
    assert result["export"]["status"] == "SUCCESS"
    zip_path = Path(result["export"]["zip_path"])
    assert zip_path.exists()

    with zipfile.ZipFile(zip_path, "r") as zf:
        namelist = zf.namelist()
        assert "main.py" in namelist
        assert "README.md" in namelist

        # Rule check: state and .env excluded
        assert ".env" not in namelist
        assert "terraform.tfstate" not in namelist
        assert "terraform.tfstate.backup" not in namelist
        assert not any(".terraform" in name for name in namelist)
