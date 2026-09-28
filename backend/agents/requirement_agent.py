from backend.core.model_router import get_fast_model
import os

from google import genai

from backend.agents.state import AgentState
from backend.core.llm_cache import cached_generate_content


def requirement_agent(state: AgentState) -> AgentState:
    """Analyze the customer prompt using Gemini."""
    requirements = state["requirements"]
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    client = genai.Client(api_key=api_key)

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

Do not simply repeat the customer requirement.
Do not use phrases such as:
"Requirement received"
"Analyze required application components"
"Identify cloud services needed"

Instead, provide an actual technical analysis of what the application needs.
Return only the technical analysis in clear, structured text.
"""

    response = cached_generate_content(
        client,
        "requirement",
        model=get_fast_model(),
        contents=prompt,
    )
    analysis = (response.text or "").strip()
    if not analysis:
        raise RuntimeError("Gemini returned an empty requirement analysis.")

    state["suggestions"] = [f"AI Requirement Analysis:\n{analysis}"]
    return state
