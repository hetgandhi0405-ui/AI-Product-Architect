from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class ProjectState(BaseModel):
    project_id: str
    project_name: str

    status: str = "created"

    requirements: Optional[Dict[str, Any]] = None

    suggestions: List[str] = []

    architecture: Optional[Dict[str, Any]] = None

    security_score: Optional[int] = None

    scalability: Optional[str] = None

    validation_status: Optional[str] = None