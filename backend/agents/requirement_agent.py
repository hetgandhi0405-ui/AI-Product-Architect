import os

from google import genai

from backend.agents.state import AgentState


client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


def requirement_agent(state: AgentState) -> AgentState:
    """
    Analyze customer requirements using Gemini.
    """

    requirements = state["requirements"]

    prompt = f"""
You are a senior software and cloud solution architect.

Analyze the following customer requirement:

{requirements}

Provide a structured technical requirement analysis.

Cover:

1. Main functional requirements
2. Application components
3. User and traffic requirements
4. Data requirements
5. Security requirements
6. Availability requirements
7. Scalability requirements
8. Important technical considerations

Do not repeat the customer requirement as the answer.
Do not use phrases such as:
"Requirement received"
"Analyze required application components"
"Identify cloud services needed"

Instead, provide an actual technical analysis
of what the application needs.

Return only the technical analysis in clear,
structured text.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    analysis = response.text.strip()

    state["suggestions"] = [
        f"AI Requirement Analysis:\n{analysis}"
    ]

    return state