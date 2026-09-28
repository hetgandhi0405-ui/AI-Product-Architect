from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict, total=False):
    project_id: str
    project_name: str
    requirements: str

    suggestions: List[str]

    product_plan: Dict[str, Any]
    ui_specification: Dict[str, Any]
    api_specification: Dict[str, Any]
    database_specification: Dict[str, Any]

    architecture: Dict[str, Any]
    monitoring: Dict[str, Any]
    failure_detection: Dict[str, Any]

    dynamic_routing: Dict[str, Any]
    tool_registry: Dict[str, Any]
    selected_tools: Dict[str, Any]

    code_generation_contract: Dict[str, Any]
    dependency_specification: Dict[str, Any]
    environment_configuration: Dict[str, Any]

    project_memory: Dict[str, Any]
    security_analysis: Dict[str, Any]

    # Code Delivery Pipeline
    file_manifest: Dict[str, Any]
    generated_files: Dict[str, str]
    assembled_project_path: str

    # Validations
    code_validation: Dict[str, Any]
    build_validation: Dict[str, Any]
    api_validation: Dict[str, Any]
    database_validation: Dict[str, Any]
    docker_validation: Dict[str, Any]

    # Self-Correction
    correction_attempts: int
    max_correction_attempts: int
    code_correction_attempts: int
    max_code_correction_attempts: int
    integration_correction_attempts: int
    max_integration_correction_attempts: int

    # Release and Export
    release_gate: Dict[str, Any]
    export: Dict[str, Any]