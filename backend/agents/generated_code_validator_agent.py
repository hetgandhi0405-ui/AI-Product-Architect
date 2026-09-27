import json
from pathlib import Path
from typing import Dict, List

from backend.agents.state import AgentState


def _check_file(path: Path, relative: str, kind: str) -> List[str]:
    if not path.exists():
        return ["file does not exist"]
    if path.stat().st_size == 0:
        return ["file is empty"]
    text = path.read_text(encoding="utf-8")
    issues: List[str] = []

    if path.suffix == ".py":
        try:
            compile(text, relative, "exec")
        except SyntaxError as exc:
            issues.append(f"Python syntax error: {exc.msg} at line {exc.lineno}")

    if path.suffix == ".json":
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            issues.append(f"Invalid JSON: {exc.msg} at line {exc.lineno}")

    if relative == "Dockerfile" and "FROM " not in text.upper():
        issues.append("Dockerfile is missing a FROM instruction")
    if relative == "docker-compose.yml" and "services:" not in text:
        issues.append("docker-compose.yml is missing services:")

    if kind == "terraform":
        if relative.endswith("main.tf") and 'provider "aws"' not in text:
            issues.append('main.tf is missing provider "aws"')
        if relative.endswith("variables.tf") and "variable " not in text:
            issues.append("variables.tf contains no variable definition")
        if relative.endswith("outputs.tf") and "output " not in text:
            issues.append("outputs.tf contains no output definition")
    return issues


def generated_code_validator_agent(state: AgentState) -> AgentState:
    root = Path(state.get("generated_project_path", ""))
    file_issues: Dict[str, List[str]] = {}
    checks: List[str] = []

    for item in state.get("file_manifest", {}).get("files", []):
        path = item["path"]
        issues = _check_file(root / path, path, item.get("kind", "source"))
        if issues:
            file_issues[path] = issues
        else:
            checks.append(f"PASS: {path}")

    state["generated_code_validation"] = {
        "status": "VALID" if not file_issues else "INVALID",
        "is_valid": not file_issues,
        "checks": checks,
        "file_issues": file_issues,
        "issues": [
            f"{path}: {message}"
            for path, messages in file_issues.items()
            for message in messages
        ],
        "summary": (
            "Generated project passed file validation."
            if not file_issues
            else f"Generated project has {len(file_issues)} invalid file(s)."
        ),
    }
    return state
