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

    def clean_text(text):
        text = str(text)
        text = re.sub(r"[\[\]{}()]", "", text)
        text = text.replace('"', "'")
        return text[:120]

    diagram = (
        "flowchart LR\n"
        "\n"
        '    User["USER"]\n'
        '    Frontend["FRONTEND"]\n'
        '    Backend["BACKEND"]\n'
        '    Database["DATABASE"]\n'
        '    Storage["STORAGE"]\n'
        '    Auth["AUTHENTICATION"]\n'
        '    Network["NETWORKING"]\n'
        '    Compute["COMPUTE"]\n'
        '    Monitoring["MONITORING"]\n'
        '    Security["SECURITY"]\n'
        "\n"
        "    User --> Security\n"
        "    Security --> Network\n"
        "    Network --> Frontend\n"
        "    Frontend --> Auth\n"
        "    Frontend --> Backend\n"
        "    Backend --> Compute\n"
        "    Compute --> Database\n"
        "    Compute --> Storage\n"
        "    Backend --> Monitoring\n"
    )

    diagram = diagram.replace("FRONTEND", clean_text(frontend))
    diagram = diagram.replace("BACKEND", clean_text(backend))
    diagram = diagram.replace("DATABASE", clean_text(database))
    diagram = diagram.replace("STORAGE", clean_text(storage))
    diagram = diagram.replace("AUTHENTICATION", clean_text(authentication))
    diagram = diagram.replace("NETWORKING", clean_text(networking))
    diagram = diagram.replace("COMPUTE", clean_text(compute))
    diagram = diagram.replace("MONITORING", clean_text(monitoring))
    diagram = diagram.replace("SECURITY", clean_text(security))

    state["architecture"]["diagram"] = diagram

    return state