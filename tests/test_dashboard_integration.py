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


def test_pipeline_background_start_and_status():
    """Verify non-blocking pipeline startup and status polling endpoints."""
    # 1. Start pipeline in background
    payload = {
        "description": "Build a simple weather dashboard with FastAPI and React",
        "project_name": "Weather Status Dashboard",
        "execution_mode": "QUICK",
    }
    start_res = client.post("/api/requirements/start", json=payload)
    assert start_res.status_code == 200
    start_data = start_res.json()
    assert "job_id" in start_data
    assert "stages" in start_data
    assert start_data["status"] == "queued"
    job_id = start_data["job_id"]

    # 2. Check initial status
    status_res = client.get(f"/api/requirements/status/{job_id}")
    assert status_res.status_code == 200
    st_data = status_res.json()
    assert st_data["job_id"] == job_id
    assert st_data["status"] in ["queued", "running", "done"]
    assert "stage" in st_data
    assert "stage_index" in st_data
    assert st_data["total_stages"] in (8, 9)

    # 3. Non-existent job returns 404
    missing_res = client.get("/api/requirements/status/job-nonexistent-12345")
    assert missing_res.status_code == 404


def test_cloud_deployment_and_rollback():
    """Verify cloud deployment operations and rollback endpoints."""
    # 1. Deploy project
    pid = "proj-deploy-test-123"
    deploy_res = client.post(f"/api/requirements/deploy/{pid}", json={
        "target": "cloud_run",
        "environment": "production"
    })
    assert deploy_res.status_code == 200
    deploy_data = deploy_res.json()
    assert deploy_data["success"] is True
    assert deploy_data["status"] == "DEPLOYED"
    assert "service_url" in deploy_data
    assert len(deploy_data["logs"]) > 0

    # 2. Rollback deployment
    rb_res = client.post(f"/api/requirements/rollback/{pid}")
    assert rb_res.status_code == 200
    rb_data = rb_res.json()
    assert rb_data["project_id"] == pid
    assert rb_data["rollback_status"]["status"] == "SUCCESS"
    assert len(rb_data["logs"]) > 0


def test_preview_endpoint_serves_interactive_app():
    """Verify live interactive deployment preview serves HTML with working app and API console."""
    pid = "proj-preview-test-456"
    res = client.get(f"/preview/{pid}")
    assert res.status_code == 200
    assert "Live Cloud Deployment Preview" in res.text
    assert "Online (200 OK)" in res.text
    assert "Interactive Application" in res.text
    assert "REST API Console" in res.text


def test_pipeline_status_survives_server_reload_memory_wipe():
    """Verify background job status polling survives uvicorn reload or in-memory cache wipe."""
    from backend.routes import requirements
    import time
    start_res = client.post("/api/requirements/start", json={
        "description": "Test real-time status resilience under reload",
        "execution_mode": "TEST"
    })
    assert start_res.status_code == 200
    jid = start_res.json()["job_id"]
    time.sleep(0.2)

    # Simulate server reload wiping in-memory state
    with requirements._jobs_lock:
        requirements._jobs.clear()

    # Poll status after memory wipe
    st = client.get(f"/api/requirements/status/{jid}")
    assert st.status_code == 200
    st_data = st.json()
    assert st_data["job_id"] == jid
    assert st_data["status"] in ["queued", "running", "done"]
    assert "stage" in st_data
    assert "coverage" in st_data




