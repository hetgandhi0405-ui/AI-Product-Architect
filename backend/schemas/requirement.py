from pydantic import BaseModel, Field
from typing import List, Optional


class RequirementRequest(BaseModel):
    description: str = Field(
        ...,
        description="Natural language description of what the customer wants"
    )

    project_name: Optional[str] = Field(
        None,
        description="Optional name of the project. If omitted, will be derived automatically."
    )

    project_id: Optional[str] = Field(
        None,
        description="Optional custom project identifier. If omitted, a unique ID is generated."
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
