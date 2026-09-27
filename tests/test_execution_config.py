from backend.core.execution_config import get_execution_config


def test_quick_mode_skips_optional_nodes():
    config = get_execution_config("QUICK")

    assert config.should_run("architecture") is True
    assert config.should_run("dynamic_router") is False
    assert config.should_run("plugin_tool") is False
    assert config.should_run("monitoring") is False


def test_test_mode_skips_heavy_simulation():
    config = get_execution_config("TEST")

    assert config.should_run("architecture") is True
    assert config.should_run("digital_twin") is False
    assert config.should_run("what_if_engine") is False
    assert config.should_run("architecture_simulator") is False
    assert config.should_run("security") is True


def test_full_mode_runs_every_node():
    config = get_execution_config("FULL")

    assert config.should_run("architecture") is True
    assert config.should_run("dynamic_router") is True
    assert config.should_run("digital_twin") is True
    assert config.should_run("monitoring") is True


def test_invalid_execution_mode():
    try:
        get_execution_config("INVALID")
        assert False
    except ValueError:
        assert True
