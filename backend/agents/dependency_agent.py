import json
import os
import time

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


def _extract_json(text: str):
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


def dependency_agent(state: AgentState) -> AgentState:
    requirements = state.get("requirements", "")
    product_plan = state.get("product_plan", {})
    ui_specification = state.get("ui_specification", {})
    api_specification = state.get("api_specification", {})
    database_specification = state.get(
        "database_specification",
        {}
    )
    architecture = state.get("architecture", {})

    prompt = f"""
You are a Software Dependency Architect.

Analyze the following generated product specifications and
produce a structured dependency specification.

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

Your task is ONLY to identify the software dependencies
required to implement the product.

Do NOT generate application code.
Do NOT generate SQL.
Do NOT generate Terraform.
Do NOT install packages.

Return ONLY valid JSON with this structure:

{{
  "frontend": {{
    "framework": "",
    "dependencies": []
  }},
  "backend": {{
    "framework": "",
    "dependencies": []
  }},
  "database": {{
    "type": "",
    "dependencies": []
  }},
  "testing": {{
    "dependencies": []
  }},
  "development": {{
    "dependencies": []
  }},
  "runtime": {{
    "dependencies": []
  }},
  "summary": ""
}}

Rules:

1. Dependencies must be relevant to the generated product.
2. Avoid unnecessary packages.
3. Use well-known package names.
4. Keep frontend dependencies separate from backend dependencies.
5. Database dependencies must match the selected database.
6. Testing dependencies must support the generated API,
   frontend, or database testing requirements.
7. Development dependencies may include linters, formatters,
   type checkers, or development utilities when appropriate.
8. Runtime dependencies should contain packages required
   when the application runs.
9. Do not invent custom packages.
10. Return JSON only.
"""

    last_error = None

    for attempt in range(3):
        try:
            client = _get_client()

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            dependency_specification = _extract_json(
                response.text
            )

            state["architecture"][
                "dependency_specification"
            ] = dependency_specification

            return state

        except Exception as exc:
            last_error = exc

            if attempt < 2:
                time.sleep(1)

    raise RuntimeError(
        f"Dependency Agent failed after 3 attempts: {last_error}"
    )