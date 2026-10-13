"""
Shared Pydantic Schemas and Contracts for AI-Product-Architect
Defines explicit typed models for all 22 agents, orchestration state,
requirement traceability, and deployment interfaces.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time


class ProjectRequest(BaseModel):
    prompt: str = Field(..., description="Natural language project requirements description")
    project_name: Optional[str] = Field(None, description="Optional customer project name")
    preferred_stack: Optional[str] = Field(None, description="Preferred technology stack")
    preferred_deployment: Optional[str] = Field("cloud_run", description="Target deployment environment")
    execution_mode: Optional[str] = Field("QUICK", description="Execution mode: QUICK, FULL, or TEST")


class RequirementItem(BaseModel):
    id: str = Field(..., description="Unique requirement ID (e.g. REQ-F-001)")
    type: str = Field(..., description="Type: functional, non_functional, security, performance, integration")
    description: str = Field(..., description="Concise requirement description")
    priority: str = Field("HIGH", description="Priority: CRITICAL, HIGH, MEDIUM, LOW")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Measurable criteria")
    status: str = Field("SATISFIED", description="Implementation status: SATISFIED, PARTIAL, UNSATISFIED")
    verification_status: str = Field("VERIFIED", description="Verification status: VERIFIED, FAILED, PENDING")
    mapped_components: List[str] = Field(default_factory=list)
    mapped_files: List[str] = Field(default_factory=list)
    mapped_endpoints: List[str] = Field(default_factory=list)
    mapped_tests: List[str] = Field(default_factory=list)


class RequirementsSpecification(BaseModel):
    project_id: str
    project_name: str
    domain: str
    user_roles: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    requirements: List[RequirementItem] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    unresolved_clarifications: List[str] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)


class FeatureItem(BaseModel):
    id: str
    name: str
    description: str
    module: str
    mapped_requirement_ids: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)


class ProductPlan(BaseModel):
    project_id: str
    scope_summary: str
    features: List[FeatureItem] = Field(default_factory=list)
    user_journeys: List[Dict[str, Any]] = Field(default_factory=list)
    milestones: List[str] = Field(default_factory=list)


class TechnologyDecisions(BaseModel):
    frontend_framework: str = "React"
    backend_framework: str = "FastAPI"
    database_engine: str = "PostgreSQL"
    auth_strategy: str = "JWT"
    api_style: str = "REST"
    cache_engine: Optional[str] = "Redis"
    infrastructure_tool: str = "Terraform"
    container_runtime: str = "Docker"
    tradeoffs_rationale: Dict[str, str] = Field(default_factory=dict)


class ArchitectureNode(BaseModel):
    id: str
    name: str
    type: str  # client, ingress, compute, database, cache, security, external
    technology: str
    responsibilities: List[str] = Field(default_factory=list)
    mapped_requirements: List[str] = Field(default_factory=list)


class ArchitectureEdge(BaseModel):
    source: str
    target: str
    label: str
    protocol: Optional[str] = "HTTPS"


class ArchitectureGraph(BaseModel):
    project_id: str
    title: str
    summary: str
    components: List[ArchitectureNode] = Field(default_factory=list)
    connections: List[ArchitectureEdge] = Field(default_factory=list)
    diagram_source: str = ""
    mermaid_diagram: str = ""
    generation_status: str = "completed"


class DatabaseField(BaseModel):
    name: str
    type: str
    primary_key: bool = False
    nullable: bool = True
    foreign_key: Optional[str] = None


class DatabaseEntity(BaseModel):
    name: str
    table_name: str
    fields: List[DatabaseField] = Field(default_factory=list)
    relationships: List[str] = Field(default_factory=list)


class DatabaseSchemaContract(BaseModel):
    engine: str = "PostgreSQL"
    entities: List[DatabaseEntity] = Field(default_factory=list)
    sql_ddl: str = ""


class APIEndpoint(BaseModel):
    path: str
    method: str
    summary: str
    auth_required: bool = False
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    mapped_requirement_ids: List[str] = Field(default_factory=list)


class APIContractSpec(BaseModel):
    title: str
    version: str = "1.0.0"
    endpoints: List[APIEndpoint] = Field(default_factory=list)


class FileManifestItem(BaseModel):
    path: str
    language: str
    size: int
    category: str  # frontend, backend, database, docker, infra, docs, tests
    mapped_requirement_ids: List[str] = Field(default_factory=list)
    status: str = "valid"


class FileManifestSpec(BaseModel):
    project_id: str
    total_files: int
    files: List[FileManifestItem] = Field(default_factory=list)


class CodingTaskFile(BaseModel):
    path: str
    action: str = "create"  # create, modify
    content: str


class CodingTaskRequest(BaseModel):
    project_id: str
    task_id: str
    requirement_ids: List[str] = Field(default_factory=list)
    instructions: str
    target_files: List[str] = Field(default_factory=list)
    existing_files: Dict[str, str] = Field(default_factory=dict)
    api_contracts: Optional[Dict[str, Any]] = None
    database_schemas: Optional[Dict[str, Any]] = None


class CodingTaskResponse(BaseModel):
    project_id: str
    task_id: str
    provider: str
    status: str  # SUCCESS, FAILED, PROVIDER_UNAVAILABLE
    files: List[CodingTaskFile] = Field(default_factory=list)
    implementation_notes: List[str] = Field(default_factory=list)
    known_limitations: List[str] = Field(default_factory=list)
    tests_to_run: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None


class TraceabilityItem(BaseModel):
    requirement_id: str
    description: str
    type: str
    status: str
    verification_status: str
    mapped_components: List[str]
    mapped_files: List[str]
    mapped_endpoints: List[str]
    mapped_tests: List[str]
    evidence: str


class TraceabilityMatrixSpec(BaseModel):
    project_id: str
    total_requirements: int
    satisfied_requirements: int
    verified_requirements: int
    implementation_coverage_pct: float
    verified_coverage_pct: float
    matrix: List[TraceabilityItem] = Field(default_factory=list)
    category_metrics: Dict[str, str] = Field(default_factory=dict)


class ValidationCheckItem(BaseModel):
    gate: str
    name: str
    status: str  # PASSED, FAILED, WARN, NOT_RUN
    message: str = ""
    evidence: Optional[str] = None


class ValidationReportSpec(BaseModel):
    project_id: str
    status: str  # PASSED, FAILED, WARN
    deployment_ready: bool
    gates_passed: int
    gates_total: int
    summary: str
    checks: List[ValidationCheckItem] = Field(default_factory=list)
    blocking_issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class DeploymentRecordSpec(BaseModel):
    deployment_id: str
    project_id: str
    mode: str = "local_preview"  # local_preview, docker, cloud_run, ecs
    status: str = "DEPLOYED"  # STARTING, DEPLOYED, STOPPED, FAILED, UNAVAILABLE
    service_url: str
    preview_url: str
    health_status: str = "HEALTHY"
    runtime_logs: List[str] = Field(default_factory=list)
    started_at: float = Field(default_factory=time.time)
    process_id: Optional[int] = None


class DeploymentControlRequest(BaseModel):
    action: str  # start, stop, restart, redeploy
    target_env: Optional[str] = "local_preview"


class ExportArtifactSpec(BaseModel):
    project_id: str
    zip_path: str
    zip_filename: str
    size_bytes: int
    file_count: int
    integrity_verified: bool
    created_at: float = Field(default_factory=time.time)


class ProjectStateContract(BaseModel):
    project_id: str
    generation_id: str
    prompt: str
    project_name: str
    requirements: RequirementsSpecification
    product_plan: ProductPlan
    technology_stack: TechnologyDecisions
    architecture: ArchitectureGraph
    api_contract: APIContractSpec
    database_schema: DatabaseSchemaContract
    file_manifest: FileManifestSpec
    generated_files: Dict[str, str] = Field(default_factory=dict)
    traceability: TraceabilityMatrixSpec
    validation_report: ValidationReportSpec
    deployment: Optional[DeploymentRecordSpec] = None
    export: Optional[ExportArtifactSpec] = None
    errors: List[str] = Field(default_factory=list)
    current_stage: str = "COMPLETED"
    final_status: str = "SUCCESS"
    elapsed_seconds: float = 0.0
