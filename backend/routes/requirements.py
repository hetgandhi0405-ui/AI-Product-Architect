from fastapi import APIRouter
from backend.schemas.requirement import RequirementRequest

router = APIRouter(
    prefix="/requirements",
    tags=["Requirements"]
)


@router.post("/")
def create_requirement(requirement: RequirementRequest):

    return {
        "status": "received",
        "message": "Customer requirement received successfully",
        "requirement": requirement.model_dump()
    }