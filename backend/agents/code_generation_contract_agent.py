from backend.agents.state import AgentState


def code_generation_contract_agent(state: AgentState) -> AgentState:
    """
    Build a standardized contract that can be consumed by
    the full-stack code generation system.
    """

    product_plan = state.get("product_plan", {})
    ui_specification = state.get("ui_specification", {})
    api_specification = state.get("api_specification", {})
    database_specification = state.get("database_specification", {})
    architecture = state.get("architecture", {})

    contract = {
        "project": {
            "name": state.get("project_name", "Generated Product"),
            "requirements": state.get("requirements", "")
        },

        "frontend": {
            "pages": ui_specification.get("pages", []),
            "navigation": ui_specification.get("navigation", {}),
            "components": ui_specification.get("components", []),
            "forms": ui_specification.get("forms", []),
            "user_flows": ui_specification.get("user_flows", [])
        },

        "backend": {
            "api_style": api_specification.get("api_style", "REST"),
            "base_path": api_specification.get("base_path", "/api"),
            "endpoints": api_specification.get("endpoints", [])
        },

        "database": {
            "database_type": database_specification.get(
                "database_type",
                "PostgreSQL"
            ),
            "tables": database_specification.get("tables", [])
        },

        "infrastructure": architecture.get("infrastructure", {}),

        "terraform": architecture.get("terraform", {}),

        "generation_targets": {
            "frontend": True,
            "backend": True,
            "database": True,
            "tests": True,
            "docker": True,
            "terraform": True,
            "documentation": True
        },

        "expected_repository": {
            "frontend": "frontend/",
            "backend": "backend/",
            "database": "database/",
            "infrastructure": "infrastructure/",
            "tests": "tests/",
            "docker_compose": "docker-compose.yml",
            "environment": ".env.example",
            "readme": "README.md"
        }
    }

    state["code_generation_contract"] = contract

    return state
