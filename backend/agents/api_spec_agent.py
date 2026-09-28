import os
import json
import time

from google import genai
from backend.agents.state import AgentState


client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


def api_spec_agent(state: AgentState) -> AgentState:
    """
    Generate a structured backend/API specification
    from the product plan and requirements.
    """

    requirements = state["requirements"]
    product_plan = state.get("product_plan", {})

    prompt = f"""
You are a senior backend architect and API designer.

Design the backend API specification for this application.

CUSTOMER REQUIREMENTS:
{requirements}

PRODUCT PLAN:
{product_plan}

Create a practical REST API specification.

For every API endpoint include:

1. HTTP method
2. Endpoint
3. Purpose
4. Authentication requirement
5. Request data
6. Response data

Rules:

- APIs must directly support the product requirements.
- Do not create unrelated APIs.
- Use REST API conventions.
- Use appropriate HTTP methods such as GET, POST, PUT, PATCH, and DELETE.
- Authentication should be required for protected user operations.
- Do not generate actual backend code.
- Do not generate database SQL.
- Do not generate cloud architecture.
- Return ONLY valid JSON.

Use exactly this structure:

{{
    "api_style": "REST",
    "base_path": "/api",
    "endpoints": [
        {{
            "method": "GET",
            "endpoint": "/example",
            "purpose": "...",
            "authentication": true,
            "request": {{}},
            "response": {{}}
        }}
    ]
}}

Do not use Markdown.
Do not use code fences.
"""

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            api_text = response.text.strip()

            if api_text.startswith("```"):
                api_text = api_text.replace(
                    "```json", ""
                )
                api_text = api_text.replace(
                    "```", ""
                )
                api_text = api_text.strip()

            api_specification = json.loads(api_text)

            state["api_specification"] = api_specification

            return state

        except Exception as error:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt

                print(
                    f"API specification request failed. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)
            else:
                raise error

    return state
