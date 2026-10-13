from typing import Any, Dict, List
from backend.agents.state import AgentState

# Pinned AWS pricing table for us-east-1 (as of January 2026)
AWS_PRICE_CATALOG = {
    "region": "us-east-1",
    "prices_as_of": "2026-01-01",
    "disclaimer": "Estimates based on published AWS on-demand pricing. Does not reflect taxes, credits, or actual invoice totals.",
    "fargate": {
        "vcpu_hourly": 0.04048,
        "gb_memory_hourly": 0.004445,
    },
    "rds": {
        "db.t4g.micro": 0.016,     # ~$11.68 / mo
        "db.t4g.small": 0.032,     # ~$23.36 / mo
        "db.t4g.medium": 0.064,    # ~$46.72 / mo
        "storage_gb_monthly": 0.115, # gp3
    },
    "alb": {
        "fixed_hourly": 0.0225,    # ~$16.43 / mo
        "lcu_hourly": 0.008,
    },
    "public_ipv4": {
        "hourly": 0.005,           # ~$3.65 / mo
    },
    "ecr": {
        "gb_monthly": 0.10,
    }
}


def cost_agent(state: AgentState) -> AgentState:
    """
    Estimate monthly infrastructure cost using pinned AWS price table.
    Outputs estimated: true, breakdown components, total, and recommendations.
    Never claims billing accuracy.
    """
    hours_per_month = 730.0

    # Extract infrastructure parameters from state or defaults
    arch = state.get("architecture", {})
    infra = arch.get("infrastructure", {})

    # Fargate specs
    fargate_cpu = infra.get("fargate_cpu", 256)       # 256 units = 0.25 vCPU
    fargate_memory = infra.get("fargate_memory", 512) # 512 MB = 0.5 GB
    desired_count = infra.get("desired_count", 1)

    vcpu_count = (fargate_cpu / 1024.0) * desired_count
    gb_count = (fargate_memory / 1024.0) * desired_count

    fargate_vcpu_cost = round(vcpu_count * AWS_PRICE_CATALOG["fargate"]["vcpu_hourly"] * hours_per_month, 2)
    fargate_mem_cost = round(gb_count * AWS_PRICE_CATALOG["fargate"]["gb_memory_hourly"] * hours_per_month, 2)
    fargate_total = round(fargate_vcpu_cost + fargate_mem_cost, 2)

    # RDS specs
    db_class = infra.get("db_instance_class", "db.t4g.micro")
    rds_hourly = AWS_PRICE_CATALOG["rds"].get(db_class, AWS_PRICE_CATALOG["rds"]["db.t4g.micro"])
    rds_compute_cost = round(rds_hourly * hours_per_month, 2)
    rds_storage_cost = round(20 * AWS_PRICE_CATALOG["rds"]["storage_gb_monthly"], 2)
    rds_total = round(rds_compute_cost + rds_storage_cost, 2)

    # ALB specs
    alb_fixed_cost = round(AWS_PRICE_CATALOG["alb"]["fixed_hourly"] * hours_per_month, 2)
    alb_lcu_cost = round(AWS_PRICE_CATALOG["alb"]["lcu_hourly"] * hours_per_month * 0.5, 2) # approx 0.5 LCU
    alb_total = round(alb_fixed_cost + alb_lcu_cost, 2)

    # Public IPv4 (ECS tasks with assign_public_ip + ALB)
    # 2 public subnets for ALB + desired_count tasks
    ipv4_count = 2 + desired_count
    ipv4_total = round(ipv4_count * AWS_PRICE_CATALOG["public_ipv4"]["hourly"] * hours_per_month, 2)

    # ECR storage (approx 1 GB)
    ecr_total = round(1.0 * AWS_PRICE_CATALOG["ecr"]["gb_monthly"], 2)

    monthly_total = round(fargate_total + rds_total + alb_total + ipv4_total + ecr_total, 2)

    components = {
        "ecs_fargate": {
            "vcpus": round(vcpu_count, 2),
            "memory_gb": round(gb_count, 2),
            "tasks": desired_count,
            "monthly_cost_usd": fargate_total,
        },
        "rds_postgres": {
            "instance_class": db_class,
            "allocated_storage_gb": 20,
            "monthly_cost_usd": rds_total,
        },
        "application_load_balancer": {
            "monthly_cost_usd": alb_total,
        },
        "public_ipv4_addresses": {
            "count": ipv4_count,
            "monthly_cost_usd": ipv4_total,
        },
        "ecr_registry_storage": {
            "monthly_cost_usd": ecr_total,
        }
    }

    recommendations: List[str] = []
    if monthly_total > 80.0:
        recommendations.append("Consider downsizing RDS instance to db.t4g.micro or consolidating task resources.")
    if desired_count > 2:
        recommendations.append("Review whether desired task count can be auto-scaled down during off-peak hours.")
    recommendations.append("Use AWS Savings Plans or Reserved Instances for predictable steady-state workloads.")

    state["cost_analysis"] = {
        "estimated": True,
        "currency": "USD",
        "region": AWS_PRICE_CATALOG["region"],
        "prices_as_of": AWS_PRICE_CATALOG["prices_as_of"],
        "disclaimer": AWS_PRICE_CATALOG["disclaimer"],
        "monthly_total_usd": monthly_total,
        "components": components,
        "recommendations": recommendations,
    }

    return state
