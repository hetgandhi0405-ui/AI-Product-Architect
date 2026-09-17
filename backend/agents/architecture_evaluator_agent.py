import json
import os
import re
from typing import Any, Dict

from google import genai

from backend.agents.state import AgentState


MODEL_NAME = "gemini-3.5-flash-lite"


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set."
        )

    return genai.Client(api_key=api_key)


def _extract_json(text: str) -> Any:
    """Extract JSON from Gemini output."""

    if not text:
        return {}

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    start = text.find("[")
    end = text.rfind("]")

    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    return {}


def _normalize_score(value: Any) -> float:
    """Convert a score into a value between 0 and 10."""

    if isinstance(value, dict):
        value = (
            value.get("score")
            or value.get("value")
            or value.get("rating")
        )

    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0

    return round(
        max(0.0, min(10.0, score)),
        2,
    )


def _normalize_list(value: Any) -> list:
    """Normalize a value into a list of strings."""

    if value is None:
        return []

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    return [str(value).strip()]


def _find_evaluation(
    evaluations: list,
    architecture_id: str,
    architecture_name: str,
    index: int,
) -> Dict[str, Any]:
    """Find the matching evaluation."""

    # Match by architecture ID.
    for evaluation in evaluations:
        if not isinstance(evaluation, dict):
            continue

        evaluation_id = str(
            evaluation.get(
                "architecture_id",
                evaluation.get("id", ""),
            )
        )

        if evaluation_id == architecture_id:
            return evaluation

    # Match by architecture name.
    for evaluation in evaluations:
        if not isinstance(evaluation, dict):
            continue

        evaluation_name = str(
            evaluation.get(
                "architecture_name",
                evaluation.get("name", ""),
            )
        ).strip()

        if evaluation_name == architecture_name:
            return evaluation

    # Positional fallback.
    if index < len(evaluations):
        evaluation = evaluations[index]

        if isinstance(evaluation, dict):
            return evaluation

    return {}


def _normalize_evaluation(
    result: Any,
    alternatives: list,
) -> Dict[str, Any]:
    """Normalize different valid Gemini response structures."""

    evaluations = []
    summary = ""

    if isinstance(result, dict):

        evaluations = result.get(
            "evaluations",
            [],
        )

        if not evaluations:
            evaluations = result.get(
                "alternatives",
                [],
            )

        if not evaluations:
            evaluations = result.get(
                "results",
                [],
            )

        summary = str(
            result.get(
                "evaluation_summary",
                result.get(
                    "comparison_summary",
                    result.get(
                        "summary",
                        "",
                    ),
                ),
            )
        ).strip()

    elif isinstance(result, list):
        evaluations = result

    if not isinstance(evaluations, list):
        evaluations = []

    normalized = []

    for index, alternative in enumerate(alternatives):

        if not isinstance(alternative, dict):
            continue

        architecture_id = str(
            alternative.get(
                "id",
                f"architecture_{index + 1}",
            )
        )

        architecture_name = str(
            alternative.get(
                "name",
                f"Architecture Option {index + 1}",
            )
        )

        evaluation = _find_evaluation(
            evaluations,
            architecture_id,
            architecture_name,
            index,
        )

        # Support nested evaluation objects.
        if "evaluation" in evaluation:

            nested = evaluation.get(
                "evaluation"
            )

            if isinstance(nested, dict):
                evaluation = {
                    **evaluation,
                    **nested,
                }

        scores = evaluation.get(
            "scores",
            {},
        )

        if not isinstance(scores, dict):
            scores = {}

        # Support "criteria" as an alternative format.
        if not scores:

            criteria = evaluation.get(
                "criteria",
                {},
            )

            if isinstance(criteria, dict):
                scores = criteria

        normalized_scores = {
            "scalability": _normalize_score(
                scores.get(
                    "scalability",
                    evaluation.get(
                        "scalability",
                        0,
                    ),
                )
            ),
            "security": _normalize_score(
                scores.get(
                    "security",
                    evaluation.get(
                        "security",
                        0,
                    ),
                )
            ),
            "maintainability": _normalize_score(
                scores.get(
                    "maintainability",
                    evaluation.get(
                        "maintainability",
                        0,
                    ),
                )
            ),
            "performance": _normalize_score(
                scores.get(
                    "performance",
                    evaluation.get(
                        "performance",
                        0,
                    ),
                )
            ),
            "complexity": _normalize_score(
                scores.get(
                    "complexity",
                    evaluation.get(
                        "complexity",
                        0,
                    ),
                )
            ),
            "cost_efficiency": _normalize_score(
                scores.get(
                    "cost_efficiency",
                    evaluation.get(
                        "cost_efficiency",
                        0,
                    ),
                )
            ),
        }

        strengths = _normalize_list(
            evaluation.get(
                "strengths",
                alternative.get(
                    "strengths",
                    [],
                ),
            )
        )

        weaknesses = _normalize_list(
            evaluation.get(
                "weaknesses",
                alternative.get(
                    "tradeoffs",
                    [],
                ),
            )
        )

        reasoning = str(
            evaluation.get(
                "reasoning",
                evaluation.get(
                    "analysis",
                    "",
                ),
            )
        ).strip()

        normalized.append(
            {
                "architecture_id": architecture_id,
                "architecture_name": architecture_name,
                "scores": normalized_scores,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "reasoning": reasoning,
            }
        )

    return {
        "evaluations": normalized,
        "evaluation_summary": summary,
    }


def architecture_evaluator_agent(
    state: AgentState,
) -> AgentState:
    """
    Evaluate all architecture alternatives.

    Criteria:
    - scalability
    - security
    - maintainability
    - performance
    - complexity
    - cost_efficiency
    """

    client = _get_client()

    project_name = state.get(
        "project_name",
        "",
    )

    requirements = state.get(
        "requirements",
        "",
    )

    architecture = state.get(
        "architecture",
        {},
    )

    alternatives_data = architecture.get(
        "architecture_alternatives",
        {},
    )

    if not isinstance(
        alternatives_data,
        dict,
    ):
        alternatives_data = {}

    alternatives = alternatives_data.get(
        "alternatives",
        [],
    )

    if not isinstance(
        alternatives,
        list,
    ):
        alternatives = []

    if not alternatives:

        architecture[
            "architecture_evaluation"
        ] = {
            "evaluations": [],
            "evaluation_summary": (
                "No architecture alternatives "
                "were available for evaluation."
            ),
        }

        state["architecture"] = architecture

        return state

    prompt = f"""
You are the Architecture Evaluator Agent
in an AI Product Architect system.

PROJECT:
{project_name}

REQUIREMENTS:
{requirements}

ARCHITECTURE ALTERNATIVES:
{json.dumps(alternatives, indent=2)}

Evaluate EVERY architecture alternative.

Use exactly these six criteria:

1. scalability
2. security
3. maintainability
4. performance
5. complexity
6. cost_efficiency

Give every criterion a numeric score from 0 to 10.

SCORING RULES:

scalability:
Higher means better ability to handle increasing
traffic and workload.

security:
Higher means stronger security controls and
data protection.

maintainability:
Higher means easier to maintain, modify and extend.

performance:
Higher means better expected runtime performance.

complexity:
Higher means simpler to understand, operate,
debug and maintain.

cost_efficiency:
Higher means better infrastructure and operational
cost efficiency.

IMPORTANT:

- Evaluate ALL provided architectures.
- Use the exact architecture IDs from the input.
- Do not invent architectures.
- Do not remove architectures.
- Do not select a winner.
- Do not calculate an overall winner.
- Explain engineering trade-offs.
- Return exactly one evaluation for every architecture.
- Scores must be numeric values from 0 to 10.

Return ONLY valid JSON.

Required structure:

{{
  "evaluations": [
    {{
      "architecture_id": "architecture_1",
      "architecture_name": "Architecture Name",
      "scores": {{
        "scalability": 8,
        "security": 8,
        "maintainability": 8,
        "performance": 8,
        "complexity": 8,
        "cost_efficiency": 8
      }},
      "strengths": [
        "strength"
      ],
      "weaknesses": [
        "weakness"
      ],
      "reasoning": "Engineering reasoning."
    }}
  ],
  "evaluation_summary": "Summary of engineering trade-offs."
}}

Do not include Markdown.
Do not include explanations outside JSON.
"""

    response = client.models.generate_content(
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

    normalized = _normalize_evaluation(
        result,
        alternatives,
    )

    architecture[
        "architecture_evaluation"
    ] = normalized

    state["architecture"] = architecture

    return state