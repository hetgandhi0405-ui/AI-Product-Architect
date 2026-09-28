from backend.agents.state import AgentState


def terraform_agent(state: AgentState) -> AgentState:
    """
    Convert the infrastructure blueprint into
    Terraform Infrastructure-as-Code.
    """

    architecture = state.get("architecture", {})
    infrastructure = architecture.get("infrastructure", {})
    resources = infrastructure.get("resources", [])

    terraform_resources = []

    for resource in resources:
        resource_type = resource.get("type", "resource")
        service = resource.get("service", "AWS Service")
        purpose = resource.get("purpose", "")

        terraform_resources.append({
            "resource_type": resource_type,
            "service": service,
            "purpose": purpose
        })

    main_tf = """terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  required_version = ">= 1.6.0"
}

provider "aws" {
  region = var.aws_region
}
"""

    variables_tf = """variable "aws_region" {
  description = "AWS region for the infrastructure"
  type        = string
  default     = "ap-south-1"
}
"""

    outputs_tf = """output "architecture_provider" {
  description = "Cloud provider used by the generated architecture"
  value       = "AWS"
}

output "resource_count" {
  description = "Number of infrastructure resources identified"
  value       = var.resource_count
}
"""

    resource_count = len(terraform_resources)

    variables_tf += f"""
variable "resource_count" {{
  description = "Number of infrastructure resources"
  type        = number
  default     = {resource_count}
}}
"""

    blueprint = {
        "provider": "AWS",
        "files": {
            "main.tf": main_tf,
            "variables.tf": variables_tf,
            "outputs.tf": outputs_tf
        },
        "resources": terraform_resources
    }

    state["architecture"]["terraform"] = blueprint

    return state