from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):
    project_id: str
    project_name: str
    requirements: str

    suggestions: List[str]

    architecture: Dict[str, Any]

    correction_attempts: int
    max_correction_attempts: int

    product_plan: Dict[str, Any]

    ui_specification: Dict[str, Any]

    api_specification: Dict[str, Any]

    database_specification: Dict[str, Any]

    code_generation_contract: Dict[str, Any]

    dependency_specification: Dict[str, Any]

    environment_configuration: Dict[str, Any]