import os
import json
import time

from google import genai

from backend.agents.state import AgentState


client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


def architecture_agent(state: AgentState) -> AgentState:
    """
    Generate an AI-powered AWS cloud architecture
    with automatic retry handling for temporary API errors.
    """

    requirements = state["requirements"]
    suggestions = state.get("suggestions", [])

    prompt = f"""
You are a senior AWS cloud architect.

Design a production-ready AWS cloud architecture
for the following application.

CUSTOMER REQUIREMENTS:
{requirements}

AI RECOMMENDATIONS:
{suggestions}

Return ONLY valid JSON.

Use exactly these fields:

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

Choose AWS services based on the actual requirements.

For an e-commerce application, consider services such as:
Amazon S3, CloudFront, API Gateway, ECS/Fargate,
Lambda, Aurora PostgreSQL, DynamoDB, ElastiCache,
Cognito, VPC, CloudWatch, WAF, KMS, Secrets Manager,
EventBridge and SQS.

Do not use generic values such as:
"Web Application"
"API Server"
"Managed Database"
"Cloud Object Storage"

Return only the JSON object.
"""

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            architecture_text = response.text.strip()

            # Remove Markdown code fences if Gemini returns them
            if architecture_text.startswith("```"):
                architecture_text = architecture_text.replace(
                    "```json", ""
                )
                architecture_text = architecture_text.replace(
                    "```", ""
                )
                architecture_text = architecture_text.strip()

            architecture = json.loads(architecture_text)

            state["architecture"] = architecture

            return state

        except Exception as error:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(
                    f"Gemini request failed. "
                    f"Retrying in {wait_time} seconds..."
                )
                time.sleep(wait_time)
            else:
                raise error

    return state