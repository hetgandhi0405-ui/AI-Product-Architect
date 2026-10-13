from typing import Any, Dict, List


# Baseline monthly estimates in Indian Rupees (INR).
# These are architecture-level estimates, not live cloud prices.
DEFAULT_MONTHLY_COSTS_INR = {
    "ec2": 3000.0,
    "ecs": 3800.0,
    "eks": 6300.0,
    "lambda": 850.0,
    "rds": 3400.0,
    "aurora": 6800.0,
    "s3": 425.0,
    "cloudfront": 850.0,
    "api gateway": 680.0,
    "elasticache": 2550.0,
    "redis": 2550.0,
    "dynamodb": 2100.0,
    "cloudwatch": 680.0,
    "cognito": 425.0,
    "ses": 255.0,
    "sns": 255.0,
}


def _normalize(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip().lower()


def _extract_architecture_items(
    architecture: Dict[str, Any],
) -> List[str]:

    items = []

    keys = [
        "cloud_services",
        "services",
        "components",
        "architecture_components",
        "infrastructure_resources",
        "terraform_resources",
    ]

    for key in keys:

        value = architecture.get(key)

        if isinstance(value, list):

            for item in value:

                if isinstance(item, dict):

                    name = (
                        item.get("name")
                        or item.get("service")
                        or item.get("type")
                        or item.get("resource")
                    )

                    if name:
                        items.append(str(name))

                elif item:
                    items.append(str(item))

        elif isinstance(value, str) and value.strip():

            items.extend(
                x.strip()
                for x in value.split(",")
                if x.strip()
            )

    return list(dict.fromkeys(items))


def _estimate_service_cost(
    service: str,
) -> float:

    normalized = _normalize(service)

    for key, cost in DEFAULT_MONTHLY_COSTS_INR.items():

        if key in normalized:
            return cost

    return 0.0


def _cost_category(
    cost: float,
) -> str:

    if cost < 5000:
        return "LOW"

    if cost < 15000:
        return "MEDIUM"

    if cost < 30000:
        return "HIGH"

    return "VERY_HIGH"


def cost_intelligence_agent(
    state: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Estimate architecture-level monthly infrastructure cost
    in Indian Rupees (INR).

    These are baseline estimates and are not live cloud-provider
    prices.
    """

    architecture = state.get(
        "architecture",
        {},
    )

    if not isinstance(architecture, dict):
        architecture = {}

    services = _extract_architecture_items(
        architecture
    )

    cost_breakdown = []

    estimated_monthly_cost = 0.0

    for service in services:

        estimated_cost = _estimate_service_cost(
            service
        )

        cost_breakdown.append(
            {
                "service": service,
                "estimated_monthly_cost_inr": (
                    estimated_cost
                ),
                "currency": "INR",
                "pricing_source": "baseline_estimate",
            }
        )

        estimated_monthly_cost += estimated_cost

    estimated_monthly_cost = round(
        estimated_monthly_cost,
        2,
    )

    optimization_recommendations = []

    service_text = " ".join(
        _normalize(service)
        for service in services
    )

    if "ec2" in service_text:

        optimization_recommendations.append(
            "Consider autoscaling and right-sizing compute instances."
        )

    if "rds" in service_text or "aurora" in service_text:

        optimization_recommendations.append(
            "Use database right-sizing and storage optimization."
        )

    if "s3" in service_text:

        optimization_recommendations.append(
            "Use lifecycle policies for infrequently accessed objects."
        )

    if "cloudfront" not in service_text:

        optimization_recommendations.append(
            "Consider CDN usage for high-volume static content."
        )

    if not optimization_recommendations:

        optimization_recommendations.append(
            "Review resource sizing and usage regularly."
        )

    cost_analysis = {

        "status": "SUCCESS",

        "estimated_monthly_cost_inr": (
            estimated_monthly_cost
        ),

        "currency": "INR",

        "currency_symbol": "₹",

        "cost_category": _cost_category(
            estimated_monthly_cost
        ),

        "services_analyzed": len(services),

        "cost_breakdown": cost_breakdown,

        "optimization_recommendations": (
            optimization_recommendations
        ),

        "pricing_method": "baseline_estimate",

        "pricing_disclaimer": (
            "Estimate only. Actual cloud cost depends "
            "on provider, region, workload, usage, "
            "resource configuration, taxes, and current "
            "cloud-provider pricing."
        ),
    }

    architecture["cost_analysis"] = cost_analysis

    state["architecture"] = architecture

    state["cost_analysis"] = cost_analysis

    return state
