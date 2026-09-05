import os

from google import genai

from backend.agents.state import AgentState


client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


def suggestion_agent(state: AgentState) -> AgentState:
    """
    Generate AI-powered technical suggestions
    from the customer requirements and previous
    requirement analysis.
    """

    requirements = state["requirements"]
    previous_analysis = state.get("suggestions", [])

    prompt = f"""
You are a senior cloud solution architect.

Analyze the customer requirement and the previous
AI requirement analysis.

CUSTOMER REQUIREMENT:
{requirements}

PREVIOUS AI ANALYSIS:
{previous_analysis}

Generate practical technical recommendations for
building this application.

Cover:

1. Application architecture
2. Cloud services
3. Database
4. Storage
5. Authentication
6. Networking
7. Compute
8. Monitoring
9. Security
10. Scalability

For an e-commerce application, consider suitable
AWS services such as S3, CloudFront, API Gateway,
Lambda, ECS/Fargate, Aurora, DynamoDB, ElastiCache,
Cognito, VPC, CloudWatch, WAF, KMS, EventBridge
and SQS.

Choose services according to the actual requirements.
Do not simply list every AWS service.

Return a clear, structured technical recommendation.
Do not return JSON.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    suggestions = response.text.strip()

    # Replace old rule-based suggestions with the
    # actual AI-generated recommendation.
    state["suggestions"] = [
        f"AI Requirement Analysis: {previous_analysis[0]}"
        if previous_analysis
        else "AI Requirement Analysis: Not available",
        f"AI Architecture Suggestions: {suggestions}"
    ]

    return state