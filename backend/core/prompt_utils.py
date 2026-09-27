import json
from typing import Any


def compact_json(value: Any) -> str:
    """Serialize JSON compactly for LLM prompts."""
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
    )
