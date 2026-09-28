import os
from typing import Dict, Any, List
from backend.agents.state import AgentState
from backend.agents.llm_client import LazyGenAIClient
from backend.agents.file_assembler_agent import file_assembler_agent
from backend.agents.generated_code_validator_agent import generated_code_validator_agent
from backend.agents.code_generation_agent import _clean_markdown_fences, _generate_file_deterministic


def generated_code_self_correction_agent(state: AgentState) -> AgentState:
    """
    Automatically diagnose and correct code-level validation failures (syntax errors,
    missing files, empty files, malformed JSON).
    Regenerates only affected files, reassembles them, and re-runs validation.
    Enforces a strict upper bound to prevent infinite loops.
    """
    validation = state.get("code_validation", {})
    if validation.get("status") == "PASS":
        return state

    attempts = state.get("code_correction_attempts", 0)
    max_attempts = state.get("max_code_correction_attempts", 3)

    if attempts >= max_attempts:
        return state

    state["code_correction_attempts"] = attempts + 1

    file_issues = validation.get("file_issues", [])
    manifest = state.get("file_manifest", {})
    manifest_files_by_path = {f["path"]: f for f in manifest.get("files", [])}
    generated_files = state.get("generated_files", {})
    has_api_key = bool(os.environ.get("GEMINI_API_KEY"))

    correction_records: List[Dict[str, Any]] = []

    for issue_item in file_issues:
        target_path = issue_item.get("file")
        error_msg = issue_item.get("issue", "")
        if not target_path or target_path == "root":
            continue

        file_info = manifest_files_by_path.get(target_path, {"path": target_path, "language": "text", "purpose": "Corrected file"})
        current_code = generated_files.get(target_path, "")

        corrected_code = ""

        if has_api_key and current_code:
            try:
                client = LazyGenAIClient()
                prompt = f"""
You are an expert automated code repair system. Fix the code for '{target_path}'.
The file failed validation with this error:
{error_msg}

CURRENT CODE:
{current_code}

RULES:
1. Return ONLY the complete, corrected code.
2. Do NOT use Markdown code blocks or fences (no ```).
3. Ensure no syntax errors and all imports/syntax are 100% valid.
"""
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                corrected_code = _clean_markdown_fences(response.text or "")
            except Exception as e:
                print(f"[SelfCorrection] LLM fix failed for {target_path}: {e}")
                corrected_code = _generate_file_deterministic(target_path, file_info, state)
        else:
            corrected_code = _generate_file_deterministic(target_path, file_info, state)

        generated_files[target_path] = corrected_code
        correction_records.append({
            "attempt": state["code_correction_attempts"],
            "file": target_path,
            "error_addressed": error_msg,
            "status": "REGENERATED"
        })

    state["generated_files"] = generated_files

    # Re-assemble the files into the real directory
    state = file_assembler_agent(state)

    # Re-validate the generated code
    state = generated_code_validator_agent(state)

    architecture = state.get("architecture", {})
    history = architecture.setdefault("correction_history", [])
    history.extend(correction_records)
    state["architecture"] = architecture

    return state
