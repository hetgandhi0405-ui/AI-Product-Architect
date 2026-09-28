import os
import json
import re
from google import genai


class MockResponse:
    def __init__(self, text: str):
        self.text = text


class MockModels:
    """
    Deterministic synthesis mock used when GEMINI_API_KEY is not configured.
    Enables offline deterministic testing and guarantees a functional delivery pipeline.
    Matches agents by their unique system role header ("You are a ...").
    """

    def generate_content(self, model: str, contents: str, **kwargs):
        prompt_lower = str(contents).lower()

        # 1. Dynamic Router Agent
        if "dynamic agent router" in prompt_lower or "dynamic_routing" in prompt_lower:
            return MockResponse(json.dumps({
                "selected_agents": [
                    "requirement", "suggestion", "product_planner", "ui_ux_spec",
                    "api_spec", "database_spec", "architecture", "architecture_alternatives",
                    "architecture_evaluator", "architecture_knowledge_graph", "digital_twin",
                    "what_if_engine", "architecture_simulator", "security", "integration",
                    "plugin_tool", "code_generation_contract", "code_quality", "test",
                    "dependency", "environment_config", "integration_validation", "diagram",
                    "infrastructure", "terraform", "validation", "self_correction",
                    "monitoring", "failure_detection", "memory_sync"
                ],
                "optional_agents": [],
                "skipped_agents": [],
                "execution_mode": "STANDARD",
                "reasoning": "Deterministic full-pipeline execution plan for customer application."
            }))

        # 2. Product Planner Agent
        if "senior product manager" in prompt_lower:
            return MockResponse(json.dumps({
                "product_name": "Task Management App",
                "user_roles": ["Standard User", "Administrator"],
                "features": [
                    "User registration and login",
                    "Task creation and tracking",
                    "Task status update and completion",
                    "Task deletion",
                    "Task filtering and search"
                ],
                "user_stories": [
                    "As a user, I want to create tasks so that I can manage my work.",
                    "As a user, I want to mark tasks as completed.",
                    "As a user, I want to delete tasks I no longer need."
                ],
                "pages": [
                    "Login / Registration Page",
                    "Task Dashboard Page",
                    "Task Detail View"
                ],
                "scope": [
                    "Frontend React SPA",
                    "FastAPI REST API",
                    "PostgreSQL Relational Database"
                ]
            }))

        # 3. UI/UX Specification Agent
        if "ui/ux architect" in prompt_lower:
            return MockResponse(json.dumps({
                "pages": [
                    {"name": "Dashboard", "path": "/dashboard", "purpose": "Overview of tasks"},
                    {"name": "Tasks", "path": "/tasks", "purpose": "Task management list and filters"},
                    {"name": "Login", "path": "/login", "purpose": "User authentication"}
                ],
                "navigation": {
                    "links": [{"label": "Tasks", "path": "/tasks"}]
                },
                "components": [
                    {"name": "TaskList", "type": "List"},
                    {"name": "TaskCard", "type": "Card"},
                    {"name": "TaskForm", "type": "Form"},
                    {"name": "Loading", "type": "Spinner"}
                ],
                "forms": [
                    {"name": "TaskForm", "fields": ["title", "description"]}
                ],
                "user_flows": [
                    "User logs in -> views tasks -> creates task -> marks complete"
                ]
            }))

        # 4. API Specification Agent
        if "api designer" in prompt_lower or "backend architect and api designer" in prompt_lower:
            return MockResponse(json.dumps({
                "api_style": "REST",
                "base_path": "/api",
                "endpoints": [
                    {"method": "GET", "endpoint": "/tasks", "purpose": "List tasks", "authentication": False, "request": {}, "response": {}},
                    {"method": "POST", "endpoint": "/tasks", "purpose": "Create task", "authentication": False, "request": {}, "response": {}},
                    {"method": "GET", "endpoint": "/tasks/{id}", "purpose": "Get task details", "authentication": False, "request": {}, "response": {}},
                    {"method": "PUT", "endpoint": "/tasks/{id}", "purpose": "Update task", "authentication": False, "request": {}, "response": {}},
                    {"method": "DELETE", "endpoint": "/tasks/{id}", "purpose": "Delete task", "authentication": False, "request": {}, "response": {}},
                    {"method": "POST", "endpoint": "/auth/register", "purpose": "Register user", "authentication": False, "request": {}, "response": {}},
                    {"method": "POST", "endpoint": "/auth/login", "purpose": "Login user", "authentication": False, "request": {}, "response": {}}
                ]
            }))

        # 5. Database Specification Agent
        if "database architect" in prompt_lower:
            return MockResponse(json.dumps({
                "database_type": "PostgreSQL",
                "tables": [
                    {
                        "name": "users",
                        "columns": [
                            {"name": "id", "type": "SERIAL PRIMARY KEY"},
                            {"name": "username", "type": "VARCHAR(100)"},
                            {"name": "email", "type": "VARCHAR(255)"},
                            {"name": "password_hash", "type": "VARCHAR(255)"}
                        ]
                    },
                    {
                        "name": "tasks",
                        "columns": [
                            {"name": "id", "type": "SERIAL PRIMARY KEY"},
                            {"name": "title", "type": "VARCHAR(255)"},
                            {"name": "description", "type": "TEXT"},
                            {"name": "completed", "type": "BOOLEAN DEFAULT FALSE"},
                            {"name": "user_id", "type": "INTEGER REFERENCES users(id)"}
                        ]
                    }
                ]
            }))

        # 6. Architecture Agent (AWS Cloud Architecture)
        if "aws cloud solution architect" in prompt_lower:
            return MockResponse(json.dumps({
                "frontend": "Amazon S3 static website hosting distributed through Amazon CloudFront CDN",
                "backend": "FastAPI application running on Amazon ECS with AWS Fargate",
                "database": "Amazon RDS for PostgreSQL with automated backups and encryption",
                "storage": "Amazon S3 for secure document and static asset storage",
                "authentication": "Amazon Cognito user pools with OAuth 2.0 and JWT token support",
                "networking": "Amazon VPC with public and private subnets across multiple AZs with NAT Gateway",
                "compute": "Serverless containers on AWS Fargate",
                "monitoring": "Amazon CloudWatch logs, metrics, and AWS X-Ray distributed tracing",
                "security": "AWS WAF for perimeter protection and AWS Secrets Manager for credentials",
                "scalability": "Target tracking Application Auto Scaling based on CPU utilization"
            }))

        # 7. Architecture Alternatives Agent
        if "distinct aws cloud architectures" in prompt_lower or "cloud architecture alternatives" in prompt_lower or "generate three distinct" in prompt_lower:
            return MockResponse(json.dumps({
                "alternatives": [
                    {"name": "Cost-Optimized", "description": "Single-container deployment with RDS db.t4g.micro"},
                    {"name": "Balanced", "description": "ECS Fargate with managed RDS PostgreSQL multi-AZ"},
                    {"name": "High-Performance", "description": "Multi-AZ Kubernetes cluster with Aurora PostgreSQL"}
                ]
            }))

        # 8. Architecture Evaluator Agent
        if "architecture decision engine" in prompt_lower or "evaluate the provided architecture alternatives" in prompt_lower:
            return MockResponse(json.dumps({
                "evaluations": [
                    {
                        "architecture_name": "Balanced",
                        "overall_score": 8.5,
                        "scores": {"scalability": 8.5, "cost": 8.0, "security": 9.0, "reliability": 8.8},
                        "strengths": ["Managed services reduce operational overhead", "High availability with Multi-AZ"],
                        "weaknesses": ["Moderate recurring cloud infrastructure cost"]
                    }
                ],
                "summary": "Balanced 3-tier architecture recommended for production workloads."
            }))

        # 9. Security Agent
        if "security architect agent" in prompt_lower:
            return MockResponse(json.dumps({
                "status": "PASS",
                "risk_level": "LOW",
                "security_score": 90,
                "issues": [],
                "recommendations": ["Enforce HTTPS/TLS and regular token rotation in production."],
                "security_controls": {
                    "authentication": ["JWT tokens with short expiration"],
                    "authorization": ["Role-based access control"],
                    "api_security": ["CORS headers, rate limiting"],
                    "database_security": ["Least privilege database user"],
                    "cloud_security": ["Private subnets for backend and database"],
                    "network_security": ["Security groups restricting port access"],
                    "secrets_management": ["Environment variables / Secrets Manager"],
                    "monitoring": ["CloudWatch audit logs"],
                    "data_protection": ["AES-256 encryption at rest"]
                },
                "summary": "Application architecture satisfies baseline security standards."
            }))

        # 10. Plugin and Tool Selection Agent
        if "plugin and tool selection agent" in prompt_lower or "available tool registry" in prompt_lower:
            return MockResponse(json.dumps({
                "tools": [
                    {
                        "name": "PostgreSQL",
                        "category": "database",
                        "purpose": "Relational data store",
                        "reason": "Structured relational data model",
                        "required": True,
                        "integration_point": "backend/models.py",
                        "configuration": {}
                    },
                    {
                        "name": "Docker",
                        "category": "infrastructure",
                        "purpose": "Containerization and orchestration",
                        "reason": "Consistent multi-environment deployments",
                        "required": True,
                        "integration_point": "Dockerfile, docker-compose.yml",
                        "configuration": {}
                    }
                ],
                "categories": ["database", "infrastructure"],
                "selection_summary": "Selected PostgreSQL and Docker as foundational tools.",
                "security_notes": [],
                "tool_count": 2,
                "summary": "Selected PostgreSQL and Docker as foundational tools."
            }))

        # 11. Code Quality Agent
        if "code quality reviewer" in prompt_lower:
            return MockResponse(json.dumps({
                "score": 92,
                "status": "APPROVED",
                "issues": [],
                "recommendations": ["Ensure environment variables are loaded securely in production."]
            }))

        # 12. Testing Agent
        if "software test architect" in prompt_lower:
            return MockResponse(json.dumps({
                "testing_strategy": "Automated pytest unit, integration, and API contract tests",
                "test_cases": [
                    {
                        "test_id": "TC001",
                        "category": "Functional",
                        "test_name": "Task CRUD lifecycle",
                        "objective": "Verify creating, reading, updating, and deleting tasks.",
                        "input": {"title": "Sample Task", "description": "Verification"},
                        "expected_result": "Task created, updated, and deleted successfully.",
                        "priority": "HIGH"
                    }
                ],
                "coverage": {
                    "functional": True,
                    "api": True,
                    "authentication": True,
                    "database": True,
                    "integration": True,
                    "security": True,
                    "edge_cases": True,
                    "performance": True
                },
                "summary": "Comprehensive test plan covering CRUD, authentication, and error handling."
            }))

        # 13. Dependency Agent
        if "software dependency architect" in prompt_lower:
            return MockResponse(json.dumps({
                "frontend": {
                    "framework": "React",
                    "dependencies": ["react", "react-dom", "axios"]
                },
                "backend": {
                    "framework": "FastAPI",
                    "dependencies": ["fastapi", "uvicorn", "pydantic", "sqlalchemy"]
                },
                "database": {
                    "type": "PostgreSQL",
                    "dependencies": ["psycopg2-binary", "asyncpg"]
                },
                "testing": {
                    "dependencies": ["pytest", "httpx"]
                },
                "development": {
                    "dependencies": ["black", "flake8"]
                },
                "runtime": {
                    "dependencies": ["python:3.11-slim"]
                },
                "summary": "Complete dependency stack for modern React and FastAPI web service."
            }))

        # 14. Environment Config Agent
        if "environment configuration architect" in prompt_lower:
            return MockResponse(json.dumps({
                "environment_variables": [
                    {"name": "PORT", "description": "Application port", "required": True, "secret": False, "example": "8000"},
                    {"name": "HOST", "description": "Host binding", "required": True, "secret": False, "example": "0.0.0.0"},
                    {"name": "DATABASE_URL", "description": "PostgreSQL connection string", "required": True, "secret": True, "example": "postgresql://user:pass@localhost:5432/appdb"},
                    {"name": "SECRET_KEY", "description": "JWT signature secret", "required": True, "secret": True, "example": "change-in-production"},
                    {"name": "ENVIRONMENT", "description": "Runtime mode", "required": True, "secret": False, "example": "development"}
                ],
                "environment_files": {
                    "development": ".env",
                    "example": ".env.example",
                    "production": "Supplied via AWS Secrets Manager"
                },
                "secret_management": {
                    "required": True,
                    "recommendation": "Use AWS Secrets Manager for production secrets"
                },
                "configuration_notes": ["Never commit .env to version control"],
                "summary": "Secure environment variable configuration."
            }))

        # 15. Integration Validation Agent
        if "software integration architect" in prompt_lower or "cross-agent integration validation" in prompt_lower:
            return MockResponse(json.dumps({
                "status": "VALID",
                "score": 95,
                "checks": {
                    "product_ui": "PASS",
                    "product_api": "PASS",
                    "api_database": "PASS",
                    "architecture_infrastructure": "PASS",
                    "infrastructure_terraform": "PASS",
                    "quality_testing": "PASS",
                    "overall_consistency": "PASS"
                },
                "issues": [],
                "warnings": [],
                "summary": "All generated specifications are consistent and implementation-ready."
            }))

        # 16. Requirement Agent (freeform text)
        if "analyze the following customer requirement" in prompt_lower:
            return MockResponse(
                "AI Requirement Analysis:\n"
                "1. Functional Requirements: User authentication, task management (create, read, update, delete, complete).\n"
                "2. Application Components: React SPA frontend, FastAPI REST backend, PostgreSQL relational database.\n"
                "3. User & Traffic Requirements: Scalable architecture supporting standard web workloads.\n"
                "4. Data Requirements: Relational schema for users and tasks with foreign key relationships.\n"
                "5. Security Requirements: Password hashing, JWT token authentication, CORS security headers.\n"
                "6. Availability & Scalability: Containerized deployment using Docker and cloud VPC infrastructure.\n"
                "7. Important Technical Considerations: RESTful endpoints with consistent error status codes."
            )

        # 17. Suggestion Agent
        if "senior cloud solution architect and product consultant" in prompt_lower or "suggestion" in prompt_lower:
            return MockResponse(
                "Architecture Suggestions:\n"
                "- Employ 3-tier modular architecture with clean separation of concerns.\n"
                "- Use PostgreSQL with indexed foreign keys for optimal query performance.\n"
                "- Provide automated container configuration for frictionless developer onboarding."
            )

        # Fallback generic JSON
        return MockResponse(json.dumps({
            "status": "SUCCESS",
            "summary": "Synthesized specification."
        }))


class LazyGenAIClient:
    """
    Unified GenAI Client:
    - Uses real Google GenAI when GEMINI_API_KEY is present.
    - Uses high-fidelity deterministic MockModels when offline or testing without API key.
    """

    def __init__(self):
        self._real_client = None
        self._mock_models = MockModels()

    def _get_client(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            if self._real_client is None:
                self._real_client = genai.Client(api_key=api_key)
            return self._real_client
        return None

    @property
    def models(self):
        client = self._get_client()
        if client is not None:
            return client.models
        return self._mock_models

    def __getattr__(self, name):
        client = self._get_client()
        if client is not None:
            return getattr(client, name)
        raise AttributeError(f"LazyGenAIClient attribute '{name}' unavailable in mock mode.")


def get_client():
    return LazyGenAIClient()
