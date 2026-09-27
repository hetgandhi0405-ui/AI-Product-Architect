from backend.agents.code_generation_agent import generate_file_content
from backend.agents.state import AgentState


def generated_code_self_correction_agent(state: AgentState) -> AgentState:
    attempts = state.get("generated_code_correction_attempts", 0) + 1
    max_attempts = state.get("max_generated_code_correction_attempts", 3)
    issues = state.get("generated_code_validation", {}).get("file_issues", {})
    generated = dict(state.get("generated_files", {})
    by_path = {
        item["path"]: item
        for item in state.get("file_manifest", {}).get("files", [])
    }
    for path, messages in issues.items():
        item = by_path.get(path, {}
        generated[path] = generate_file_content(
            state, path, item.get("kind", "source"), "\n".join(messages)
        )
    state["generated_files"] = generated
    state["generated_code_correction_attempts"] = attempts
    state["max_generated_code_correction_attempts"] = max_attempts
    return state
