import os
import json
from google import genai

from backend.agents.state import AgentState


client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def architecture_agent(state: AgentState) -> AgentState:
    """
    Generate an AI-powered cloud architecture
    from the customer's requirements and AI suggestions.
    """

    requirements = state["requirements"]
    suggestions = state.get("suggestions", [])

    prompt = f"""
You are a senior AWS cloud architect.

Design a production-ready cloud architecture for this project.

Customer requirements:
{requirements}

AI recommendations:
{suggestions}

Return ONLY valid JSON using exactly these fields:

{{
  "frontend": "",
  "backend": "",
  "database": "",
  "storage": "",
  "authentication": "",
  "networking": "",
  "compute": "",
  "monitoring": "",
  "security": "",
  "scalability": ""
}}

Use appropriate AWS services where suitable.
Choose services based on the actual requirements.
Do not add unnecessary services.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    architecture_text = response.text.strip()

    # Remove markdown code fences if Gemini adds them
    if architecture_text.startswith("```"):
        architecture_text = architecture_text.replace("```json", "")
        architecture_text = architecture_text.replace("```", "")
        architecture_text = architecture_text.strip()

    try:
        architecture = json.loads(architecture_text)
    except json.JSONDecodeError:
        architecture = {
            "raw_response": architecture_text
        }

    state["architecture"] = architecture

    return state