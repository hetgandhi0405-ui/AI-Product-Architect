from backend.agents.state import AgentState


def integration_agent(state: AgentState) -> AgentState:
    product_plan = state.get("product_plan", {})
    ui_specification = state.get("ui_specification", {})
    api_specification = state.get("api_specification", {})
    database_specification = state.get("database_specification", {})

    features = product_plan.get("features", [])
    pages = ui_specification.get("pages", [])
    endpoints = api_specification.get("endpoints", [])
    tables = database_specification.get("tables", [])

    page_names = [p.get("name", "").lower() if isinstance(p, dict) else str(p).lower() for p in pages]
    endpoint_paths = [e.get("endpoint", "").lower() for e in endpoints if isinstance(e, dict)]
    table_names = [t.get("name", "").lower() for t in tables if isinstance(t, dict)]

    checks = []
    issues = []

    feature_page_keywords = {
        "registration": ["registration", "register", "signup", "sign up", "account"],
        "authentication": ["login", "signin", "sign in", "authentication", "account"],
        "product": ["product", "catalog", "shop", "shopping"],
        "cart": ["cart", "shopping cart"],
        "checkout": ["checkout", "payment", "order"],
        "order": ["order", "orders", "order history"],
        "admin": ["admin", "dashboard", "management"]
    }

    for feature in features:
        name = feature.get("name", "") if isinstance(feature, dict) else str(feature)
        feature_lower = name.lower()
        keywords = []
        for key, values in feature_page_keywords.items():
            if key in feature_lower:
                keywords.extend(values)
        ui_match = any(keyword in page for keyword in keywords for page in page_names)
        if ui_match:
            checks.append(f"Feature '{name}' has UI support.")
        else:
            issues.append(f"Feature '{name}' may not have corresponding UI support.")

    if endpoints:
        checks.append(f"API specification contains {len(endpoints)} endpoints.")
    else:
        issues.append("No API endpoints were generated.")

    if tables:
        checks.append(f"Database specification contains {len(tables)} tables.")
    else:
        issues.append("No database tables were generated.")

    matches = sum(1 for endpoint in endpoint_paths if any(table in endpoint for table in table_names))
    if matches:
        checks.append("API specification has database-related endpoint mappings.")
    else:
        checks.append("No direct API-to-database naming matches were found; manual validation may be required.")

    state["architecture"]["integration"] = {
        "status": "NEEDS_REVIEW" if issues else "INTEGRATED",
        "checks": checks,
        "issues": issues,
        "summary": "Cross-agent specifications are consistent." if not issues else "Some cross-agent relationships require review."
    }

    return state
