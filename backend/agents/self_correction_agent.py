from backend.agents.state import AgentState


def self_correction_agent(state: AgentState) -> AgentState:
    """
    Automatically correct common architecture validation issues.
    """

    architecture = state.get("architecture", {})

    correction_attempts = state.get("correction_attempts", 0)
    max_correction_attempts = state.get("max_correction_attempts", 3)

    correction_attempts += 1

    corrections = []

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

    # Correct missing architecture fields
    for field, default_value in defaults.items():
        if not architecture.get(field):
            architecture[field] = default_value
            corrections.append(
                f"Added missing architecture field '{field}' "
                f"with default '{default_value}'."
            )

    # Correct missing infrastructure blueprint
    infrastructure = architecture.get("infrastructure")

    if not infrastructure:
        architecture["infrastructure"] = {
            "provider": "AWS",
            "resources": [
                {
                    "type": "frontend",
                    "service": architecture["frontend"],
                    "purpose": "Host and deliver the web application"
                },
                {
                    "type": "backend",
                    "service": architecture["backend"],
                    "purpose": "Provide application APIs and business logic"
                },
                {
                    "type": "compute",
                    "service": architecture["compute"],
                    "purpose": "Run application workloads"
                },
                {
                    "type": "database",
                    "service": architecture["database"],
                    "purpose": "Store application and transactional data"
                },
                {
                    "type": "storage",
                    "service": architecture["storage"],
                    "purpose": "Store files and application objects"
                },
                {
                    "type": "authentication",
                    "service": architecture["authentication"],
                    "purpose": "Manage authentication and authorization"
                },
                {
                    "type": "networking",
                    "service": architecture["networking"],
                    "purpose": "Provide secure network isolation"
                },
                {
                    "type": "monitoring",
                    "service": architecture["monitoring"],
                    "purpose": "Monitor application health and performance"
                },
                {
                    "type": "security",
                    "service": architecture["security"],
                    "purpose": "Protect applications, data, and credentials"
                }
            ]
        }

        corrections.append(
            "Created missing AWS infrastructure blueprint."
        )

    # Correct missing Terraform blueprint
    terraform = architecture.get("terraform")

    if not terraform:
        architecture["terraform"] = {
            "provider": "AWS",
            "files": {
                "main.tf": (
                    'terraform {\n'
                    '  required_providers {\n'
                    '    aws = {\n'
                    '      source  = "hashicorp/aws"\n'
                    '      version = "~> 6.0"\n'
                    '    }\n'
                    '  }\n\n'
                    '  required_version = ">= 1.6.0"\n'
                    '}\n\n'
                    'provider "aws" {\n'
                    '  region = var.aws_region\n'
                    '}\n'
                ),
                "variables.tf": (
                    'variable "aws_region" {\n'
                    '  description = "AWS region for the infrastructure"\n'
                    '  type        = string\n'
                    '  default     = "ap-south-1"\n'
                    '}\n'
                ),
                "outputs.tf": (
                    'output "architecture_provider" {\n'
                    '  description = "Cloud provider used by the generated architecture"\n'
                    '  value       = "AWS"\n'
                    '}\n'
                )
            },
            "resources": []
        }

        corrections.append(
            "Created missing Terraform infrastructure blueprint."
        )

    # Update architecture
    state["architecture"] = architecture

    validation = architecture.get("validation", {})
    issues = validation.get("issues", [])

    state["architecture"]["self_correction"] = {
        "corrections_applied": corrections,
        "correction_count": len(corrections),
        "original_issues": issues,
        "status": (
            "CORRECTED"
            if corrections
            else "NO_CORRECTIONS_REQUIRED"
        ),
        "attempt": correction_attempts,
        "max_attempts": max_correction_attempts
    }

    # Store loop counters
    state["correction_attempts"] = correction_attempts
    state["max_correction_attempts"] = max_correction_attempts

    return state