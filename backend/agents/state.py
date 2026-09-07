from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):
    project_id: str
    project_name: str
    requirements: str
    suggestions: List[str]
    architecture: Dict[str, Any]

    # Day 10 validation loop
    correction_attempts: int
    max_correction_attempts: int