from backend.agents.dynamic_router_agent import (
    VALID_AGENTS,
    _normalize_routing_result,
)


def test_dynamic_router_normalization_filters_unknown_and_conflicts():
    result = _normalize_routing_result(
        {
            "selected_agents": [
                "architecture",
                "not-a-real-agent",
                "architecture",
            ],
            "optional_agents": [
                "architecture",
                "plugin_tool",
            ],
            "skipped_agents": [
                "plugin_tool",
                "database_spec",
                "not-a-real-agent",
            ],
            "priority_order": [
                "plugin_tool",
                "architecture",
                "database_spec",
            ],
            "routing_reasons": {
                "architecture": "required",
                "not-a-real-agent": "ignore",
            },
        }
    )

    assert result["selected_agents"] == ["architecture"]
    assert result["optional_agents"] == ["plugin_tool"]
    assert result["skipped_agents"] == ["database_spec"]
    assert result["priority_order"] == ["architecture"]
    assert set(result["routing_reasons"]) == {"architecture"}
    assert set(result["selected_agents"]).issubset(VALID_AGENTS)
