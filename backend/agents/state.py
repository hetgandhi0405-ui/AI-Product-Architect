from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):
    project_id: str
    project_name: str
    requirements: str
    suggestions: List[str]

    # Day 12 - Product Planner
    product_plan: Dict[str, Any]
    ui_specification: Dict[str, Any]
    api_specification: Dict[str, Any]
    database_specification: Dict[str, Any]
    code_generation_contract: Dict[str, Any]

    architecture: Dict[str, Any]

    # Validation and self-correction
    correction_attempts: int
    max_correction_attempts: int