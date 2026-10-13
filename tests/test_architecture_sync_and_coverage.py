import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.domain_analyzer import analyze_domain
from backend.routes.requirements import _calculate_requirement_coverage
from backend.routes.projects import record_project, _load_store, _save_store

client = TestClient(app)


def test_calculate_requirement_coverage_dynamic_logic():
    """Verify coverage is computed dynamically from requirement matrix items."""
    matrix = [
        {"req_id": "REQ-1", "type": "functional", "status": "SATISFIED"},
        {"req_id": "REQ-2", "type": "functional", "status": "SATISFIED"},
        {"req_id": "REQ-3", "type": "security", "status": "SATISFIED"},
        {"req_id": "REQ-4", "type": "performance", "status": "SATISFIED"},
        {"req_id": "REQ-5", "type": "non_functional", "status": "SATISFIED"},
    ]
    cov_pct, metrics = _calculate_requirement_coverage(matrix)
    assert cov_pct == 100.0
    assert metrics["functional"] == "2/2"
    assert metrics["security"] == "1/1"
    assert metrics["performance"] == "1/1"
    assert metrics["non_functional"] == "1/1"

    # Test with partial satisfaction
    matrix_partial = [
        {"req_id": "REQ-1", "type": "functional", "status": "SATISFIED"},
        {"req_id": "REQ-2", "type": "functional", "status": "PENDING"},
    ]
    cov_pct_partial, metrics_partial = _calculate_requirement_coverage(matrix_partial)
    assert cov_pct_partial == 50.0
    assert metrics_partial["functional"] == "1/2"


def test_all_domains_have_dynamic_coverage_not_hardcoded_92():
    """Ensure all domains compute real dynamic coverage and never default to 92."""
    domains = [
        ("task", "Build a task management app with priorities and deadlines"),
        ("ecommerce", "Online store with product catalog and shopping cart checkout"),
        ("lms", "Learning management system for students and course enrollments"),
        ("hospital", "Clinical appointment booking system for doctors and patients"),
        ("iot", "Smart home IoT dashboard with sensors, devices, and MQTT alerts"),
    ]
    for name, req in domains:
        spec = analyze_domain(req, name)
        cov, metrics = _calculate_requirement_coverage(spec.traceability_matrix)
        assert cov > 0
        assert cov != 92.0, f"Domain {name} unexpectedly produced hardcoded 92% coverage"
        assert "functional" in metrics
        assert "security" in metrics


def test_architecture_diagram_sync_across_views():
    """
    Verify architecture diagram is unified across the project record:
    diagram, architecture_diagram, and architecture.diagram match exactly.
    """
    ticket_req = "Customer support ticket system with tickets, comments, and SLA workflows"
    ticket_spec = analyze_domain(ticket_req, "Support System")
    expected_mermaid = ticket_spec.architecture_spec.get("diagram", "")

    proj_id = "test-sync-proj-001"
    record_project({
        "project_id": proj_id,
        "project_name": "Support System",
        "requirements": ticket_req,
        "status": "completed",
        "diagram": expected_mermaid,
        "architecture_diagram": expected_mermaid,
        "coverage": 100.0,
        "data": {
            "project_id": proj_id,
            "project_name": "Support System",
            "diagram": expected_mermaid,
            "architecture_diagram": expected_mermaid,
            "architecture": {
                "diagram": expected_mermaid,
                "mermaid_diagram": expected_mermaid,
            },
            "coverage": 100.0,
        }
    })

    res = client.get(f"/api/projects/{proj_id}")
    assert res.status_code == 200
    p = res.json()
    data = p.get("data", p)

    # All three architecture diagram keys must exist and match identically
    main_diag = data.get("diagram")
    arch_diag = data.get("architecture_diagram")
    nested_diag = data.get("architecture", {}).get("diagram")

    assert main_diag == expected_mermaid
    assert arch_diag == expected_mermaid
    assert nested_diag == expected_mermaid
    assert "Ticket" in main_diag or "Support" in main_diag


def test_switching_projects_provides_distinct_architectures():
    """Verify Project A and Project B have distinct diagrams in their project records."""
    proj_a_spec = analyze_domain("Task manager app with users and tasks", "TaskManager")
    proj_b_spec = analyze_domain("IoT smart home dashboard with devices and sensors", "SmartHome")

    record_project({
        "project_id": "proj-a-task",
        "project_name": "TaskManager",
        "diagram": proj_a_spec.architecture_spec["diagram"],
        "architecture_diagram": proj_a_spec.architecture_spec["diagram"],
        "coverage": 100.0,
    })
    record_project({
        "project_id": "proj-b-iot",
        "project_name": "SmartHome",
        "diagram": proj_b_spec.architecture_spec["diagram"],
        "architecture_diagram": proj_b_spec.architecture_spec["diagram"],
        "coverage": 100.0,
    })

    res_a = client.get("/api/projects/proj-a-task")
    res_b = client.get("/api/projects/proj-b-iot")
    assert res_a.status_code == 200
    assert res_b.status_code == 200

    diag_a = res_a.json()["data"]["diagram"]
    diag_b = res_b.json()["data"]["diagram"]

    assert diag_a != diag_b
    assert "Task" in diag_a
    assert "IoT" in diag_b or "Device" in diag_b


def test_deploy_fails_for_nonexistent_project():
    """Verify deployment rejects invalid or non-existent projects with 404."""
    res = client.post("/api/requirements/deploy/nonexistent-project-xyz999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_deploy_and_preview_workflow_for_valid_project():
    """Verify deployment succeeds and generates verified preview for valid project."""
    proj_id = "test-deploy-valid-001"
    record_project({
        "project_id": proj_id,
        "project_name": "Hospital Portal",
        "requirements": "Clinical appointment booking system for doctors and patients",
        "status": "completed",
        "coverage": 100.0,
    })

    deploy_res = client.post(f"/api/requirements/deploy/{proj_id}", json={"target": "cloud_run"})
    assert deploy_res.status_code == 200
    data = deploy_res.json()
    assert data["success"] is True
    assert data["status"] == "DEPLOYED"
    assert data["health_status"] == "HEALTHY"
    assert f"/preview/{proj_id}" in data["service_url"]
    assert len(data["logs"]) >= 5

    preview_res = client.get(f"/preview/{proj_id}")
    assert preview_res.status_code == 200
    assert "html" in preview_res.headers.get("content-type", "").lower()
    html_text = preview_res.text
    assert "Hospital Portal" in html_text or "Doctor" in html_text or "Appointment" in html_text
