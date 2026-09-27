from backend.core.prompt_utils import compact_json


def test_compact_json_is_semantically_equivalent():
    value = {
        "name": "demo",
        "items": ["a", "b"],
        "nested": {"enabled": True},
    }

    compact = compact_json(value)

    assert compact == '{"name":"demo","items":["a","b"],"nested":{"enabled":true}}'
