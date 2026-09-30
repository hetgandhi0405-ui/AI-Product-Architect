import re
from typing import Dict, List

from backend.dataset.schema import get_required_columns


COLUMN_ALIASES = {
    "project_id": ["project_id", "projectid", "id", "project"],
    "domain": ["domain", "industry", "sector", "application_domain"],
    "user_prompt": ["user_prompt", "prompt", "query", "requirement_prompt"],
    "project_type": ["project_type", "application_type", "system_type", "type"],
    "features": ["features", "feature_list", "capabilities"],
    "functional_requirements": [
        "functional_requirements",
        "functional_requirement",
        "functional_requirements_text",
        "requirements",
    ],
    "non_functional_requirements": [
        "non_functional_requirements",
        "nonfunctional_requirements",
        "nfr",
        "quality_requirements",
    ],
    "users": ["users", "user_count", "target_users", "users_count"],
    "frontend_technology": [
        "frontend_technology",
        "frontend",
        "frontend_framework",
        "frontend_tech",
    ],
    "backend_technology": [
        "backend_technology",
        "backend",
        "backend_framework",
        "backend_tech",
    ],
    "database_type": ["database_type", "database", "db_type", "database_technology"],
    "authentication": ["authentication", "auth", "authentication_method"],
    "api_type": ["api_type", "api", "api_style", "api_architecture"],
    "cloud_provider": ["cloud_provider", "cloud", "provider"],
    "cloud_services": ["cloud_services", "cloud_service", "aws_services", "services"],
    "architecture_pattern": [
        "architecture_pattern",
        "architecture_style",
        "design_pattern",
        "pattern",
    ],
    "architecture_components": [
        "architecture_components",
        "components",
        "architecture_nodes",
        "nodes",
    ],
    "architecture_relationships": [
        "architecture_relationships",
        "relationships",
        "architecture_edges",
        "edges",
    ],
    "security_requirements": [
        "security_requirements",
        "security",
        "security_controls",
    ],
    "scalability_requirements": [
        "scalability_requirements",
        "scalability",
        "scaling_requirements",
    ],
    "availability_requirements": [
        "availability_requirements",
        "availability",
        "uptime_requirements",
    ],
    "external_tools": ["external_tools", "tools", "integrations", "external_services"],
    "selected_tools": ["selected_tools", "recommended_tools", "chosen_tools"],
    "dependencies": ["dependencies", "packages", "libraries", "dependency_list"],
    "environment_variables": [
        "environment_variables",
        "env_variables",
        "environment",
        "env",
    ],
    "infrastructure_resources": [
        "infrastructure_resources",
        "infrastructure",
        "resources",
        "cloud_resources",
    ],
    "terraform_resources": [
        "terraform_resources",
        "terraform",
        "terraform_config",
        "iac_resources",
    ],
    "docker_required": ["docker_required", "docker", "container_required"],
    "testing_strategy": ["testing_strategy", "testing", "test_strategy", "tests"],
    "validation_checks": ["validation_checks", "validation", "checks"],
    "validation_status": ["validation_status", "status", "validation_result"],
    "security_score": ["security_score", "security_rating", "security_score_value"],
    "architecture_score": [
        "architecture_score",
        "architecture_rating",
        "architecture_quality_score",
    ],
    "estimated_cost": ["estimated_cost", "cost", "monthly_cost", "cloud_cost"],
    "architecture_alternatives": [
        "architecture_alternatives",
        "alternatives",
        "alternative_architectures",
    ],
    "recommended_architecture": [
        "recommended_architecture",
        "architecture_recommendation",
        "recommended_design",
    ],
    "architecture_diagram": [
        "architecture_diagram",
        "diagram",
        "architecture_image",
        "architecture_mermaid",
        "mermaid",
    ],
    "final_output": ["final_output", "output", "generated_output", "result"],
}


def normalize_column_name(name: str) -> str:
    """Normalize a dataset column name for comparison."""
    return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")


def build_normalized_columns(columns: List[str]) -> Dict[str, str]:
    """Map normalized column names back to their original names."""
    return {
        normalize_column_name(column): column
        for column in columns
    }


def map_columns(columns: List[str]) -> dict:
    """
    Map source dataset columns to the 38-field AI Product Architect schema.

    Matching levels:
    - EXACT: normalized source name equals target name
    - ALIAS: source name matches a known semantic alias
    - MISSING: no supported mapping exists
    """
    normalized_columns = build_normalized_columns(columns)

    mappings = {}
    used_source_columns = set()

    for target in get_required_columns():
        target_normalized = normalize_column_name(target)

        if target_normalized in normalized_columns:
            source = normalized_columns[target_normalized]
            mappings[target] = {
                "source_column": source,
                "match_type": "EXACT",
            }
            used_source_columns.add(source)
            continue

        source = None

        for alias in COLUMN_ALIASES.get(target, []):
            alias_normalized = normalize_column_name(alias)
            if alias_normalized in normalized_columns:
                candidate = normalized_columns[alias_normalized]
                if candidate not in used_source_columns:
                    source = candidate
                    break

        if source:
            mappings[target] = {
                "source_column": source,
                "match_type": "ALIAS",
            }
            used_source_columns.add(source)
        else:
            mappings[target] = {
                "source_column": None,
                "match_type": "MISSING",
            }

    exact_matches = sum(
        1 for item in mappings.values() if item["match_type"] == "EXACT"
    )
    alias_matches = sum(
        1 for item in mappings.values() if item["match_type"] == "ALIAS"
    )
    missing = sum(
        1 for item in mappings.values() if item["match_type"] == "MISSING"
    )

    total = len(mappings)
    coverage = ((exact_matches + alias_matches) / total * 100) if total else 0.0

    return {
        "mappings": mappings,
        "summary": {
            "total_required_columns": total,
            "exact_matches": exact_matches,
            "alias_matches": alias_matches,
            "missing_columns": missing,
            "coverage_percent": round(coverage, 2),
        },
    }
