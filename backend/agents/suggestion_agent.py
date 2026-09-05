import os
from google import genai

from backend.agents.state import AgentState


client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def suggestion_agent(state: AgentState) -> AgentState:
    """
    Generate AI-powered technical suggestions
    based on the requirement analysis.
    """

    requirements = state["requirements"]
    previous_analysis = state.get("suggestions", [])

    prompt = f"""
You are a senior cloud solution architect.

Customer requirement:
{requirements}

Requirement analysis from the previous AI agent:
{previous_analysis}

Based on this information, recommend the most appropriate:

1. Application components
2. Cloud services
3. Database technology
4. Storage solution
5. Authentication approach
6. Monitoring and logging
7. Security measures
8. Scalability approach

Keep the recommendations practical and suitable
for a production-ready application.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    suggestions = response.text

    state["suggestions"].append(
        f"AI Architecture Suggestions: {suggestions}"
    )

    return state