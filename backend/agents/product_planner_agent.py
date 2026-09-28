import os
import json
import time

from google import genai
from backend.agents.state import AgentState


client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


def product_planner_agent(state: AgentState) -> AgentState:
    """
    Convert customer requirements into a structured
    product plan.
    """

    requirements = state["requirements"]

    prompt = f"""
You are a senior product manager and software architect.

Analyze the following customer requirement:

{requirements}

Create a practical product plan.

Identify:

1. Product name
2. User roles
3. Main features
4. User stories
5. Required application pages
6. Important product scope

Rules:

- Understand the customer's actual requirement.
- Do not add unrelated features.
- Keep the plan realistic and implementable.
- Features must be clear and specific.
- User stories must describe what users can do.
- Pages must match the required features.
- Do not include cloud architecture.
- Do not include Terraform.
- Return ONLY valid JSON.

Use exactly this format:

{{
    "product_name": "...",
    "user_roles": [],
    "features": [],
    "user_stories": [],
    "pages": [],
    "scope": []
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

            product_text = response.text.strip()

            if product_text.startswith("```"):
                product_text = product_text.replace(
                    "```json", ""
                )
                product_text = product_text.replace(
                    "```", ""
                )
                product_text = product_text.strip()

            product_plan = json.loads(product_text)

            state["product_plan"] = product_plan

            return state

        except Exception as error:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt

                print(
                    f"Product Planner request failed. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)
            else:
                raise error

    return state
