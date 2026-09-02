from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):
    project_id: str
    project_name: str
    requirements: str
    suggestions: List[str]
    architecture: Dict[str, Any]