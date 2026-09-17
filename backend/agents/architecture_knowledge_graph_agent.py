import json
from typing import Any, Dict, List

from backend.agents.state import AgentState


def _add_node(
    nodes: List[Dict[str, Any]],
    node_id: str,
    node_type: str,
    name: str,
    properties: Dict[str, Any] | None = None,
) -> None:
    """Add a node if it does not already exist."""

    if any(node["id"] == node_id for node in nodes):
        return

    nodes.append(
        {
            "id": node_id,
            "type": node_type,
            "name": name,
            "properties": properties or {},
        }
    )


def _add_relationship(
    relationships: List[Dict[str, Any]],
    source: str,
    target: str,
    relationship: str,
) -> None:
    """Add a relationship if it does not already exist."""

    relation = {
        "source": source,
        "target": target,
        "relationship": relationship,
    }

    if relation not in relationships:
        relationships.append(relation)


def architecture_knowledge_graph_agent(
    state: AgentState,
) -> AgentState:
    """
    Convert the generated AI Product Architect state
    into a structured architecture knowledge graph.

    The graph contains:

    - Project
    - Product Plan
    - UI
    - API
    - Database
    - Architecture
    - Infrastructure
    - Cloud Services
    - Security
    - Monitoring
    - Dependencies
    - Environment
    - Architecture Alternatives
    """

    project_name = state.get(
        "project_name",
        "AI Product",
    )

    project_id = state.get(
        "project_id",
        "project",
    )

    requirements = state.get(
        "requirements",
        "",
    )

    architecture = state.get(
        "architecture",
        {},
    )

    product_plan = state.get(
        "product_plan",
        {},
    )

    ui_specification = state.get(
        "ui_specification",
        {},
    )

    api_specification = state.get(
        "api_specification",
        {},
    )

    database_specification = state.get(
        "database_specification",
        {},
    )

    nodes: List[Dict[str, Any]] = []

    relationships: List[Dict[str, Any]] = []

    # =========================================================
    # PROJECT
    # =========================================================

    project_node_id = f"project:{project_id}"

    _add_node(
        nodes,
        project_node_id,
        "Project",
        project_name,
        {
            "project_id": project_id,
            "requirements": requirements,
        },
    )

    # =========================================================
    # PRODUCT PLAN
    # =========================================================

    if product_plan:

        product_plan_id = f"product_plan:{project_id}"

        _add_node(
            nodes,
            product_plan_id,
            "ProductPlan",
            "Product Plan",
            product_plan,
        )

        _add_relationship(
            relationships,
            project_node_id,
            product_plan_id,
            "HAS_PRODUCT_PLAN",
        )

    # =========================================================
    # UI / FRONTEND
    # =========================================================

    if ui_specification:

        ui_node_id = f"ui:{project_id}"

        _add_node(
            nodes,
            ui_node_id,
            "Frontend",
            "UI / Frontend",
            ui_specification,
        )

        _add_relationship(
            relationships,
            project_node_id,
            ui_node_id,
            "HAS_FRONTEND",
        )

    # =========================================================
    # API / BACKEND
    # =========================================================

    if api_specification:

        api_node_id = f"api:{project_id}"

        _add_node(
            nodes,
            api_node_id,
            "API",
            "Backend API",
            api_specification,
        )

        _add_relationship(
            relationships,
            project_node_id,
            api_node_id,
            "HAS_API",
        )

    # =========================================================
    # DATABASE
    # =========================================================

    if database_specification:

        database_node_id = f"database:{project_id}"

        _add_node(
            nodes,
            database_node_id,
            "Database",
            "Database",
            database_specification,
        )

        _add_relationship(
            relationships,
            project_node_id,
            database_node_id,
            "USES_DATABASE",
        )

        if api_specification:
            _add_relationship(
                relationships,
                f"api:{project_id}",
                database_node_id,
                "READS_WRITES",
            )

    # =========================================================
    # ARCHITECTURE
    # =========================================================

    architecture_node_id = f"architecture:{project_id}"

    architecture_properties = {
        key: value
        for key, value in architecture.items()
        if key
        not in {
            "architecture_alternatives",
            "architecture_evaluation",
            "knowledge_graph",
        }
    }

    _add_node(
        nodes,
        architecture_node_id,
        "Architecture",
        "Primary Architecture",
        architecture_properties,
    )

    _add_relationship(
        relationships,
        project_node_id,
        architecture_node_id,
        "HAS_ARCHITECTURE",
    )

    # =========================================================
    # ARCHITECTURE COMPONENTS
    # =========================================================

    component_mapping = {
        "frontend": "Frontend",
        "backend": "Backend",
        "database": "Database",
        "storage": "Storage",
        "authentication": "Authentication",
        "networking": "Networking",
        "compute": "Compute",
        "monitoring": "Monitoring",
        "security": "Security",
        "scalability": "Scalability",
    }

    for key, node_type in component_mapping.items():

        value = architecture.get(
            key
        )

        if value is None or value == "":
            continue

        node_id = (
            f"{node_type.lower()}:{project_id}"
        )

        _add_node(
            nodes,
            node_id,
            node_type,
            str(value),
            {
                "architecture_field": key,
                "value": value,
            },
        )

        _add_relationship(
            relationships,
            architecture_node_id,
            node_id,
            "CONTAINS",
        )

    # =========================================================
    # INFRASTRUCTURE
    # =========================================================

    infrastructure = architecture.get(
        "infrastructure",
        {},
    )

    if isinstance(infrastructure, dict) and infrastructure:

        infrastructure_node_id = (
            f"infrastructure:{project_id}"
        )

        _add_node(
            nodes,
            infrastructure_node_id,
            "Infrastructure",
            "Cloud Infrastructure",
            infrastructure,
        )

        _add_relationship(
            relationships,
            architecture_node_id,
            infrastructure_node_id,
            "DEPLOYED_ON",
        )

        # Create resource nodes.
        resources = infrastructure.get(
            "resources",
            infrastructure.get(
                "components",
                [],
            ),
        )

        if isinstance(resources, list):

            for index, resource in enumerate(
                resources,
                start=1,
            ):

                if isinstance(resource, dict):

                    resource_name = str(
                        resource.get(
                            "name",
                            resource.get(
                                "resource",
                                f"Resource {index}",
                            ),
                        )
                    )

                    resource_id = (
                        f"resource:{project_id}:{index}"
                    )

                    _add_node(
                        nodes,
                        resource_id,
                        "CloudResource",
                        resource_name,
                        resource,
                    )

                    _add_relationship(
                        relationships,
                        infrastructure_node_id,
                        resource_id,
                        "CONTAINS_RESOURCE",
                    )

                else:

                    resource_id = (
                        f"resource:{project_id}:{index}"
                    )

                    _add_node(
                        nodes,
                        resource_id,
                        "CloudResource",
                        str(resource),
                        {
                            "value": resource,
                        },
                    )

                    _add_relationship(
                        relationships,
                        infrastructure_node_id,
                        resource_id,
                        "CONTAINS_RESOURCE",
                    )

    # =========================================================
    # TERRAFORM
    # =========================================================

    terraform = architecture.get(
        "terraform",
        {},
    )

    if isinstance(terraform, dict) and terraform:

        terraform_node_id = (
            f"terraform:{project_id}"
        )

        _add_node(
            nodes,
            terraform_node_id,
            "Terraform",
            "Terraform Infrastructure",
            terraform,
        )

        _add_relationship(
            relationships,
            architecture_node_id,
            terraform_node_id,
            "DEFINED_BY",
        )

    # =========================================================
    # DEPENDENCIES
    # =========================================================

    dependency_specification = (
        architecture.get(
            "dependency_specification",
            state.get(
                "dependency_specification",
                {},
            ),
        )
    )

    if (
        isinstance(
            dependency_specification,
            dict,
        )
        and dependency_specification
    ):

        dependency_node_id = (
            f"dependencies:{project_id}"
        )

        _add_node(
            nodes,
            dependency_node_id,
            "Dependencies",
            "Project Dependencies",
            dependency_specification,
        )

        _add_relationship(
            relationships,
            project_node_id,
            dependency_node_id,
            "HAS_DEPENDENCIES",
        )

    # =========================================================
    # ENVIRONMENT CONFIGURATION
    # =========================================================

    environment_configuration = (
        architecture.get(
            "environment_configuration",
            state.get(
                "environment_configuration",
                {},
            ),
        )
    )

    if (
        isinstance(
            environment_configuration,
            dict,
        )
        and environment_configuration
    ):

        environment_node_id = (
            f"environment:{project_id}"
        )

        _add_node(
            nodes,
            environment_node_id,
            "Environment",
            "Environment Configuration",
            environment_configuration,
        )

        _add_relationship(
            relationships,
            project_node_id,
            environment_node_id,
            "HAS_ENVIRONMENT",
        )

    # =========================================================
    # ARCHITECTURE ALTERNATIVES
    # =========================================================

    alternatives_data = architecture.get(
        "architecture_alternatives",
        {},
    )

    if isinstance(
        alternatives_data,
        dict,
    ):

        alternatives = alternatives_data.get(
            "alternatives",
            [],
        )

        if isinstance(
            alternatives,
            list,
        ):

            alternatives_group_id = (
                f"alternatives:{project_id}"
            )

            _add_node(
                nodes,
                alternatives_group_id,
                "ArchitectureAlternatives",
                "Architecture Alternatives",
                {
                    "count": len(alternatives),
                },
            )

            _add_relationship(
                relationships,
                architecture_node_id,
                alternatives_group_id,
                "HAS_ALTERNATIVES",
            )

            for index, alternative in enumerate(
                alternatives,
                start=1,
            ):

                if not isinstance(
                    alternative,
                    dict,
                ):
                    continue

                alternative_id = str(
                    alternative.get(
                        "id",
                        f"architecture_{index}",
                    )
                )

                alternative_name = str(
                    alternative.get(
                        "name",
                        f"Architecture Option {index}",
                    )
                )

                alternative_node_id = (
                    f"alternative:{project_id}:{alternative_id}"
                )

                _add_node(
                    nodes,
                    alternative_node_id,
                    "ArchitectureAlternative",
                    alternative_name,
                    alternative,
                )

                _add_relationship(
                    relationships,
                    alternatives_group_id,
                    alternative_node_id,
                    "CONTAINS_ALTERNATIVE",
                )

    # =========================================================
    # ARCHITECTURE EVALUATION
    # =========================================================

    evaluation = architecture.get(
        "architecture_evaluation",
        {},
    )

    if isinstance(
        evaluation,
        dict,
    ) and evaluation:

        evaluation_node_id = (
            f"evaluation:{project_id}"
        )

        _add_node(
            nodes,
            evaluation_node_id,
            "ArchitectureEvaluation",
            "Architecture Evaluation",
            evaluation,
        )

        _add_relationship(
            relationships,
            architecture_node_id,
            evaluation_node_id,
            "HAS_EVALUATION",
        )

    # =========================================================
    # CORE COMPONENT RELATIONSHIPS
    # =========================================================

    frontend_id = f"frontend:{project_id}"
    backend_id = f"backend:{project_id}"
    database_id = f"database:{project_id}"
    authentication_id = (
        f"authentication:{project_id}"
    )
    storage_id = f"storage:{project_id}"
    networking_id = (
        f"networking:{project_id}"
    )
    compute_id = f"compute:{project_id}"
    monitoring_id = (
        f"monitoring:{project_id}"
    )
    security_id = f"security:{project_id}"

    if any(
        node["id"] == frontend_id
        for node in nodes
    ) and any(
        node["id"] == backend_id
        for node in nodes
    ):
        _add_relationship(
            relationships,
            frontend_id,
            backend_id,
            "CALLS",
        )

    if any(
        node["id"] == backend_id
        for node in nodes
    ) and any(
        node["id"] == database_id
        for node in nodes
    ):
        _add_relationship(
            relationships,
            backend_id,
            database_id,
            "USES",
        )

    if any(
        node["id"] == backend_id
        for node in nodes
    ) and any(
        node["id"] == authentication_id
        for node in nodes
    ):
        _add_relationship(
            relationships,
            backend_id,
            authentication_id,
            "USES",
        )

    if any(
        node["id"] == backend_id
        for node in nodes
    ) and any(
        node["id"] == storage_id
        for node in nodes
    ):
        _add_relationship(
            relationships,
            backend_id,
            storage_id,
            "USES",
        )

    if any(
        node["id"] == backend_id
        for node in nodes
    ) and any(
        node["id"] == compute_id
        for node in nodes
    ):
        _add_relationship(
            relationships,
            backend_id,
            compute_id,
            "RUNS_ON",
        )

    if any(
        node["id"] == backend_id
        for node in nodes
    ) and any(
        node["id"] == networking_id
        for node in nodes
    ):
        _add_relationship(
            relationships,
            backend_id,
            networking_id,
            "USES_NETWORK",
        )

    if any(
        node["id"] == backend_id
        for node in nodes
    ) and any(
        node["id"] == monitoring_id
        for node in nodes
    ):
        _add_relationship(
            relationships,
            backend_id,
            monitoring_id,
            "MONITORED_BY",
        )

    if any(
        node["id"] == architecture_node_id
        for node in nodes
    ) and any(
        node["id"] == security_id
        for node in nodes
    ):
        _add_relationship(
            relationships,
            architecture_node_id,
            security_id,
            "PROTECTED_BY",
        )

    # =========================================================
    # KNOWLEDGE GRAPH SUMMARY
    # =========================================================

    knowledge_graph = {
        "graph_type": "Architecture Knowledge Graph",
        "version": "1.0",
        "project": {
            "project_id": project_id,
            "project_name": project_name,
        },
        "nodes": nodes,
        "relationships": relationships,
        "statistics": {
            "node_count": len(nodes),
            "relationship_count": len(
                relationships
            ),
        },
    }

    architecture[
        "knowledge_graph"
    ] = knowledge_graph

    state[
        "architecture"
    ] = architecture

    return state