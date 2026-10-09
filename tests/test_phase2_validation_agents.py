"""
Tests for Phase 2 validation agents:
- dependency_validation_agent
- frontend_validation_agent
- security_validation_agent
- validation_report_agent
"""
import pytest
from backend.agents.dependency_validation_agent import dependency_validation_agent
from backend.agents.frontend_validation_agent import frontend_validation_agent
from backend.agents.security_validation_agent import security_validation_agent
from backend.agents.validation_report_agent import validation_report_agent


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_state(**kwargs):
    """Build a minimal AgentState dict for testing."""
    base = {
        "project_id": "test-proj",
        "assembled_project_path": "",
        "generated_files": {},
    }
    base.update(kwargs)
    return base


# ─────────────────────────────────────────────────────────────────────────────
# dependency_validation_agent
# ─────────────────────────────────────────────────────────────────────────────

class TestDependencyValidationAgent:
    def test_pass_with_valid_files(self):
        req_txt = "fastapi>=0.100\nuvicorn>=0.20\npydantic>=2.0\nsqlalchemy"
        pkg_json = '{"dependencies":{"react":"^18","react-dom":"^18"},"scripts":{"start":"react-scripts start"}}'
        state = _make_state(generated_files={
            "backend/requirements.txt": req_txt,
            "frontend/package.json": pkg_json,
        })
        result = dependency_validation_agent(state)
        dv = result["dependency_validation"]
        assert dv["status"] == "PASS"
        assert len(dv["issues"]) == 0

    def test_fail_missing_requirements(self):
        pkg_json = '{"dependencies":{"react":"^18","react-dom":"^18"},"scripts":{"build":"react-scripts build"}}'
        state = _make_state(generated_files={
            "frontend/package.json": pkg_json,
        })
        result = dependency_validation_agent(state)
        dv = result["dependency_validation"]
        assert dv["status"] == "FAIL"
        assert any("requirements.txt" in i for i in dv["issues"])

    def test_fail_missing_fastapi_package(self):
        req_txt = "sqlalchemy\nrequests"  # missing fastapi, uvicorn, pydantic
        pkg_json = '{"dependencies":{"react":"^18","react-dom":"^18"},"scripts":{"start":"react-scripts start"}}'
        state = _make_state(generated_files={
            "backend/requirements.txt": req_txt,
            "frontend/package.json": pkg_json,
        })
        result = dependency_validation_agent(state)
        dv = result["dependency_validation"]
        assert dv["status"] == "FAIL"
        assert any("fastapi" in i.lower() or "Missing critical" in i for i in dv["issues"])

    def test_fail_missing_react_dependency(self):
        req_txt = "fastapi\nuvicorn\npydantic"
        pkg_json = '{"dependencies":{"axios":"^1.0"},"scripts":{"start":"node index.js"}}'
        state = _make_state(generated_files={
            "backend/requirements.txt": req_txt,
            "frontend/package.json": pkg_json,
        })
        result = dependency_validation_agent(state)
        dv = result["dependency_validation"]
        assert dv["status"] == "FAIL"
        assert any("react" in i.lower() for i in dv["issues"])


# ─────────────────────────────────────────────────────────────────────────────
# frontend_validation_agent
# ─────────────────────────────────────────────────────────────────────────────

class TestFrontendValidationAgent:
    _VALID_INDEX = '<!DOCTYPE html><html><body><div id="root"></div></body></html>'
    _VALID_APP = 'import React from "react";\nexport default function App() { return <div>Hello</div>; }'
    _VALID_API_JS = 'export async function fetchData() { return fetch("/api/items").then(r=>r.json()); }'

    def test_pass_valid_frontend(self):
        state = _make_state(generated_files={
            "frontend/index.html": self._VALID_INDEX,
            "frontend/src/App.jsx": self._VALID_APP,
            "frontend/src/api.js": self._VALID_API_JS,
        })
        result = frontend_validation_agent(state)
        fv = result["frontend_validation"]
        assert fv["status"] == "PASS"

    def test_fail_missing_root_div(self):
        state = _make_state(generated_files={
            "frontend/index.html": "<html><body><div id='app'></div></body></html>",
            "frontend/src/App.jsx": self._VALID_APP,
            "frontend/src/api.js": self._VALID_API_JS,
        })
        result = frontend_validation_agent(state)
        fv = result["frontend_validation"]
        assert fv["status"] == "FAIL"
        assert any("root" in i for i in fv["issues"])

    def test_fail_missing_app_jsx(self):
        state = _make_state(generated_files={
            "frontend/index.html": self._VALID_INDEX,
            "frontend/src/api.js": self._VALID_API_JS,
        })
        result = frontend_validation_agent(state)
        fv = result["frontend_validation"]
        assert fv["status"] == "FAIL"
        assert any("App.jsx" in i for i in fv["issues"])

    def test_fail_no_http_functions_in_api_js(self):
        state = _make_state(generated_files={
            "frontend/index.html": self._VALID_INDEX,
            "frontend/src/App.jsx": self._VALID_APP,
            "frontend/src/api.js": "// placeholder",
        })
        result = frontend_validation_agent(state)
        fv = result["frontend_validation"]
        assert fv["status"] == "FAIL"
        assert any("HTTP" in i or "fetch" in i.lower() for i in fv["issues"])


# ─────────────────────────────────────────────────────────────────────────────
# security_validation_agent
# ─────────────────────────────────────────────────────────────────────────────

class TestSecurityValidationAgent:
    def test_pass_clean_code(self):
        state = _make_state(generated_files={
            "backend/main.py": 'from fastapi import FastAPI\napp = FastAPI()',
            "backend/services.py": 'from sqlalchemy.orm import Session\ndef get_items(db: Session): return db.query(Item).all()',
        })
        result = security_validation_agent(state)
        sv = result["security_validation"]
        assert sv["status"] in ("PASS", "WARN")  # no SQL injection → at most WARN

    def test_warn_on_debug_true(self):
        state = _make_state(generated_files={
            "backend/main.py": 'DEBUG = True\nfrom fastapi import FastAPI',
        })
        result = security_validation_agent(state)
        sv = result["security_validation"]
        # debug=True triggers a warning
        assert sv["status"] in ("WARN", "PASS")

    def test_warn_on_open_cors(self):
        state = _make_state(generated_files={
            "backend/main.py": 'app.add_middleware(CORSMiddleware, allow_origins=["*"])',
        })
        result = security_validation_agent(state)
        sv = result["security_validation"]
        assert sv["status"] in ("WARN", "PASS")

    def test_status_has_required_keys(self):
        state = _make_state()
        result = security_validation_agent(state)
        sv = result["security_validation"]
        assert "status" in sv
        assert "checks" in sv
        assert "issues" in sv
        assert "warnings" in sv


# ─────────────────────────────────────────────────────────────────────────────
# validation_report_agent
# ─────────────────────────────────────────────────────────────────────────────

class TestValidationReportAgent:
    def _all_pass_state(self):
        pass_gate = {"status": "PASS", "checks": [], "issues": [], "warnings": []}
        pass_gate_valid = {"status": "PASS", "checks": [], "issues": [], "is_valid": True}
        return {
            "code_validation":       pass_gate_valid,
            "build_validation":      pass_gate,
            "api_validation":        pass_gate,
            "database_validation":   pass_gate,
            "docker_validation":     pass_gate,
            "dependency_validation": pass_gate,
            "frontend_validation":   pass_gate,
            "security_validation":   {**pass_gate, "status": "PASS"},
        }

    def test_all_pass_means_deployment_ready(self):
        state = self._all_pass_state()
        result = validation_report_agent(state)
        vr = result["validation_report"]
        assert vr["status"] == "passed"
        assert vr["deployment_ready"] is True
        assert vr["gates_passed"] == 8
        assert len(vr["blocking_issues"]) == 0

    def test_hard_gate_fail_blocks_deployment(self):
        state = self._all_pass_state()
        state["code_validation"] = {"status": "FAIL", "is_valid": False, "checks": [], "issues": ["syntax error"]}
        result = validation_report_agent(state)
        vr = result["validation_report"]
        assert vr["deployment_ready"] is False
        assert vr["status"] == "failed"
        assert any("code_validation" in iss for iss in vr["blocking_issues"])

    def test_soft_gate_fail_does_not_block(self):
        state = self._all_pass_state()
        # dependency failure is a soft gate — should not block deployment
        state["dependency_validation"] = {"status": "FAIL", "checks": [], "issues": ["Missing axios"], "warnings": []}
        result = validation_report_agent(state)
        vr = result["validation_report"]
        # Hard gates all pass → should still be deployment_ready
        assert vr["deployment_ready"] is True

    def test_report_has_deployment_ready_key(self):
        state = self._all_pass_state()
        result = validation_report_agent(state)
        vr = result["validation_report"]
        assert "deployment_ready" in vr
        assert "gates" in vr
        assert "gates_passed" in vr
        assert "gates_total" in vr
        assert vr["gates_total"] == 8
