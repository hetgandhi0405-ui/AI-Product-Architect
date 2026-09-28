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


def _extract_json(text: str) -> Dict[str, Any]:
    """
    Extract a JSON object from Gemini output.
    """

    text = text.strip()

    # Remove markdown code fences if present.
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

    # Try extracting the first JSON object.
    match = re.search(
        r"\{.*\}",
        text,
        flags=re.DOTALL,
    )

    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return {}


def _normalize_alternatives(
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Normalize Gemini output into a predictable structure.
    """

    alternatives = result.get(
        "alternatives",
        [],
    )

    if not isinstance(alternatives, list):
        alternatives = []

    normalized = []

    for index, alternative in enumerate(
        alternatives[:3],
        start=1,
    ):
        if not isinstance(alternative, dict):
            continue

        name = str(
            alternative.get(
                "name",
                f"Architecture Option {index}",
            )
        ).strip()

        architecture_type = str(
            alternative.get(
                "architecture_type",
                "General",
            )
        ).strip()

        description = str(
            alternative.get(
                "description",
                "",
            )
        ).strip()

        components = alternative.get(
            "components",
            {},
        )

        if not isinstance(components, dict):
            components = {}

        strengths = alternative.get(
            "strengths",
            [],
        )

        if not isinstance(strengths, list):
            strengths = []

        strengths = [
            str(item).strip()
            for item in strengths
            if str(item).strip()
        ]

        tradeoffs = alternative.get(
            "tradeoffs",
            [],
        )

        if not isinstance(tradeoffs, list):
            tradeoffs = []

        tradeoffs = [
            str(item).strip()
            for item in tradeoffs
            if str(item).strip()
        ]

        normalized.append(
            {
                "id": f"architecture_{index}",
                "name": name,
                "architecture_type": architecture_type,
                "description": description,
                "components": components,
                "strengths": strengths,
                "tradeoffs": tradeoffs,
            }
        )

    return {
        "alternatives": normalized,
        "comparison_summary": str(
            result.get(
                "comparison_summary",
                "",
            )
        ).strip(),
    }


def architecture_alternatives_agent(
    state: AgentState,
) -> AgentState:
    """
    Generate multiple architecture alternatives for the
    current project requirements.
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

    product_plan = state.get(
        "product_plan",
        {},
    )

    existing_architecture = state.get(
        "architecture",
        {},
    )

    prompt = f"""
You are the Architecture Alternatives Agent in an
AI Product Architect system.

Generate exactly 3 realistic architecture alternatives
for the requested software product.

PROJECT:
{project_name}

REQUIREMENTS:
{requirements}

PRODUCT PLAN:
{json.dumps(product_plan, indent=2)}

EXISTING ARCHITECTURE:
{json.dumps(existing_architecture, indent=2)}

The alternatives should represent genuinely different
architecture strategies when appropriate.

Prefer options such as:
1. Serverless architecture
2. Containerized architecture
3. Traditional three-tier architecture

However, adapt the alternatives to the actual project.
Do not force an unsuitable architecture.

For every alternative provide:

- name
- architecture_type
- description
- components
- strengths
- tradeoffs

The components should describe:
- frontend
- backend
- database
- storage
- authentication
- networking
- compute
- monitoring
- security

Return ONLY valid JSON.

Required format:

{{
  "alternatives": [
    {{
      "name": "string",
      "architecture_type": "string",
      "description": "string",
      "components": {{
        "frontend": "string",
        "backend": "string",
        "database": "string",
        "storage": "string",
        "authentication": "string",
        "networking": "string",
        "compute": "string",
        "monitoring": "string",
        "security": "string"
      }},
      "strengths": [
        "string"
      ],
      "tradeoffs": [
        "string"
      ]
    }}
  ],
  "comparison_summary": "string"
}}

Do not include markdown.
Do not include explanations outside JSON.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    result = _extract_json(
        response.text
    )

    normalized = _normalize_alternatives(
        result
    )

    architecture = state.get(
        "architecture",
        {},
    )

    architecture[
        "architecture_alternatives"
    ] = normalized

    state["architecture"] = architecture

    return state