from backend.core.execution_config import get_execution_config


def test_execution_modes():
    quick = get_execution_config("quick")
    test = get_execution_config("TEST")
    full = get_execution_config("FULL")

    assert quick.is_quick
    assert test.is_test
    assert full.is_full

    assert not quick.should_run("dynamic_router")
    assert not quick.should_run("plugin_tool")
    assert quick.should_run("architecture")

    assert not test.should_run("digital_twin")
    assert test.should_run("plugin_tool")
    assert full.should_run("digital_twin")


def test_invalid_execution_mode():
    try:
        get_execution_config("INVALID")
    except ValueError as exc:
        assert "QUICK, TEST, or FULL" in str(exc)
    else:
        raise AssertionError("Invalid mode should raise ValueError")


def test_dynamic_routing_only_allows_optional_nodes():
    config = get_execution_config("FULL")

    assert "architecture" not in config.dynamically_routable_nodes
    assert "architecture_alternatives" in config.dynamically_routable_nodes
    assert "plugin_tool" in config.dynamically_routable_nodes


def test_quick_mode_skips_all_optional_nodes():
    config = get_execution_config("QUICK")

    assert config.should_run("architecture") is True
    assert config.should_run("dynamic_router") is False
    assert config.should_run("plugin_tool") is False
    assert config.should_run("monitoring") is False
