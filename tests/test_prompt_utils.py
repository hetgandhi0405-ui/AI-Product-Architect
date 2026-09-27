from backend.core.prompt_utils import compact_json


def test_compact_json_is_semantically_equivalent():
    value = {
        "name": "demo",
        "items": ["a", "b"],
        "nested": {"enabled": True},
    }

    compact = compact_json(value)

    assert compact == '{"name":"demo","items":["a","b"],"nested":{"enabled":true}}'


def test_architecture_core_keeps_only_architecture_fields():
    from backend.core.prompt_utils import architecture_core

    architecture = {
        "frontend": "React",
        "backend": "FastAPI",
        "database": "PostgreSQL",
        "storage": "S3",
        "authentication": "JWT",
        "networking": "VPC",
        "compute": "ECS",
        "monitoring": "CloudWatch",
        "security": "WAF",
        "scalability": "Auto Scaling",
        "dynamic_routing": {"agents": ["security", "testing"]},
        "security_report": {"issues": []},
        "test_specification": {"tests": []},
    }

    core = architecture_core(architecture)

    assert core == {
        "frontend": "React",
        "backend": "FastAPI",
        "database": "PostgreSQL",
        "storage": "S3",
        "authentication": "JWT",
        "networking": "VPC",
        "compute": "ECS",
        "monitoring": "CloudWatch",
        "security": "WAF",
        "scalability": "Auto Scaling",
    }
