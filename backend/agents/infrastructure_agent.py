from backend.agents.state import AgentState


def infrastructure_agent(state: AgentState) -> AgentState:
    """
    Convert the generated AWS architecture into
    a structured infrastructure blueprint.
    """

    architecture = state.get("architecture", {})

    infrastructure = {
        "provider": "AWS",

        "resources": [
            {
                "type": "frontend",
                "service": architecture.get("frontend", "Amazon S3 + CloudFront"),
                "purpose": "Host and deliver the web application"
            },
            {
                "type": "backend",
                "service": architecture.get("backend", "API Gateway + Lambda"),
                "purpose": "Provide application APIs and business logic"
            },
            {
                "type": "compute",
                "service": architecture.get("compute", "AWS Lambda"),
                "purpose": "Run application workloads"
            },
            {
                "type": "database",
                "service": architecture.get("database", "Amazon Aurora"),
                "purpose": "Store application and transactional data"
            },
            {
                "type": "storage",
                "service": architecture.get("storage", "Amazon S3"),
                "purpose": "Store files and application objects"
            },
            {
                "type": "authentication",
                "service": architecture.get("authentication", "Amazon Cognito"),
                "purpose": "Manage user authentication and authorization"
            },
            {
                "type": "networking",
                "service": architecture.get("networking", "Amazon VPC"),
                "purpose": "Provide secure network isolation"
            },
            {
                "type": "monitoring",
                "service": architecture.get("monitoring", "Amazon CloudWatch"),
                "purpose": "Monitor application health and performance"
            },
            {
                "type": "security",
                "service": architecture.get("security", "AWS WAF + KMS + Secrets Manager"),
                "purpose": "Protect applications, data, and credentials"
            }
        ]
    }

    state["architecture"]["infrastructure"] = infrastructure

    return state