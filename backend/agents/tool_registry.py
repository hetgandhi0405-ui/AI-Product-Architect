from typing import Any, Dict, List


TOOL_REGISTRY: List[Dict[str, Any]] = [
    {
        "name": "AWS S3",
        "category": "storage",
        "capabilities": ["object storage", "file upload", "file storage", "media storage"],
        "provider": "AWS",
        "integration_type": "cloud_service",
        "security_level": "high",
    },
    {
        "name": "AWS Cognito",
        "category": "authentication",
        "capabilities": ["user authentication", "login", "signup", "identity management", "JWT"],
        "provider": "AWS",
        "integration_type": "cloud_service",
        "security_level": "high",
    },
    {
        "name": "Amazon SES",
        "category": "email",
        "capabilities": ["email", "transactional email", "email notification", "verification email"],
        "provider": "AWS",
        "integration_type": "cloud_service",
        "security_level": "high",
    },
    {
        "name": "Amazon SNS",
        "category": "messaging",
        "capabilities": ["notifications", "SMS", "messaging", "alerts"],
        "provider": "AWS",
        "integration_type": "cloud_service",
        "security_level": "high",
    },
    {
        "name": "Amazon CloudWatch",
        "category": "monitoring",
        "capabilities": ["monitoring", "logging", "metrics", "alerts", "observability"],
        "provider": "AWS",
        "integration_type": "cloud_service",
        "security_level": "high",
    },
    {
        "name": "Stripe",
        "category": "payment",
        "capabilities": ["payments", "checkout", "subscriptions", "billing", "payment processing"],
        "provider": "Stripe",
        "integration_type": "api",
        "security_level": "high",
    },
    {
        "name": "Redis",
        "category": "caching",
        "capabilities": ["caching", "session storage", "rate limiting", "fast data access"],
        "provider": "Open Source",
        "integration_type": "database",
        "security_level": "medium",
    },
    {
        "name": "Elasticsearch",
        "category": "search",
        "capabilities": ["search", "full text search", "filtering", "analytics"],
        "provider": "Elastic",
        "integration_type": "api",
        "security_level": "high",
    },
    {
        "name": "GitHub",
        "category": "development",
        "capabilities": ["source control", "repository", "version control", "CI/CD"],
        "provider": "GitHub",
        "integration_type": "developer_tool",
        "security_level": "high",
    },
    {
        "name": "Docker",
        "category": "deployment",
        "capabilities": ["containerization", "containers", "deployment", "portable environments"],
        "provider": "Docker",
        "integration_type": "developer_tool",
        "security_level": "medium",
    },
    {
        "name": "Playwright",
        "category": "testing",
        "capabilities": ["browser testing", "end-to-end testing", "UI testing", "automation"],
        "provider": "Microsoft",
        "integration_type": "testing_tool",
        "security_level": "medium",
    },
    {
        "name": "OpenTelemetry",
        "category": "observability",
        "capabilities": ["tracing", "metrics", "telemetry", "distributed tracing"],
        "provider": "Open Source",
        "integration_type": "observability_tool",
        "security_level": "medium",
    },
    {
        "name": "OWASP ZAP",
        "category": "security",
        "capabilities": ["security testing", "API security testing", "vulnerability scanning", "DAST"],
        "provider": "OWASP",
        "integration_type": "security_tool",
        "security_level": "high",
    },
    {
        "name": "Google Maps API",
        "category": "maps",
        "capabilities": ["maps", "location", "geocoding", "directions", "places"],
        "provider": "Google",
        "integration_type": "api",
        "security_level": "high",
    },
]


def get_tool_registry() -> List[Dict[str, Any]]:
    """Return the complete registered tool catalog."""
    return TOOL_REGISTRY


def get_tools_by_category(category: str) -> List[Dict[str, Any]]:
    """Return tools belonging to a specific category."""
    return [
        tool
        for tool in TOOL_REGISTRY
        if tool["category"].lower() == category.lower()
    ]


def find_tools_by_capability(
    capability: str,
) -> List[Dict[str, Any]]:
    """Find tools matching a requested capability."""
    capability = capability.lower()

    matches = []

    for tool in TOOL_REGISTRY:
        if any(
            capability in item.lower()
            or item.lower() in capability
            for item in tool["capabilities"]
        ):
            matches.append(tool)

    return matches
