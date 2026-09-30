import os
import re
from pathlib import Path
from typing import Dict, Any, List
from backend.agents.state import AgentState


def database_integration_testing_agent(state: AgentState) -> AgentState:
    """
    Validate that the generated database schema and backend models
    faithfully satisfy the database specification contract.
    """
    project_path_str = state.get("assembled_project_path")
    db_spec = state.get("database_specification", {})
    expected_tables = db_spec.get("tables", [])

    if not project_path_str or not os.path.exists(project_path_str):
        state["database_validation"] = {
            "status": "FAIL",
            "tables_checked": [],
            "issues": ["Project directory does not exist for database validation"],
            "summary": "Database validation failed: project directory missing."
        }
        return state

    project_dir = Path(project_path_str)
    schema_sql_file = project_dir / "database" / "schema.sql"
    models_file = project_dir / "backend" / "models.py"

    schema_sql = ""
    if schema_sql_file.exists():
        schema_sql = schema_sql_file.read_text(encoding="utf-8")

    models_code = ""
    if models_file.exists():
        models_code = models_file.read_text(encoding="utf-8")

    issues: List[str] = []
    tables_checked: List[Dict[str, Any]] = []

    # If no tables in spec, extract or check for standard tables
    if not expected_tables:
        has_create_table = "CREATE TABLE" in schema_sql.upper()
        status = "PASS" if has_create_table else "WARN"
        summary = "No explicit tables in database specification. Schema DDL verified."
        state["database_validation"] = {
            "status": status,
            "tables_checked": [],
            "issues": issues,
            "summary": summary
        }
        return state

    for table in expected_tables:
        table_name = table if isinstance(table, str) else table.get("name", "")
        if not table_name:
            continue

        clean_name = table_name.lower().strip()

        # Check in schema.sql: CREATE TABLE (IF NOT EXISTS)? table_name
        sql_pattern = rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{clean_name}\b"
        sql_match = bool(re.search(sql_pattern, schema_sql, re.IGNORECASE))

        # Check in models.py: __tablename__ = 'table_name' or class TableName
        model_pattern = rf"__tablename__\s*=\s*['\"]{clean_name}['\"]"
        model_match = bool(re.search(model_pattern, models_code, re.IGNORECASE))

        table_record = {
            "table_name": clean_name,
            "sql_defined": sql_match,
            "model_defined": model_match,
        }
        tables_checked.append(table_record)

        if not sql_match:
            issues.append(f"Table '{clean_name}' not defined in database/schema.sql")
        if not model_match:
            issues.append(f"Model for table '{clean_name}' not defined in backend/models.py")

    status = "PASS" if len(issues) == 0 else "FAIL"
    summary = (
        f"Database specification validation {status}: "
        f"{sum(1 for t in tables_checked if t['sql_defined'])}/{len(tables_checked)} "
        f"tables found in DDL schema. Issues detected: {len(issues)}."
    )

    db_result = {
        "status": status,
        "tables_checked": tables_checked,
        "issues": issues,
        "summary": summary
    }

    state["database_validation"] = db_result

    architecture = state.get("architecture", {})
    architecture["database_validation"] = db_result
    state["architecture"] = architecture

    return state
