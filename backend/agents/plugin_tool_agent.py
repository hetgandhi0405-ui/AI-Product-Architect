from typing import Any, Dict
import json
import os

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
    Extract a JSON object from the model response.
    """

    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

        if text.startswith("json"):
            text = text[4:].strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "No JSON object found in model response."
        )

    return json.loads(
        text[start:end + 1]
    )


def plugin_tool_agent(
    state: AgentState
) -> AgentState:
    """
    Analyze the generated product specifications and
    recommend useful external tools, services, and
    integrations.

    This agent only produces recommendations.
    It does not install packages, connect services,
    create credentials, or execute external tools.
    """

    requirements = state.get(
        "requirements",
        ""
    )

    product_plan = state.get(
        "product_plan",
        {}
    )

    ui_specification = state.get(
        "ui_specification",
        {}
    )

    api_specification = state.get(
        "api_specification",
        {}
    )

    database_specification = state.get(
        "database_specification",
        {}
    )

    architecture = state.get(
        "architecture",
        {}
    )

    prompt = f"""
You are the Plugin and Tool Selection Agent
inside an autonomous AI software architecture platform.

Your job is to analyze the generated software
specifications and recommend useful external tools,
services, APIs, integrations, or developer tools.

PROJECT REQUIREMENTS:
{requirements}

PRODUCT PLAN:
{json.dumps(product_plan, indent=2)}

UI/UX SPECIFICATION:
{json.dumps(ui_specification, indent=2)}

API SPECIFICATION:
{json.dumps(api_specification, indent=2)}

DATABASE SPECIFICATION:
{json.dumps(database_specification, indent=2)}

ARCHITECTURE:
{json.dumps(architecture, indent=2)}

Return ONLY valid JSON.

Use exactly this structure:

{{
  "tools": [
    {{
      "name": "",
      "category": "",
      "purpose": "",
      "reason": "",
      "required": false,
      "integration_point": "",
      "alternatives": []
    }}
  ],
  "categories": [],
  "selection_summary": "",
  "security_notes": [],
  "implementation_notes": []
}}

Rules:

1. Recommend tools only when they are useful for the
   actual project requirements.

2. Consider categories such as:
   payment,
   authentication,
   storage,
   email,
   messaging,
   analytics,
   monitoring,
   search,
   maps,
   AI,
   deployment,
   observability,
   testing,
   security.

3. Do not recommend every possible service.

4. Prefer practical and commonly used tools.

5. Consider services already present in the architecture.
   Do not blindly duplicate them.

6. For each tool explain why it is useful.

7. "required" must be true only when the product
   genuinely depends on the tool.

8. Include alternatives where meaningful.

9. Mention security considerations when an integration
   handles credentials, payments, personal data, or
   sensitive information.

10. Do not generate application code.

11. Do not generate Terraform.

12. Do not install packages.

13. Do not create API keys or credentials.

14. Do not execute external tools.

15. This is a planning and recommendation agent only.
"""

    client = _get_client()

    last_error = None

    for _ in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            result = _extract_json(
                response.text
            )

            if "tools" not in result:
                raise ValueError(
                    "Plugin tool response is missing 'tools'."
                )

            result.setdefault(
                "categories",
                []
            )

            result.setdefault(
                "selection_summary",
                ""
            )

            result.setdefault(
                "security_notes",
                []
            )

            result.setdefault(
                "implementation_notes",
                []
            )

            architecture = state.get(
                "architecture",
                {}
            )

            architecture[
                "plugin_tool_specification"
            ] = result

            state["architecture"] = architecture

            return state

        except Exception as error:
            last_error = error

    raise RuntimeError(
        "Plugin / Tool Agent failed after 3 attempts: "
        f"{last_error}"
    )