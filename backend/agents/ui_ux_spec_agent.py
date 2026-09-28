import os
import json
import time

from google import genai
from backend.agents.state import AgentState


client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


def ui_ux_spec_agent(state: AgentState) -> AgentState:
    """
    Generate a structured UI/UX specification from
    the product plan and customer requirements.
    """

    requirements = state["requirements"]
    product_plan = state.get("product_plan", {})

    prompt = f"""
You are a senior UI/UX product designer.

Design the UI/UX specification for the following application.

CUSTOMER REQUIREMENTS:
{requirements}

PRODUCT PLAN:
{product_plan}

Create a practical UI/UX specification.

Include:

1. Required pages
2. Navigation structure
3. Important UI components
4. Forms and inputs
5. Main user flows
6. Responsive requirements

Rules:

- Use the product requirements and product plan.
- Do not add unrelated pages or features.
- Pages must support the actual product features.
- Keep the design practical for a real web application.
- This is a specification only.
- Do not generate HTML, CSS, React or JavaScript code.
- Do not generate cloud architecture.
- Return ONLY valid JSON.

Use exactly this format:

{{
    "pages": [],
    "navigation": [],
    "components": [],
    "forms": [],
    "user_flows": [],
    "responsive_requirements": []
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

            ui_text = response.text.strip()

            if ui_text.startswith("```"):
                ui_text = ui_text.replace(
                    "```json", ""
                )
                ui_text = ui_text.replace(
                    "```", ""
                )
                ui_text = ui_text.strip()

            ui_specification = json.loads(ui_text)

            state["ui_specification"] = ui_specification

            return state

        except Exception as error:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt

                print(
                    f"UI/UX specification request failed. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)
            else:
                raise error

    return state
