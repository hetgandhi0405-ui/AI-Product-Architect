import os
from typing import Dict

from google import genai

from backend.agents.state import AgentState
from backend.core.llm_cache import cached_generate_content
from backend.core.model_router import get_fast_model
from backend.core.prompt_utils import compact_json

def _strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def generate_file_content(state: AgentState, path: str, kind: str, feedback: str = "") -> str:
    prompt = (
        "Generate exactly one complete raw file for an AI Product Architect project.\n"
        f"Path: {path}\nKind: {kind}\n"
        f"Customer requirement:\n{state.get('requirements', '')}\n"
        f"Product plan:\n{compact_json(state.get('product_plan', {}))}\n"
        f"UI specification:\n{compact_json(state.get('ui_specification', {}))}\n"
        f"API specification:\n{compact_json(state.get('api_specification', {}))}\n"
        f"Database specification:\n{compact_json(state.get('database_specification', {}))}\n"
        f"Code generation contract:\n{compact_json(state.get('code_generation_contract', {}))}\n"
        f"Architecture:\n{compact_json(state.get('architecture', {}))}\n"
        "The generated file must be internally consistent with the supplied specifications and other files in the requested project. Return only file contents, with no explanation or Markdown fences."
    )
    if feedback:
        prompt += f"\nPrevious validation failures:\n{feedback}\nRegenerate the complete corrected file."
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    client = genai.Client(api_key=api_key)
    response = cached_generate_content(
        client,
        f"code_generation:{path}",
        model=get_fast_model(),
        contents=prompt,
    )
    content = _strip_code_fence(response.text or "")
    if not content:
        raise RuntimeError(f"Gemini returned empty content for generated file: {path}")
    return content


def code_generation_agent(state: AgentState) -> AgentState:
    manifest = state.get("file_manifest", {}).get("files", [])
    generated: Dict[str, str] = dict(state.get("generated_files", {}))
    feedback = state.get("generated_code_validation", {}).get("file_issues", {})
    for item in manifest:
        path = item["path"]
        generated[path] = generate_file_content(
            state, path, item.get("kind", "source"), "\n".join(feedback.get(path, []))
        )
    state["generated_files"] = generated
    state["generation_status"] = "GENERATED"
    return state
