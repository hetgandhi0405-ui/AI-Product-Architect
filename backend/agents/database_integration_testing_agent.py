import re
from pathlib import Path
from typing import Dict, List, Set

from backend.agents.state import AgentState


def _sql_tables(sql: str) -> Set[str]:
    return {
        name.lower()
        for name in re.findall(r"\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\"']?([A-Za-z_][A-Za-z0-9_]*)", sql, re.I)
    }


def _spec_tables(state: AgentState) -> Set[str]:
    spec = state.get("database_specification", {})
    tables = spec.get("tables", []) if isinstance(spec, dict) else []
    return {
        str(item.get("name")).lower()
        for item in tables
        if isinstance(item, dict) and item.get("name")
    }


def _backend_table_references(root: Path) -> Set[str]:
    found = set()
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in (
            r"__tablename__\s*=\s*[\"']([A-Za-z_][A-Za-z0-9_]*)",
            r"\b(?:FROM|JOIN|INTO|UPDATE)\s+(?:[\"'])([A-Za-z_][A-Za-z0-9_]*)[\"']",
        ):
            found.update(m.lower() for m in re.findall(pattern, text, re.I))
    return found


def database_integration_testing_agent(state: AgentState) -> AgentState:
    root = Path(state.get("generated_project_path", ""))
    issues: List[str] = []
    checks: List[str] = []

    if not root.exists():
        issues.append("Generated project directory does not exist.")
    else:
        spec_tables = _spec_tables(state)
        schema_files = list(root.rglob("*.sql"))
        sql_tables = set()
        for schema in schema_files:
            sql_tables.update(_sql_tables(schema.read_text(encoding="utf-8")))

        backend_tables = _backend_table_references(root)

        if spec_tables and sql_tables:
            missing_schema = spec_tables - sql_tables
            extra_schema = sql_tables - spec_tables
            for table in sorted(missing_schema):
                issues.append(f"Database specification table is missing from SQL schema: {table}")
            for table in sorted(extra_schema):
                issues.append(f"SQL schema contains table not present in database specification: {table}")

        if spec_tables and backend_tables:
            missing_spec = backend_tables - spec_tables
            for table in sorted(missing_spec):
                issues.append(f"Backend references table not present in database specification: {table}")

        if spec_tables and not schema_files:
            issues.append("Database specification exists but no SQL schema file was generated.")

        checks.extend([
            f"Database specification tables: {len(spec_tables)}",
            f"SQL tables discovered: {len(sql_tables)}",
            f"Backend table references: {len(backend_tables)}",
        ])

    state["database_integration_validation"] = {
        "status": "VALID" if not issues else "INVALID",
        "is_valid": not issues,
        "checks": checks,
        "issues": issues,
        "summary": (
            "Database integration checks passed."
            if not issues
            else f"Database integration checks found {len(issues)} issue(s)."
        ),
    }
    return state
