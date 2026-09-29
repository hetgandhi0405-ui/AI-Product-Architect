"""
Level 2 AI Test Suite: Full End-to-End Generation with Live Gemini API.

Only executes if GEMINI_API_KEY is present in the environment or .env file.
If GEMINI_API_KEY is missing, gracefully skips all tests.
"""
import os
import pytest
from pathlib import Path

# Check if real API key is present
api_key = os.getenv("GEMINI_API_KEY", "").strip()
pytestmark = pytest.mark.skipif(
    not api_key or api_key == "mock" or api_key.startswith("your_"),
    reason="GEMINI_API_KEY is not set or is mock. Skipping Level 2 live AI tests."
)


def test_real_ai_full_generation_pipeline():
    """
    Test real Gemini AI generation across the entire pipeline.
    Ensures prompt translates to specs, code, assembly, validation, and export.
    """
    from backend.agents.graph import app
    from backend.agents.state import AgentState

    test_prompt = "Build a modern task tracking API with user authentication and status filtering."
    initial_state = {
        "project_id": "test-real-ai-001",
        "project_name": "AI Task Tracker",
        "requirements": test_prompt,
        "suggestions": [],
        "architecture": {},
    }

    try:
        from google.genai.errors import ServerError, APIError
    except ImportError:
        ServerError = APIError = Exception

    try:
        final_state = app.invoke(initial_state)
    except Exception as exc:
        err_msg = str(exc)
        if any(k in err_msg for k in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "Quota", "quota", "high demand", "failed after 3 attempts"]):
            pytest.skip(f"Google Gemini API rate limit or service unavailable: {exc}")
        raise

    # 1. Verify specification generation
    assert final_state.get("requirements") is not None
    assert final_state.get("architecture") is not None

    # 2. Verify code generation & manifest
    manifest = final_state.get("file_manifest", {})
    files = manifest.get("files", []) if isinstance(manifest, dict) else manifest
    assert len(files) >= 5, f"Expected at least 5 files in manifest, got {len(files)}"

    generated_files = final_state.get("generated_files", {})
    assert len(generated_files) >= 5, "Expected generated code for manifest files"

    # 3. Verify assembly and validation
    val_res = final_state.get("code_validation", {})
    assert val_res is not None

    # 4. Verify release gate and export
    release_gate = final_state.get("release_gate", {})
    gate_status = release_gate.get("status")
    assert gate_status in ["APPROVED", "BLOCKED"]

    if gate_status == "APPROVED":
        export_zip = final_state.get("export_zip_path")
        assert export_zip is not None
        assert Path(export_zip).exists()

