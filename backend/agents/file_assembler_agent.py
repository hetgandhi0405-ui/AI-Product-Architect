import os
import re
from pathlib import Path

from backend.agents.state import AgentState


def _safe_relative_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"Unsafe generated file path: {path}")
    return candidate


def file_assembler_agent(state: AgentState) -> AgentState:
    project_id = re.sub(r"[^A-Za-z0-9_.-]", "_", state.get("project_id", "generated-project"))
    root = Path(os.getenv("AI_PRODUCT_ARCHITECT_OUTPUT_DIR", "generated_projects")) / project_id
    root.mkdir(parents=True, exist_ok=True)
    for relative_path, content in state.get("generated_files", {}).items():
        target = root / _safe_relative_path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    state["generated_project_path"] = str(root)
    state["assembly_status"] = "ASSEMBLED"
    state["assembled_file_count"] = len(state.get("generated_files", {}))
    return state
