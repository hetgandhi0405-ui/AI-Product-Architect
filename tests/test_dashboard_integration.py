import pytest
from fastapi.testclient import TestClient
from backend.main import app
import zipfile
import io

client = TestClient(app)


def test_dashboard_routes():
    """Verify that all dashboard endpoints serve HTML correctly."""
    for path in ["/", "/ui", "/generator", "/dashboard"]:
        res = client.get(path)
        assert res.status_code == 200
        assert "Autonomous AI Product-to-Cloud Platform" in res.text
        assert "AI Product Architect" in res.text
        assert "Agent Pipeline Execution" in res.text


def test_projects_crud_lifecycle():
    """Verify projects listing, creation, fetch, and deletion."""
    # 1. Create a project
    payload = {
        "project_name": "Integration Test E-Commerce",
        "project_type": "Full Stack Web App",
        "requirements": "Build an online bookstore with FastAPI and PostgreSQL",
        "preferred_stack": "React, FastAPI, PostgreSQL",
    }
    create_res = client.post("/api/projects/", json=payload)
    assert create_res.status_code == 200
    created = create_res.json()
    assert created["success"] is True
    pid = created["project_id"]
    assert pid is not None

    # 2. Get list of projects
    list_res = client.get("/api/projects/")
    assert list_res.status_code == 200
    projects = list_res.json()
    assert isinstance(projects, list)
    matching = [p for p in projects if p["project_id"] == pid]
    assert len(matching) == 1
    assert matching[0]["project_name"] == "Integration Test E-Commerce"

    # 3. Get single project
    get_res = client.get(f"/api/projects/{pid}")
    assert get_res.status_code == 200
    single = get_res.json()
    assert single["project_id"] == pid

    # 4. Delete project
    del_res = client.delete(f"/api/projects/{pid}")
    assert del_res.status_code == 200
    assert del_res.json()["deleted"] is True

    # 5. Confirm deleted
    get_after_del = client.get(f"/api/projects/{pid}")
    assert get_after_del.status_code == 404


def test_export_zip_returns_valid_archive():
    """Verify that export endpoint returns a valid ZIP archive without error."""
    # First create a project record
    payload = {
        "project_name": "ZIP Download Test App",
        "requirements": "Build a task app",
    }
    create_res = client.post("/api/projects/", json=payload)
    pid = create_res.json()["project_id"]

    res = client.get(f"/api/requirements/export/{pid}")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"

    # Verify bytes form a valid zip
    buf = io.BytesIO(res.content)
    with zipfile.ZipFile(buf, "r") as zf:
        namelist = zf.namelist()
        assert len(namelist) > 0


def test_file_content_endpoint_and_security():
    """Verify safe file preview and path traversal protection."""
    payload = {
        "project_name": "File Preview Test App",
        "requirements": "Build a portal",
    }
    create_res = client.post("/api/projects/", json=payload)
    pid = create_res.json()["project_id"]

    # 1. Valid file preview
    res = client.get(f"/api/requirements/file-content/{pid}?path=backend/main.py")
    assert res.status_code == 200
    data = res.json()
    assert "content" in data
    assert data["path"] == "backend/main.py"

    # 2. Path traversal attack must be blocked with 403 Forbidden
    attack_res = client.get(f"/api/requirements/file-content/{pid}?path=../../etc/passwd")
    assert attack_res.status_code == 403
