import hashlib
import json
import os
import threading
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Optional


CACHE_DIR = Path(
    os.getenv(
        "AI_PRODUCT_ARCHITECT_LLM_CACHE",
        ".cache/llm",
    )
)

CACHE_ENABLED = os.getenv(
    "AI_PRODUCT_ARCHITECT_CACHE",
    "true",
).lower() not in {"0", "false", "no", "off"}

_cache_lock = threading.Lock()

_cache_hits = 0
_cache_misses = 0


def _cache_key(
    agent_name: str,
    model: str,
    contents: Any,
    config: Any = None,
) -> str:

    payload = {
        "agent": agent_name,
        "model": model,
        "contents": contents,
        "config": config,
    }

    serialized = json.dumps(
        payload,
        sort_keys=True,
        default=str,
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def get_cached_response(
    agent_name: str,
    model: str,
    contents: Any,
    config: Any = None,
) -> Optional[str]:

    global _cache_hits, _cache_misses

    if not CACHE_ENABLED:
        return None

    key = _cache_key(
        agent_name,
        model,
        contents,
        config,
    )

    cache_file = CACHE_DIR / f"{key}.json"

    with _cache_lock:

        if not cache_file.exists():
            _cache_misses += 1
            return None

        try:
            data = json.loads(
                cache_file.read_text(
                    encoding="utf-8"
                )
            )

            _cache_hits += 1

            return data.get("text")

        except (
            OSError,
            json.JSONDecodeError,
        ):
            _cache_misses += 1
            return None


def save_cached_response(
    agent_name: str,
    model: str,
    contents: Any,
    text: str,
    config: Any = None,
) -> None:

    if not CACHE_ENABLED:
        return

    key = _cache_key(
        agent_name,
        model,
        contents,
        config,
    )

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    cache_file = CACHE_DIR / f"{key}.json"

    data: Dict[str, Any] = {
        "agent": agent_name,
        "model": model,
        "text": text,
    }

    temporary_file = cache_file.with_suffix(
        ".tmp"
    )

    with _cache_lock:

        temporary_file.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        temporary_file.replace(
            cache_file
        )


def cached_generate_content(
    client: Any,
    agent_name: str,
    model: str,
    contents: Any,
    **kwargs: Any,
) -> Any:
    """
    Cached wrapper around Gemini generate_content().

    Cache hit:
        Returns a response-like object containing .text.

    Cache miss:
        Calls Gemini, stores response.text, and returns
        the original response object.
    """

    config = kwargs.get("config")

    cached_text = get_cached_response(
        agent_name=agent_name,
        model=model,
        contents=contents,
        config=config,
    )

    if cached_text is not None:
        return SimpleNamespace(
            text=cached_text
        )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        **kwargs,
    )

    response_text = getattr(
        response,
        "text",
        None,
    )

    if response_text:
        save_cached_response(
            agent_name=agent_name,
            model=model,
            contents=contents,
            text=response_text,
            config=config,
        )

    return response


def clear_cache() -> None:

    if not CACHE_DIR.exists():
        return

    for cache_file in CACHE_DIR.glob("*.json"):

        try:
            cache_file.unlink()

        except OSError:
            pass


def cache_stats() -> Dict[str, Any]:

    entries = 0

    if CACHE_DIR.exists():
        entries = len(
            list(
                CACHE_DIR.glob("*.json")
            )
        )

    return {
        "enabled": CACHE_ENABLED,
        "entries": entries,
        "hits": _cache_hits,
        "misses": _cache_misses,
        "directory": str(CACHE_DIR),
    }
