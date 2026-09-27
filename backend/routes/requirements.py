from fastapi import APIRouter, HTTPException

from backend.agents.graph import build_agent_graph
from backend.schemas.requirement import RequirementRequest
from backend.core.execution_config import get_execution_config
from backend.core.pipeline_metrics import create_metrics


router = APIRouter(
    prefix="/requirements",
    tags=["Requirements"]
)

# Build the LangGraph workflow once when the API starts.
agent_graph = build_agent_graph()


@router.post("/")
def process_requirement(
    request: RequirementRequest,
    execution_mode: str = "FULL",
):
    """
    Process customer requirements through the
    Gemini-powered LangGraph workflow.
    """

    try:
        config = get_execution_config(execution_mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    state = {
        "project_id": "api-demo-001",
        "execution_mode": config.mode,
        "pipeline_metrics": create_metrics(),
        "project_name": request.project_name,
        "requirements": request.description,

        # Customer-provided requirements
        "users": request.users,
        "features": request.features,
        "security_level": request.security_level,
        "availability": request.availability,

        # Initial workflow values
        "suggestions": [],
        "architecture": {},
    }

    # Execute the complete AI Product Architect pipeline.
    result = agent_graph.invoke(state)

    architecture = result.get("architecture", {})

    return {
        "execution_mode": result.get("execution_mode", config.mode),
        "pipeline_metrics": result.get("pipeline_metrics", {}),

        # Basic project information
        "project_name": result.get(
            "project_name",
            request.project_name
        ),
        "requirements": result.get(
            "requirements",
            request.description
        ),
        "suggestions": result.get(
            "suggestions",
            []
        ),

        # Customer requirements
        "users": result.get(
            "users",
            request.users
        ),
        "features": result.get(
            "features",
            request.features
        ),
        "security_level": result.get(
            "security_level",
            request.security_level
        ),
        "availability": result.get(
            "availability",
            request.availability
        ),

        # Architecture
        "architecture": architecture,
        "diagram": architecture.get(
            "diagram",
            ""
        ),
        "infrastructure": architecture.get(
            "infrastructure",
            {}
        ),

        # Tools
        "tool_registry": result.get(
            "tool_registry",
            {}
        ),
        "selected_tools": result.get(
            "selected_tools",
            {}
        ),

        # Member 2 intelligence
        "security_analysis": result.get(
            "security_analysis",
            {}
        ),
        "cost_analysis": result.get(
            "cost_analysis",
            {}
        ),
        "architecture_recommendation": result.get(
            "architecture_recommendation",
            {}
        ),
        "requirement_traceability": result.get(
            "requirement_traceability",
            {}
        ),
        "dependency_specification": result.get(
            "dependency_specification",
            {}
        ),
        "environment_configuration": result.get(
            "environment_configuration",
            {}
        ),
        "code_generation_contract": result.get(
            "code_generation_contract",
            {}
        ),
    }
