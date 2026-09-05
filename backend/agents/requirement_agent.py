import os
from google import genai

from backend.agents.state import AgentState


client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def requirement_agent(state: AgentState) -> AgentState:
    requirements = state["requirements"]

    prompt = f"""
You are a senior cloud solution architect.

Analyze the following customer requirement:

{requirements}

Identify:
1. Main application requirements
2. Important components
3. Scalability requirements
4. Security requirements
5. Availability requirements
6. Important technical considerations

Give a concise technical analysis that can be used by another
AI agent to design a cloud architecture.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    analysis = response.text

    state["suggestions"] = [
        f"AI Requirement Analysis: {analysis}"
    ]

    return state