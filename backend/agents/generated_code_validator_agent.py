import os
import json
import py_compile
from pathlib import Path
from typing import Dict, Any, List
from backend.agents.state import AgentState


def generated_code_validator_agent(state: AgentState) -> AgentState:
    """
    Validate the generated project files for syntactic correctness,
    file presence, non-emptiness, and structural validity.
    """
    project_path_str = state.get("assembled_project_path")
    manifest = state.get("file_manifest", {})
    manifest_files = manifest.get("files", [])

    if not project_path_str or not os.path.exists(project_path_str):
        state["code_validation"] = {
            "status": "FAIL",
            "is_valid": False,
            "checks": {},
            "file_issues": [{"file": "root", "issue": "Project directory does not exist"}],
            "issues": ["Assembled project directory does not exist"],
            "summary": "Validation failed: Project directory not found on disk."
        }
        return state

    project_dir = Path(project_path_str)
    checks: Dict[str, Any] = {
        "file_existence": {"total": len(manifest_files), "passed": 0, "failed": 0},
        "non_empty": {"total": len(manifest_files), "passed": 0, "failed": 0},
        "python_syntax": {"total": 0, "passed": 0, "failed": 0},
        "json_syntax": {"total": 0, "passed": 0, "failed": 0},
        "docker_structure": {"total": 0, "passed": 0, "failed": 0},
        "terraform_structure": {"total": 0, "passed": 0, "failed": 0},
    }

    file_issues: List[Dict[str, Any]] = []
    issues: List[str] = []

    for item in manifest_files:
        rel_path = item["path"]
        file_path = project_dir / rel_path

        # 1. File existence
        if not file_path.exists():
            checks["file_existence"]["failed"] += 1
            issue_msg = f"Missing required manifest file: '{rel_path}'"
            file_issues.append({"file": rel_path, "issue": issue_msg})
            issues.append(issue_msg)
            continue
        checks["file_existence"]["passed"] += 1

        # 2. Non-empty check
        try:
            stat = file_path.stat()
            # Allow __init__.py to be empty or minimal, others must be non-empty
            if stat.st_size == 0 and not rel_path.endswith("__init__.py"):
                checks["non_empty"]["failed"] += 1
                issue_msg = f"Required file is empty (0 bytes): '{rel_path}'"
                file_issues.append({"file": rel_path, "issue": issue_msg})
                issues.append(issue_msg)
                continue
            checks["non_empty"]["passed"] += 1
        except Exception as e:
            checks["non_empty"]["failed"] += 1
            issues.append(f"Cannot stat '{rel_path}': {e}")
            continue

        # 3. Python compilation check
        if rel_path.endswith(".py"):
            checks["python_syntax"]["total"] += 1
            try:
                py_compile.compile(str(file_path), doraise=True)
                checks["python_syntax"]["passed"] += 1
            except py_compile.PyCompileError as e:
                checks["python_syntax"]["failed"] += 1
                issue_msg = f"Python syntax compilation error in '{rel_path}': {e.msg}"
                file_issues.append({"file": rel_path, "issue": issue_msg})
                issues.append(issue_msg)

        # 4. JSON parsing check
        elif rel_path.endswith(".json"):
            checks["json_syntax"]["total"] += 1
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    json.load(f)
                checks["json_syntax"]["passed"] += 1
            except Exception as e:
                checks["json_syntax"]["failed"] += 1
                issue_msg = f"JSON parse error in '{rel_path}': {str(e)}"
                file_issues.append({"file": rel_path, "issue": issue_msg})
                issues.append(issue_msg)

        # 5. Docker structure check
        elif rel_path == "Dockerfile":
            checks["docker_structure"]["total"] += 1
            content = file_path.read_text(encoding="utf-8")
            if "FROM " not in content:
                checks["docker_structure"]["failed"] += 1
                issue_msg = "Dockerfile is missing required 'FROM' instruction"
                file_issues.append({"file": rel_path, "issue": issue_msg})
                issues.append(issue_msg)
            else:
                checks["docker_structure"]["passed"] += 1

        elif rel_path == "docker-compose.yml":
            checks["docker_structure"]["total"] += 1
            content = file_path.read_text(encoding="utf-8")
            if "services:" not in content:
                checks["docker_structure"]["failed"] += 1
                issue_msg = "docker-compose.yml is missing required 'services:' block"
                file_issues.append({"file": rel_path, "issue": issue_msg})
                issues.append(issue_msg)
            else:
                checks["docker_structure"]["passed"] += 1

        # 6. Terraform HCL structure check
        elif rel_path.endswith(".tf"):
            checks["terraform_structure"]["total"] += 1
            content = file_path.read_text(encoding="utf-8")
            # Must declare standard blocks
            has_hcl_decl = any(
                keyword in content
                for keyword in ["terraform", "provider", "resource", "variable", "output", "data", "module"]
            )
            if not has_hcl_decl and stat.st_size > 0:
                checks["terraform_structure"]["failed"] += 1
                issue_msg = f"Terraform file '{rel_path}' does not contain recognized HCL block declarations"
                file_issues.append({"file": rel_path, "issue": issue_msg})
                issues.append(issue_msg)
            else:
                checks["terraform_structure"]["passed"] += 1

    is_valid = len(issues) == 0
    status = "PASS" if is_valid else "FAIL"

    summary = (
        f"Generated code validation {status}: "
        f"{checks['file_existence']['passed']}/{checks['file_existence']['total']} files exist, "
        f"{checks['python_syntax']['passed']}/{checks['python_syntax']['total']} python files compile, "
        f"{checks['json_syntax']['passed']}/{checks['json_syntax']['total']} JSON files valid. "
        f"{len(issues)} total issues."
    )

    validation_result = {
        "status": status,
        "is_valid": is_valid,
        "checks": checks,
        "file_issues": file_issues,
        "issues": issues,
        "summary": summary,
    }

    state["code_validation"] = validation_result

    architecture = state.get("architecture", {})
    architecture["code_validation"] = validation_result
    state["architecture"] = architecture

    return state
