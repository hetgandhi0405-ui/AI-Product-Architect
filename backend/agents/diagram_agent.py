import re

from backend.agents.state import AgentState


def diagram_agent(state: AgentState) -> AgentState:
    """
    Convert the AI-generated cloud architecture
    into a Mermaid architecture diagram.
    """

    architecture = state.get("architecture", {})

    frontend = architecture.get("frontend", "Frontend")
    backend = architecture.get("backend", "Backend")
    database = architecture.get("database", "Database")
    storage = architecture.get("storage", "Storage")
    authentication = architecture.get("authentication", "Authentication")
    networking = architecture.get("networking", "Networking")
    compute = architecture.get("compute", "Compute")
    monitoring = architecture.get("monitoring", "Monitoring")
    security = architecture.get("security", "Security")

    from backend.core.domain_analyzer import analyze_domain

    requirements = state.get("requirements", "")
    project_name = state.get("project_name", "App")

    domain_spec = analyze_domain(requirements, project_name)
    diagram = domain_spec.architecture_spec.get("diagram") or domain_spec.architecture_spec.get("mermaid_diagram", "")

    if not diagram:
        clean_name = re.sub(r'[^a-zA-Z0-9]+', '', project_name) or "App"
        diagram = (
            "flowchart TD\n"
            f'  subgraph Clients\n    USER["User Clients"]\n  end\n'
            f'  subgraph Cloud Perimeter\n    LB["Load Balancer (HTTPS)"]\n  end\n'
            f'  subgraph Core Backend\n    API["{clean_name} Service"]\n  end\n'
            f'  subgraph Persistence\n    DB[("PostgreSQL Database")]\n  end\n'
            "  USER --> LB --> API --> DB"
        )

    state.setdefault("architecture", {})["diagram"] = diagram
    state["architecture_diagram"] = diagram
    return state