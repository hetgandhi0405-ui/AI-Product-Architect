"""
Phase 15 — LLM Provider Abstraction
=====================================
All agents must go through this abstraction. This enables:
- Drop-in replacement of the base model with a fine-tuned model later
- Consistent prompt/response interface
- Testability via mock providers

Usage:
    from backend.agents.llm_provider import get_llm_provider
    llm = get_llm_provider()
    response = llm.generate(prompt)
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod

from backend.agents.llm_client import LazyGenAIClient


class LLMResponse:
    """Canonical response wrapper — model-agnostic."""
    def __init__(self, text: str):
        self.text = text.strip()


class BaseLLMProvider(ABC):
    """Abstract base — implement this interface to swap the underlying model."""

    @abstractmethod
    def generate(self, prompt: str, model: str | None = None) -> LLMResponse:
        ...


class GeminiLLMProvider(BaseLLMProvider):
    """
    Production provider using the existing LazyGenAIClient
    (deterministic mock fallback when GEMINI_API_KEY is absent).
    """

    _DEFAULT_MODEL = "gemini-3.5-flash-lite"

    def __init__(self):
        self._client = LazyGenAIClient()

    def generate(self, prompt: str, model: str | None = None) -> LLMResponse:
        m = model or self._DEFAULT_MODEL
        resp = self._client.models.generate_content(model=m, contents=prompt)
        return LLMResponse(resp.text)


class FineTunedLLMProvider(BaseLLMProvider):
    """
    Placeholder for a future fine-tuned model provider.
    Raises NotImplementedError until a real endpoint is configured.

    Fine-tuning dataset schema (for future use):
    {
        "cloud_requirement": str,
        "product_metadata": dict,
        "architecture": dict,
        "infrastructure_state": dict,
        "optimization_problem": dict,
        "action": str,
        "expected_effect": dict
    }
    """

    FINETUNED_ENDPOINT = os.environ.get("FINETUNED_LLM_ENDPOINT", "")

    def generate(self, prompt: str, model: str | None = None) -> LLMResponse:
        if not self.FINETUNED_ENDPOINT:
            raise NotImplementedError(
                "FineTunedLLMProvider requires FINETUNED_LLM_ENDPOINT env var. "
                "Fine-tuning is not yet implemented."
            )
        # Future: call self.FINETUNED_ENDPOINT with prompt
        raise NotImplementedError("Fine-tuned model endpoint not yet connected.")


def get_llm_provider() -> BaseLLMProvider:
    """
    Factory — returns the appropriate provider based on environment config.
    Set USE_FINETUNED_LLM=1 to switch to FineTunedLLMProvider.
    """
    if os.environ.get("USE_FINETUNED_LLM") == "1":
        return FineTunedLLMProvider()
    return GeminiLLMProvider()


# Module-level singleton for convenience
_default_provider: BaseLLMProvider | None = None


def get_default_provider() -> BaseLLMProvider:
    global _default_provider
    if _default_provider is None:
        _default_provider = get_llm_provider()
    return _default_provider
