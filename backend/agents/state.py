from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):
    # --------------------------------------------------
    # Project Information
    # --------------------------------------------------

    project_id: str
    project_name: str
    requirements: str

    # --------------------------------------------------
    # Requirement Analysis
    # --------------------------------------------------

    suggestions: List[str]

    # --------------------------------------------------
    # Architecture
    # --------------------------------------------------

    architecture: Dict[str, Any]

    # --------------------------------------------------
    # Validation / Self-Correction
    # --------------------------------------------------

    correction_attempts: int
    max_correction_attempts: int

    # --------------------------------------------------
    # Product Planning
    # --------------------------------------------------

    product_plan: Dict[str, Any]

    # --------------------------------------------------
    # UI/UX Specification
    # --------------------------------------------------

    ui_specification: Dict[str, Any]

    # --------------------------------------------------
    # Backend API Specification
    # --------------------------------------------------

    api_specification: Dict[str, Any]

    # --------------------------------------------------
    # Database Specification
    # --------------------------------------------------

    database_specification: Dict[str, Any]

    # --------------------------------------------------
    # Code Generation Contract
    # --------------------------------------------------

    code_generation_contract: Dict[str, Any]

    # --------------------------------------------------
    # Dependency Specification
    # --------------------------------------------------

    dependency_specification: Dict[str, Any]

    # --------------------------------------------------
    # Environment Configuration
    # --------------------------------------------------

    environment_configuration: Dict[str, Any]

    # --------------------------------------------------
    # Project Memory
    # --------------------------------------------------

    project_memory: Dict[str, Any]