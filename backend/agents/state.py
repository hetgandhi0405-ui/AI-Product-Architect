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

    # Phase 2 — Extended Validation
    dependency_validation: Dict[str, Any]  # requirements.txt + package.json
    frontend_validation: Dict[str, Any]    # JSX structure, index.html, api.js
    security_validation: Dict[str, Any]    # OWASP static analysis
    validation_report: Dict[str, Any]      # Unified report with deployment_ready flag

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

    # Deployment Pipeline (Day 1)
    deploy_mode: str  # "dry-run" or "real"
    docker_status: str  # PASSED | FAILED | SKIPPED | UNAVAILABLE
    image_name: str
    image_tag: str
    docker_error: Optional[str]

    registry_status: str  # PASSED | FAILED | SKIPPED | UNAVAILABLE
    registry_url: Optional[str]
    image_uri: Optional[str]
    registry_error: Optional[str]

    terraform_status: str  # PASSED | FAILED | SKIPPED | UNAVAILABLE
    terraform_path: Optional[str]
    deployment_status: str  # PASSED | FAILED | SKIPPED | UNAVAILABLE
    deployment_timestamp: Optional[str]
    deployment_error: Optional[str]
    service_url: Optional[str]

    deployment_validation_status: str  # PASSED | FAILED | SKIPPED | UNAVAILABLE
    health_status: str  # HEALTHY | DEGRADED | UNHEALTHY | INSUFFICIENT_DATA
    validation_errors: List[str]

    # Telemetry and Monitoring (Day 2)
    telemetry_status: str  # PASSED | FAILED | SKIPPED | UNAVAILABLE
    telemetry_data: Dict[str, Any]
    performance_analysis: Dict[str, Any]
    cost_analysis: Dict[str, Any]
    reliability_analysis: Dict[str, Any]
    architecture_analysis: Dict[str, Any]

    # Optimization Loop (Day 3)
    optimization_candidates: List[Dict[str, Any]]
    optimization_recommendation: Dict[str, Any]

    # ─────────────────────────────────────────────────────────
    # PHASE 1 — Product Generation
    # ─────────────────────────────────────────────────────────
    execution_mode: str  # QUICK | FULL | TEST
    product_metadata: Dict[str, Any]  # Extracted from generated product (tech, ports, deps)

    # ─────────────────────────────────────────────────────────
    # PHASE 3 — Cloud Architecture Generation
    # ─────────────────────────────────────────────────────────
    cloud_architecture_spec: Dict[str, Any]  # Structured cloud infra spec from actual product

    # ─────────────────────────────────────────────────────────
    # PHASE 4 — Infrastructure State
    # ─────────────────────────────────────────────────────────
    infrastructure_state: Dict[str, Any]  # Canonical machine-readable infrastructure state
    infrastructure_state_path: Optional[str]  # Path to written infrastructure_state.json

    # ─────────────────────────────────────────────────────────
    # PHASE 5 — Architecture Diagram
    # ─────────────────────────────────────────────────────────
    architecture_diagram: str  # Mermaid diagram generated from infrastructure_state

    # ─────────────────────────────────────────────────────────
    # PHASE 6 — Terraform Generation
    # ─────────────────────────────────────────────────────────
    terraform_generation: Dict[str, Any]  # Per-file Terraform content map
    terraform_validation: Dict[str, Any]  # fmt / validate / plan results
    terraform_correction_attempts: int
    max_terraform_correction_attempts: int

    # ─────────────────────────────────────────────────────────
    # PHASE 8 — Deployment (Approval + Rollback)
    # ─────────────────────────────────────────────────────────
    deployment_approval: Dict[str, Any]      # {approved, approver, timestamp, mode}
    rollback_state: Dict[str, Any]           # Previous known-good infra snapshot
    deployment_history: List[Dict[str, Any]] # Ordered list of past deployments

    # ─────────────────────────────────────────────────────────
    # PHASE 9 — Deployment Verification
    # ─────────────────────────────────────────────────────────
    smoke_test_results: Dict[str, Any]  # Endpoint smoke test results post-deployment
    live_frontend_url: Optional[str]
    live_backend_url: Optional[str]

    # ─────────────────────────────────────────────────────────
    # PHASE 11 — Agentic Optimization
    # ─────────────────────────────────────────────────────────
    security_recommendations: Dict[str, Any]  # From security optimization agent

    # ─────────────────────────────────────────────────────────
    # PHASE 12 — RL Environment
    # ─────────────────────────────────────────────────────────
    rl_state: Dict[str, Any]       # Current RL environment state
    rl_action: Dict[str, Any]      # Last RL action taken
    rl_evaluation: Dict[str, Any]  # RL evaluation result with reward
    rl_policy_validated: bool      # Whether the proposed policy passed safety checks

    # ─────────────────────────────────────────────────────────
    # PHASE 15 — Fine-tuning Readiness
    # ─────────────────────────────────────────────────────────
    finetuning_dataset_record: Dict[str, Any]  # Schema record for future model fine-tuning