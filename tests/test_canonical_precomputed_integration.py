import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.project_catalog import CANONICAL_PROJECTS, match_canonical_project
import os

client = TestClient(app)

def test_canonical_catalog_has_all_ten():
    assert len(CANONICAL_PROJECTS) == 10
    for item in CANONICAL_PROJECTS:
        assert "key" in item
        assert "project_id" in item
        assert "canonical_prompt" in item
        assert "project_name" in item
        assert "domain_id" in item

@pytest.mark.parametrize("spec", CANONICAL_PROJECTS)
def test_precomputed_data_exists_on_disk(spec):
    key = spec["key"]
    precomputed_dir = os.path.join("data", "precomputed", key)
    assert os.path.isdir(precomputed_dir), f"Directory missing for {key}"
    
    # Required files
    assert os.path.isfile(os.path.join(precomputed_dir, "result.json"))
    assert os.path.isfile(os.path.join(precomputed_dir, "requirements.json"))
    assert os.path.isfile(os.path.join(precomputed_dir, "architecture.mmd"))
    assert os.path.isfile(os.path.join(precomputed_dir, "validation-report.json"))
    assert os.path.isfile(os.path.join(precomputed_dir, "project.zip"))

@pytest.mark.parametrize("spec", CANONICAL_PROJECTS)
def test_matching_canonical_prompt_returns_ready_project(spec):
    key = spec["key"]
    prompt = spec["canonical_prompt"]
    match = match_canonical_project(prompt)
    assert match is not None
    assert match["key"] == key

    # Test sync process_requirement endpoint
    res = client.post("/api/requirements/", json={
        "description": prompt,
        "project_name": spec["project_name"],
        "project_id": spec["project_id"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["project_id"] == spec["project_id"]
    assert 80.0 <= data["coverage"] <= 95.0
    assert "architecture_diagram" in data
    assert "classDiagram" in data["architecture_diagram"] or "flowchart" in data["architecture_diagram"] or "graph" in data["architecture_diagram"]
    assert data["release_gate"]["status"] == "APPROVED"
    assert data["download_url"] == f"/api/requirements/export/{spec['project_id']}"
    assert data["service_url"] == f"/preview/{spec['project_id']}"
    assert len(data.get("code_generation", {}).get("files", {})) >= 15

    # Test zip download endpoint
    zip_res = client.get(f"/api/requirements/export/{spec['project_id']}")
    assert zip_res.status_code == 200
    assert len(zip_res.content) > 1000

    # Test live preview endpoint
    preview_res = client.get(f"/preview/{spec['project_id']}")
    assert preview_res.status_code == 200
    assert "text/html" in preview_res.headers.get("content-type", "")
    assert spec["project_name"] in preview_res.text
