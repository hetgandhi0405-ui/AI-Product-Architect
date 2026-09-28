from backend.agents.state import AgentState


def validation_agent(state: AgentState) -> AgentState:
    """
    Validate the generated cloud architecture,
    infrastructure blueprint, and Terraform blueprint.
    """

    architecture = state.get("architecture", {})

    required_architecture_fields = [
        "frontend",
        "backend",
        "database",
        "storage",
        "authentication",
        "networking",
        "compute",
        "monitoring",
        "security",
        "scalability",
    ]

    required_terraform_files = [
        "main.tf",
        "variables.tf",
        "outputs.tf",
    ]

    issues = []
    checks = []

    # --------------------------------------------------
    # Architecture validation
    # --------------------------------------------------

    for field in required_architecture_fields:
        value = architecture.get(field)

        if value:
            checks.append(
                f"PASS: Architecture field '{field}' is present."
            )
        else:
            issues.append(
                f"Missing architecture field: {field}"
            )

    # --------------------------------------------------
    # Infrastructure validation
    # --------------------------------------------------

    infrastructure = architecture.get(
        "infrastructure",
        {}
    )

    resources = infrastructure.get(
        "resources",
        []
    )

    if resources:
        checks.append(
            "PASS: Infrastructure blueprint contains resources."
        )
    else:
        issues.append(
            "Infrastructure blueprint contains no resources."
        )

    # --------------------------------------------------
    # Terraform validation
    # --------------------------------------------------

    terraform = architecture.get(
        "terraform",
        {}
    )

    terraform_files = terraform.get(
        "files",
        {}
    )

    # Check required Terraform files
    for filename in required_terraform_files:

        if filename in terraform_files:
            checks.append(
                f"PASS: Terraform file '{filename}' is present."
            )
        else:
            issues.append(
                f"Missing Terraform file: {filename}"
            )

    # --------------------------------------------------
    # main.tf validation
    # --------------------------------------------------

    main_tf = terraform_files.get(
        "main.tf",
        ""
    )

    if main_tf:

        if 'provider "aws"' in main_tf:
            checks.append(
                'PASS: main.tf contains an AWS provider configuration.'
            )
        else:
            issues.append(
                'main.tf is missing provider "aws" configuration.'
            )

        if "terraform {" in main_tf:
            checks.append(
                "PASS: main.tf contains a Terraform configuration block."
            )
        else:
            issues.append(
                "main.tf is missing the Terraform configuration block."
            )

    else:
        issues.append(
            "main.tf contains no Terraform configuration."
        )

    # --------------------------------------------------
    # variables.tf validation
    # --------------------------------------------------

    variables_tf = terraform_files.get(
        "variables.tf",
        ""
    )

    if variables_tf:

        if 'variable "aws_region"' in variables_tf:
            checks.append(
                "PASS: variables.tf defines aws_region."
            )
        else:
            issues.append(
                "variables.tf is missing aws_region variable."
            )

    else:
        issues.append(
            "variables.tf contains no Terraform variables."
        )

    # --------------------------------------------------
    # outputs.tf validation
    # --------------------------------------------------

    outputs_tf = terraform_files.get(
        "outputs.tf",
        ""
    )

    if outputs_tf:

        if "output " in outputs_tf:
            checks.append(
                "PASS: outputs.tf contains an output definition."
            )
        else:
            issues.append(
                "outputs.tf contains no output definition."
            )

    else:
        issues.append(
            "outputs.tf contains no Terraform outputs."
        )

    # --------------------------------------------------
    # Terraform resource validation
    # --------------------------------------------------

    terraform_resources = terraform.get(
        "resources",
        []
    )

    if terraform_resources:

        checks.append(
            f"PASS: Terraform blueprint contains "
            f"{len(terraform_resources)} resource definition(s)."
        )

    else:

        issues.append(
            "Terraform blueprint contains no resource definitions."
        )

    # --------------------------------------------------
    # Basic architecture consistency checks
    # --------------------------------------------------

    if architecture.get("frontend") and architecture.get("backend"):
        checks.append(
            "PASS: Frontend and backend components are defined."
        )

    if architecture.get("database") and architecture.get("storage"):
        checks.append(
            "PASS: Database and storage components are defined."
        )

    if architecture.get("authentication") and architecture.get("security"):
        checks.append(
            "PASS: Authentication and security controls are defined."
        )

    if architecture.get("networking") and architecture.get("compute"):
        checks.append(
            "PASS: Networking and compute components are defined."
        )

    # --------------------------------------------------
    # Validation result
    # --------------------------------------------------

    is_valid = len(issues) == 0

    validation = {
        "status": "VALID" if is_valid else "INVALID",
        "is_valid": is_valid,
        "checks": checks,
        "issues": issues,
        "summary": (
            "Architecture passed all validation checks."
            if is_valid
            else
            f"Architecture requires correction. "
            f"{len(issues)} issue(s) detected."
        )
    }

    state["architecture"]["validation"] = validation

    return state