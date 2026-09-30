from pathlib import Path

import backend.core.llm_cache as llm_cache


class FakeResponse:
    def __init__(self, text):
        self.text = text


class FakeModels:
    def __init__(self):
        self.calls = 0

    def generate_content(self, **kwargs):
        self.calls += 1
        return FakeResponse("generated-response")


class FakeClient:
    def __init__(self):
        self.models = FakeModels()


def test_cache_hit_avoids_second_api_call(tmp_path, monkeypatch):
    monkeypatch.setattr(llm_cache, "CACHE_DIR", Path(tmp_path))

    client = FakeClient()

    first = llm_cache.cached_generate_content(
        client=client,
        agent_name="test_agent",
        model="test-model",
        contents="hello",
    )

    second = llm_cache.cached_generate_content(
        client=client,
        agent_name="test_agent",
        model="test-model",
        contents="hello",
    )

    assert first.text == "generated-response"
    assert second.text == "generated-response"

    # Only the first call should reach the fake API.
    assert client.models.calls == 1


def test_different_prompt_creates_new_cache_entry(tmp_path, monkeypatch):
    monkeypatch.setattr(llm_cache, "CACHE_DIR", Path(tmp_path))

    client = FakeClient()

    llm_cache.cached_generate_content(
        client=client,
        agent_name="test_agent",
        model="test-model",
        contents="prompt-one",
    )

    llm_cache.cached_generate_content(
        client=client,
        agent_name="test_agent",
        model="test-model",
        contents="prompt-two",
    )

    assert client.models.calls == 2


def test_cache_stats_track_hits_and_misses(tmp_path, monkeypatch):
    monkeypatch.setattr(llm_cache, "CACHE_DIR", Path(tmp_path))

    client = FakeClient()

    llm_cache.cached_generate_content(
        client=client,
        agent_name="stats_agent",
        model="test-model",
        contents="stats-prompt",
    )

    llm_cache.cached_generate_content(
        client=client,
        agent_name="stats_agent",
        model="test-model",
        contents="stats-prompt",
    )

    stats = llm_cache.cache_stats()

    assert stats["enabled"] is True
    assert stats["hits"] >= 1
    assert stats["misses"] >= 1
    assert stats["entries"] >= 1
