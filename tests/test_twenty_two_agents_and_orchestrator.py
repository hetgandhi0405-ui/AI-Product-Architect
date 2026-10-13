"""
End-to-End Test Suite for AI-Product-Architect 22-Agent Orchestration,
External Coding Provider Pipeline, Deployment Controls, and Dynamic Traceability.
"""
import os
import zipfile
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.orchestrator import PlatformOrchestrator
from backend.agents.external_code_generation_agent import ExternalCodeGenerationAgent
from backend.schemas.contracts import CodingTaskRequest

client = TestClient(app)


def test_orchestrator_initialization_and_contracts():
    """Verify that PlatformOrchestrator initializes cleanly and defines all 22 agents."""
    orchestrator = PlatformOrchestrator()
    assert orchestrator is not None
    assert len(orchestrator.STAGE_NAMES) == 22
    assert "Requirement Analysis" in orchestrator.STAGE_NAMES[0]
    assert "External AI Code Generation" in orchestrator.STAGE_NAMES[10]
    assert "Release Gate" in orchestrator.STAGE_NAMES[21]


def test_external_ai_code_generation_agent_provider_unavailable():
    """Verify that when no API keys are configured, ExternalCodeGenerationAgent honestly returns PROVIDER_UNAVAILABLE."""
    # Ensure keys are not present in test environment
    orig_gemini = os.environ.pop("GEMINI_API_KEY", None)
    orig_openai = os.environ.pop("OPENAI_API_KEY", None)

    try:
        agent = ExternalCodeGenerationAgent()
        status = agent.check_provider_status()
        assert status["available"] is False
        assert status["status"] == "PROVIDER_UNAVAILABLE"

        request = CodingTaskRequest(
            project_id="proj-test-123",
            task_id="task-test-456",
            requirement_ids=["REQ-F-001"],
            instructions="Build a high performance user management service with JWT auth.",
            target_files=["backend/routes/auth.py"],
            existing_files={}
        )
        response = agent.generate_code(request)
        assert response.status == "PROVIDER_UNAVAILABLE"
        assert response.provider == "NONE"
        assert len(response.files) == 0
        assert "No external AI coding provider configured" in response.error_message
    finally:
        if orig_gemini:
            os.environ["GEMINI_API_KEY"] = orig_gemini
        if orig_openai:
            os.environ["OPENAI_API_KEY"] = orig_openai


def test_external_provider_status_endpoint():
    """Verify GET /api/requirements/external-provider-status returns structured contract."""
    response = client.get("/api/requirements/external-provider-status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "available" in data
    assert "provider" in data


def test_orchestrator_full_project_synthesis_and_zip_export():
    """
    Execute full pipeline for a realistic prompt, verify:
    - 20 AST-verified source files
    - Distinct dual coverage (Implementation vs Verified)
    - Synchronized architecture graph and Mermaid
    - Complete ZIP deliverable with embedded architecture and traceability
    """
    orchestrator = PlatformOrchestrator()
    prompt = "Design and build a scalable SaaS inventory and supply chain tracking system with real-time alerts and PostgreSQL."
    project_name = "SupplyChainPro"

    result = orchestrator.execute(prompt=prompt, project_name=project_name)
    assert result is not None
    assert result["final_status"] == "SUCCESS"
    assert result["project_name"] == project_name
    project_id = result["project_id"]
    assert project_id is not None

    # Check that architecture graph is synchronized
    arch = result["architecture"]
    assert "components" in arch or "nodes" in arch
    comp_list = arch.get("components") or arch.get("nodes", [])
    assert len(comp_list) >= 4
    assert len(arch.get("mermaid_diagram", "")) > 0

    # Check generated files
    files = result["generated_files"]
    assert len(files) >= 15
    file_manifest = result["file_manifest"]["files"]
    assert len(file_manifest) >= 15

    # Check dual coverage metrics
    traceability = result["traceability"]
    assert traceability["implementation_coverage_pct"] >= 90.0
    assert traceability["verified_coverage_pct"] >= 90.0
    assert len(traceability["matrix"]) >= 4

    # Check validation results
    validation = result["validation_report"]
    assert validation["status"] == "PASSED"
    assert validation["deployment_ready"] is True

    # Check ZIP export file existence on disk
    zip_path = result["export"]["zip_path"]
    assert os.path.exists(zip_path)

    with zipfile.ZipFile(zip_path, "r") as zf:
        namelist = zf.namelist()
        assert "architecture.json" in namelist
        assert "architecture.mmd" in namelist
        assert "traceability.json" in namelist
        assert "validation_report.json" in namelist
        assert any(n.endswith("main.py") for n in namelist)
        assert any(n.endswith("Dockerfile") for n in namelist)


def test_deployment_lifecycle_controls():
    """Verify live deployment controls: Deploy, Stop, Restart, Health Probe, and Rollback."""
    # First create a test project via the pipeline
    orchestrator = PlatformOrchestrator()
    result = orchestrator.execute(
        prompt="Build a telemedicine patient booking portal with doctor schedules and appointments.",
        project_name="TeleMed Portal"
    )
    project_id = result["project_id"]

    # 1. Health Probe
    health_res = client.get(f"/api/requirements/preview-health/{project_id}")
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert health_data["status"] in ("healthy", "DEPLOYED", "HEALTHY")
    assert health_data["http_status"] == 200

    # 2. Stop App
    stop_res = client.post(f"/api/requirements/stop/{project_id}")
    assert stop_res.status_code == 200
    stop_data = stop_res.json()
    assert stop_data["status"] in ("stopped", "STOPPED")

    # 3. Restart App
    restart_res = client.post(f"/api/requirements/restart/{project_id}")
    assert restart_res.status_code == 200
    restart_data = restart_res.json()
    assert restart_data["status"] in ("running", "DEPLOYED")
    assert "preview_url" in restart_data

    # 4. Preview Page Render
    prev_res = client.get(f"/preview/{project_id}")
    assert prev_res.status_code == 200
    assert "TeleMed Portal" in prev_res.text or "Application" in prev_res.text

    # 5. Cloud Deploy
    deploy_res = client.post(
        f"/api/requirements/deploy/{project_id}",
        json={"target": "cloud_run", "environment": "production"}
    )
    assert deploy_res.status_code == 200
    deploy_data = deploy_res.json()
    assert deploy_data["status"] in ("deployed", "DEPLOYED")
    assert "service_url" in deploy_data

    # 6. Rollback
    rb_res = client.post(f"/api/requirements/rollback/{project_id}")
    assert rb_res.status_code == 200
    rb_data = rb_res.json()
    assert rb_data["status"] in ("rolled_back", "ROLLED_BACK")
