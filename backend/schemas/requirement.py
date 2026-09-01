from pydantic import BaseModel, Field
from typing import List, Optional


class RequirementRequest(BaseModel):
    project_name: str = Field(..., description="Name of the project")

    description: str = Field(
        ...,
        description="Natural language description of what the customer wants"
    )

    users: Optional[int] = Field(
        None,
        description="Expected number of users"
    )

    features: List[str] = Field(
        default_factory=list,
        description="Required application features"
    )

    security_level: Optional[str] = Field(
        "medium",
        description="Required security level"
    )

    availability: Optional[str] = Field(
        "medium",
        description="Required availability level"
    )
