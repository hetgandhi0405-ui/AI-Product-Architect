from backend.core.model_router import get_strong_model
import json
import os
import time
from typing import Any, Dict

from google import genai

from backend.agents.state import AgentState
from backend.core.llm_cache import cached_generate_content
from backend.core.prompt_utils import compact_json


MODEL_NAME = get_strong_model()


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set."
        )

    return genai.Client(api_key=api_key)


def _extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

        if text.lower().startswith("json"):
            text = text[4:].strip()

    return json.loads(text)


def _normalize_result(
    result: Dict[str, Any],
) -> Dict[str, Any]:

    recommendation = result.get(
        "recommendation",
        {},
    )

    if not isinstance(recommendation, dict):
        recommendation = {}

    return {
        "status": result.get(
            "status",
            "SUCCESS",
        ),
        "recommended_architecture_id": recommendation.get(
            "architecture_id",
            "",
        ),
        "recommended_architecture_name": recommendation.get(
            "architecture_name",
            "",
        ),
        "reasoning": recommendation.get(
            "reasoning",
            "",
        ),
        "strengths": recommendation.get(
            "strengths",
            [],
        ),
        "risks": recommendation.get(
            "risks",
            [],
        ),
        "tradeoffs": recommendation.get(
            "tradeoffs",
            [],
        ),
        "requirement_coverage": result.get(
            "requirement_coverage",
            {},
        ),
        "security_summary": result.get(
            "security_summary",
            {},
        ),
        "cost_summary": result.get(
            "cost_summary",
            {},
        ),
        "evaluation_summary": result.get(
            "evaluation_summary",
            "",
        ),
        "confidence": result.get(
            "confidence",
            0,
        ),
    }


def architecture_recommendation_agent(
    state: AgentState,
) -> AgentState:

    requirements = state.get(
        "requirements",
        "",
    )

    architecture = state.get(
        "architecture",
        {},
    )

    if not isinstance(architecture, dict):
        architecture = {}

    alternatives = architecture.get(
        "architecture_alternatives",
        {},
    )

    evaluation = architecture.get(
        "architecture_evaluation",
        {},
    )

    security = architecture.get(
        "security_analysis",
        {},
    )

    cost = architecture.get(
        "cost_analysis",
        {},
    )

    traceability = architecture.get(
        "requirement_traceability",
        {},
    )

    prompt = f"""
You are the Architecture Recommendation Agent
inside an AI Product Architect system.

Your task is to synthesize existing engineering
analysis and produce a transparent architecture
recommendation.

PROJECT REQUIREMENTS:
{requirements}

ARCHITECTURE ALTERNATIVES:
{compact_json(alternatives)}

ARCHITECTURE EVALUATION:
{compact_json(evaluation)}

SECURITY ANALYSIS:
{compact_json(security)}

COST ANALYSIS:
{compact_json(cost)}

REQUIREMENT TRACEABILITY:
{compact_json(traceability)}

IMPORTANT RULES:

1. Use ONLY the supplied architecture alternatives.
2. Do not invent an architecture.
3. Do not modify architecture alternatives.
4. Preserve the exact architecture ID when referring
   to an alternative.
5. Consider scalability, security, maintainability,
   performance, complexity and cost efficiency.
6. Consider the security analysis.
7. Consider the INR cost analysis.
8. Consider requirement coverage.
9. Explain engineering trade-offs.
10. Do not claim that the recommendation is objectively
    perfect.
11. Do not claim legal or regulatory compliance.
12. Return ONLY valid JSON.
13. Confidence must be between 0 and 100.
14. Cost values must remain in INR.
15. If required information is missing, explicitly
    mention it in the reasoning.

Return exactly this structure:

{{
  "status": "SUCCESS",
  "recommendation": {{
    "architecture_id": "architecture_1",
    "architecture_name": "Architecture Name",
    "reasoning": "Engineering reasoning.",
    "strengths": [
      "strength"
    ],
    "risks": [
      "risk"
    ],
    "tradeoffs": [
      "tradeoff"
    ]
  }},
  "requirement_coverage": {{
    "coverage_percent": 0,
    "status": "UNKNOWN"
  }},
  "security_summary": {{
    "security_score": 0,
    "risk_level": "UNKNOWN"
  }},
  "cost_summary": {{
    "estimated_monthly_cost_inr": 0,
    "currency": "INR"
  }},
  "evaluation_summary": "Engineering trade-off summary.",
  "confidence": 0
}}
"""

    client = _get_client()

    last_error = None

    for attempt in range(3):

        try:

            response = cached_generate_content(
                client,
                "architecture_recommendation",
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "temperature": 0.2,
                },
            )

            result = _extract_json(
                response.text
            )

            normalized = _normalize_result(
                result
            )

            architecture[
                "architecture_recommendation"
            ] = normalized

            state[
                "architecture"
            ] = architecture

            state[
                "architecture_recommendation"
            ] = normalized

            return state

        except Exception as exc:

            last_error = exc

            if attempt < 2:
                time.sleep(1)

    raise RuntimeError(
        "Architecture Recommendation Agent failed "
        f"after 3 attempts: {last_error}"
    )
