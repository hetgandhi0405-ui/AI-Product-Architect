from backend.agents.state import AgentState


def self_correction_agent(state: AgentState) -> AgentState:
    """
    Automatically correct common architecture validation issues.
    """

    architecture = state.get("architecture", {})

    validation = architecture.get(
        "validation",
        {}
    )

    issues = validation.get(
        "issues",
        []
    )

    corrections = []

    # --------------------------------------------------
    # Correct missing architecture components
    # --------------------------------------------------

    defaults = {
        "frontend": "Amazon S3 + CloudFront",
        "backend": "Amazon API Gateway + AWS Lambda",
        "database": "Amazon Aurora PostgreSQL",
        "storage": "Amazon S3",
        "authentication": "Amazon Cognito",
        "networking": "Amazon VPC",
        "compute": "AWS Lambda",
        "monitoring": "Amazon CloudWatch",
        "security": "AWS WAF + AWS KMS",
        "scalability": "AWS Auto Scaling",
    }

    for field, default_value in defaults.items():
        if not architecture.get(field):
            architecture[field] = default_value

            corrections.append(
                f"Added missing architecture component: "
                f"{field} -> {default_value}"
            )

    # --------------------------------------------------
    # Correct missing infrastructure blueprint
    # --------------------------------------------------

    infrastructure = architecture.get(
        "infrastructure"
    )

    if not infrastructure:
        infrastructure = {
            "provider": "AWS",
            "resources": []
        }

        architecture["infrastructure"] = infrastructure

        corrections.append(
            "Created missing AWS infrastructure blueprint."
        )

    resources = infrastructure.get(
        "resources",
        []
    )

    if not resources:
        resources = []

        resource_mapping = [
            ("frontend", "Frontend"),
            ("backend", "Backend"),
            ("database", "Database"),
            ("storage", "Storage"),
            ("authentication", "Authentication"),
            ("networking", "Networking"),
            ("compute", "Compute"),
            ("monitoring", "Monitoring"),
            ("security", "Security"),
        ]

        for field, resource_type in resource_mapping:
            service = architecture.get(field)

            if service:
                resources.append({
                    "type": resource_type.lower(),
                    "service": service,
                    "purpose": (
                        f"Provide the {resource_type.lower()} "
                        "capability for the application."
                    )
                })

        infrastructure["resources"] = resources

        corrections.append(
            "Generated missing infrastructure resources."
        )

    # --------------------------------------------------
    # Correct missing Terraform blueprint
    # --------------------------------------------------

    terraform = architecture.get(
        "terraform"
    )

    if not terraform:
        terraform = {
            "provider": "AWS",
            "files": {
                "main.tf": (
                    'terraform {\n'
                    '  required_providers {\n'
                    '    aws = {\n'
                    '      source  = "hashicorp/aws"\n'
                    '      version = "~> 6.0"\n'
                    '    }\n'
                    '  }\n'
                    '}\n'
                ),
                "variables.tf": (
                    'variable "aws_region" {\n'
                    '  description = '
                    '"AWS region for the infrastructure"\n'
                    '  type        = string\n'
                    '  default     = "ap-south-1"\n'
                    '}\n'
                ),
                "outputs.tf": (
                    'output "architecture_provider" {\n'
                    '  description = '
                    '"Cloud provider used by the architecture"\n'
                    '  value       = "AWS"\n'
                    '}\n'
                ),
            },
            "resources": resources
        }

        architecture["terraform"] = terraform

        corrections.append(
            "Generated missing Terraform blueprint."
        )

    # --------------------------------------------------
    # Store correction information
    # --------------------------------------------------

    architecture["self_correction"] = {
        "corrections_applied": corrections,
        "correction_count": len(corrections),
        "original_issues": issues,
        "status": (
            "CORRECTED"
            if corrections
            else "NO_CORRECTIONS_REQUIRED"
        )
    }

    return state