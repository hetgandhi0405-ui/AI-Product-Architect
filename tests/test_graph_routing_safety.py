from backend.agents.graph import timed_conditional_node


def test_dynamic_routing_can_skip_optional_agent():
    calls = []

    def fake_agent(state):
        calls.append("executed")
        return state

    wrapped = timed_conditional_node(
        "plugin_tool",
        fake_agent,
    )

    state = {
        "execution_mode": "FULL",
        "pipeline_metrics": None,
        "dynamic_routing": {
            "skipped_agents": ["plugin_tool"],
        },
    }

    result = wrapped(state)

    assert calls == []
    assert (
        result["pipeline_metrics"]["nodes"]["plugin_tool"]["status"]
        == "SKIPPED"
    )


def test_dynamic_routing_cannot_skip_core_agent():
    calls = []

    def fake_agent(state):
        calls.append("executed")
        return state

    wrapped = timed_conditional_node(
        "architecture",
        fake_agent,
    )

    state = {
        "execution_mode": "FULL",
        "pipeline_metrics": None,
        "dynamic_routing": {
            "skipped_agents": ["architecture"],
        },
    }

    result = wrapped(state)

    assert calls == ["executed"]
    assert (
        result["pipeline_metrics"]["nodes"]["architecture"]["status"]
        == "EXECUTED"
    )


def test_quick_mode_still_skips_optional_agent():
    calls = []

    def fake_agent(state):
        calls.append("executed")
        return state

    wrapped = timed_conditional_node(
        "plugin_tool",
        fake_agent,
    )

    state = {
        "execution_mode": "QUICK",
        "pipeline_metrics": None,
        "dynamic_routing": {},
    }

    result = wrapped(state)

    assert calls == []
    assert (
        result["pipeline_metrics"]["nodes"]["plugin_tool"]["status"]
        == "SKIPPED"
    )
