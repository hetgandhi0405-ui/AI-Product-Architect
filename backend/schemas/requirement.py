from pydantic import BaseModel, Field
from typing import List, Optional


class RequirementRequest(BaseModel):
    """Customer input for generating a complete software project."""

    description: str = Field(
        ...,
        min_length=10,
        description="Single natural-language customer prompt describing the product to build",
    )

    project_name: Optional[str] = Field(
        None,
        description="Optional project name. If omitted, the pipeline derives one from the prompt.",
    )

    users: Optional[int] = Field(None, description="Expected number of users")
    features: List[str] = Field(default_factory=list, description="Optional structured features")
    security_level: Optional[str] = Field("medium", description="Required security level")
    availability: Optional[str] = Field("medium", description="Required availability level")
