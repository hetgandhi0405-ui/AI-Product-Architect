import pytest
from backend.agents.cost_agent import cost_agent
from backend.agents.state import AgentState


def test_cost_agent_baseline_estimation():
    state = AgentState(
        architecture={
            "infrastructure": {
                "fargate_cpu": 256,
                "fargate_memory": 512,
                "desired_count": 1,
                "db_instance_class": "db.t4g.micro",
            }
        }
    )
    result = cost_agent(state)
    cost = result["cost_analysis"]
    assert cost["estimated"] is True
    assert cost["currency"] == "USD"
    assert cost["region"] == "us-east-1"
    assert "components" in cost
    assert "ecs_fargate" in cost["components"]
    assert "rds_postgres" in cost["components"]
    assert "application_load_balancer" in cost["components"]
    assert cost["monthly_total_usd"] > 0
    assert "disclaimer" in cost
