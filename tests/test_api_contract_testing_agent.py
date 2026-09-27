from backend.agents.api_contract_testing_agent import api_contract_testing_agent


def test_api_contract_matches_backend(tmp_path):
    (tmp_path / "backend").mkdir()
    (tmp_path / "backend" / "main.py").write_text(
        "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/api/users')\ndef users():\n    return []\n",
        encoding="utf-8",
    )
    state = {
        "generated_project_path": str(tmp_path),
        "api_specification": {
            "base_path": "/api",
            "endpoints": [{"method": "GET", "endpoint": "/users"}],
        },
    }
    result = api_contract_testing_agent(state)
    assert result["api_contract_validation"]["status"] == "VALID"


def test_api_contract_detects_missing_backend_route(tmp_path):
    (tmp_path / "backend").mkdir()
    (tmp_path / "backend" / "main.py").write_text(
        "from fastapi import FastAPI\napp = FastAPI()\n",
        encoding="utf-8",
    )
    state = {
        "generated_project_path": str(tmp_path),
        "api_specification": {
            "base_path": "/api",
            "endpoints": [{"method": "GET", "endpoint": "/users"}],
        },
    }
    result = api_contract_testing_agent(state)
    assert result["api_contract_validation"]["status"] == "INVALID"
    assert any("missing from backend" in item for item in result["api_contract_validation"]["issues"])
