import importlib


class FakeModels:
    def __init__(self):
        self.calls = 0

    def generate_content(self, **kwargs):
        self.calls += 1

        class Response:
            text = "cached-result"

        return Response()


class FakeClient:
    def __init__(self):
        self.models = FakeModels()


def test_llm_cache_hit_and_miss(tmp_path, monkeypatch):
    cache = importlib.import_module("backend.core.llm_cache")

    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(cache, "CACHE_ENABLED", True)
    monkeypatch.setattr(cache, "_cache_hits", 0)
    monkeypatch.setattr(cache, "_cache_misses", 0)

    client = FakeClient()
    contents = "same-prompt"

    first = cache.cached_generate_content(
        client=client,
        agent_name="test-agent",
        model="test-model",
        contents=contents,
    )
    second = cache.cached_generate_content(
        client=client,
        agent_name="test-agent",
        model="test-model",
        contents=contents,
    )

    assert first.text == "cached-result"
    assert second.text == "cached-result"
    assert client.models.calls == 1

    stats = cache.cache_stats()
    assert stats["misses"] == 1
    assert stats["hits"] == 1
    assert stats["entries"] == 1
