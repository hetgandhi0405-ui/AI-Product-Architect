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
        if any(k in err_msg for k in ["503", "UNAVAILABLE", "high demand", "failed after 3 attempts"]):
            pytest.skip(f"Google Gemini API temporarily unavailable: {exc}")
        raise

    # 1. Verify specification generation
    assert final_state.get("requirement_analysis") is not None
    assert final_state.get("architecture") is not None
    assert final_state.get("api_specification") is not None

    # 2. Verify code generation & manifest
    manifest = final_state.get("file_manifest", [])
    assert len(manifest) >= 5, f"Expected at least 5 files in manifest, got {len(manifest)}"

    generated_code = final_state.get("generated_code", {})
    assert len(generated_code) >= 5, "Expected generated code for manifest files"

    # 3. Verify assembly and validation
    assembled = final_state.get("assembled_files", [])
    assert len(assembled) >= 5, "Expected files assembled on disk"

    val_res = final_state.get("code_validation_results", {})
    assert val_res is not None

    # 4. Verify release gate and export
    gate_decision = final_state.get("release_gate_decision")
    assert gate_decision in ["APPROVED", "BLOCKED"]

    if gate_decision == "APPROVED":
        export_zip = final_state.get("export_zip_path")
        assert export_zip is not None
        assert Path(export_zip).exists()
