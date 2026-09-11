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


def environment_config_agent(state: AgentState) -> AgentState:
    requirements = state.get("requirements", "")
    product_plan = state.get("product_plan", {})
    api_specification = state.get("api_specification", {})
    database_specification = state.get(
        "database_specification",
        {}
    )
    architecture = state.get("architecture", {})
    dependency_specification = state.get(
        "dependency_specification",
        {}
    )

    prompt = f"""
You are an Environment Configuration Architect.

Analyze the generated product specifications and identify
the environment variables and configuration values required
to run and deploy the generated application.

PROJECT REQUIREMENTS:
{requirements}

PRODUCT PLAN:
{json.dumps(product_plan, indent=2)}

API SPECIFICATION:
{json.dumps(api_specification, indent=2)}

DATABASE SPECIFICATION:
{json.dumps(database_specification, indent=2)}

ARCHITECTURE:
{json.dumps(architecture, indent=2)}

DEPENDENCY SPECIFICATION:
{json.dumps(dependency_specification, indent=2)}

Your task is ONLY to create an environment configuration
specification.

Do NOT generate application code.
Do NOT generate real secrets.
Do NOT expose API keys, passwords, tokens, or credentials.
Do NOT generate Terraform.
Do NOT install packages.

Return ONLY valid JSON using this structure:

{{
  "environment_variables": [
    {{
      "name": "",
      "description": "",
      "required": true,
      "secret": false,
      "example": ""
    }}
  ],
  "environment_files": {{
    "development": ".env",
    "example": ".env.example",
    "production": "environment configuration supplied securely"
  }},
  "secret_management": {{
    "required": true,
    "recommendation": ""
  }},
  "configuration_notes": [],
  "summary": ""
}}

Rules:

1. Include only environment variables actually relevant
   to the generated product.
2. Never provide real credentials or secrets.
3. Secret variables must use safe placeholder examples.
4. Non-secret variables may use realistic example values.
5. Database configuration should match the database
   specification.
6. Authentication configuration should match the
   authentication architecture.
7. Cloud configuration should match the selected
   infrastructure when applicable.
8. AI configuration should include an API key variable
   only if AI functionality requires it.
9. Clearly mark secret values with "secret": true.
10. Avoid duplicate variables.
11. Do not invent unnecessary configuration.
12. Return JSON only.
"""

    last_error = None

    for attempt in range(3):
        try:
            client = _get_client()

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            environment_specification = _extract_json(
                response.text
            )

            state["architecture"][
                "environment_configuration"
            ] = environment_specification

            return state

        except Exception as exc:
            last_error = exc

            if attempt < 2:
                time.sleep(1)

    raise RuntimeError(
        "Environment Configuration Agent failed after "
        f"3 attempts: {last_error}"
    )