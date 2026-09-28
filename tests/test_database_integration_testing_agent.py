from backend.agents.database_integration_testing_agent import database_integration_testing_agent


def test_database_integration_matches_schema(tmp_path):
    (tmp_path / "database").mkdir()
    (tmp_path / "backend").mkdir()
    (tmp_path / "database" / "schema.sql").write_text(
        "CREATE TABLE users (id UUID PRIMARY KEY);\n",
        encoding="utf-8",
    )
    (tmp_path / "backend" / "main.py").write_text(
        'query = "SELECT * FROM users"\n',
        encoding="utf-8",
    )
    state = {
        "generated_project_path": str(tmp_path),
        "database_specification": {"tables": [{"name": "users"}]},
    }
    result = database_integration_testing_agent(state)
    assert result["database_integration_validation"]["status"] == "VALID"


def test_database_integration_detects_missing_schema_table(tmp_path):
    (tmp_path / "database").mkdir()
    (tmp_path / "database" / "schema.sql").write_text(
        "CREATE TABLE products (id UUID PRIMARY KEY);\n",
        encoding="utf-8",
    )
    state = {
        "generated_project_path": str(tmp_path),
        "database_specification": {"tables": [{"name": "users"}]},
    }
    result = database_integration_testing_agent(state)
    assert result["database_integration_validation"]["status"] == "INVALID"
    assert any("users" in item for item in result["database_integration_validation"]["issues"])
