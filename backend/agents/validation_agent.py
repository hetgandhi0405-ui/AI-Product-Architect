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
            else (
                f"Architecture requires correction. "
                f"{len(issues)} issue(s) detected."
            )
        )
    }

    state["architecture"]["validation"] = validation

    return state