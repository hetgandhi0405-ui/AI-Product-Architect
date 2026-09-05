from fastapi import APIRouter

from backend.agents.graph import build_agent_graph
from backend.schemas.requirement import RequirementRequest

router = APIRouter(
    prefix="/requirements",
    tags=["Requirements"]
)

agent_graph = build_agent_graph()


@router.post("/")
def process_requirement(request: RequirementRequest):
    """
    Process customer requirements through the
    Gemini-powered LangGraph workflow.
    """

    state = {
        "project_id": "api-demo-001",
        "project_name": request.project_name,
        "requirements": request.description,
        "suggestions": [],
        "architecture": {}
    }

    result = agent_graph.invoke(state)

    return {
        "project_name": result["project_name"],
        "requirements": result["requirements"],
        "suggestions": result["suggestions"],
        "architecture": result["architecture"]
    }