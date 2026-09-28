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
    Generate an AWS cloud architecture using Gemini.
    """

    requirements = state["requirements"]
    suggestions = state.get("suggestions", [])

    prompt = f"""
You are a senior AWS cloud solution architect.

Design a production-ready AWS cloud architecture
for the following customer application.

CUSTOMER REQUIREMENTS:
{requirements}

AI TECHNICAL ANALYSIS AND SUGGESTIONS:
{suggestions}

Design the architecture using AWS services that
actually fit the requirements.

Consider services such as:

- Amazon S3
- Amazon CloudFront
- Amazon API Gateway
- AWS Lambda
- Amazon ECS / Fargate
- Amazon Aurora
- Amazon DynamoDB
- Amazon ElastiCache
- Amazon Cognito
- Amazon VPC
- Amazon CloudWatch
- AWS X-Ray
- AWS WAF
- AWS KMS
- AWS Secrets Manager
- Amazon SQS
- Amazon EventBridge

Do NOT use every service automatically.
Choose only appropriate services.

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{{
  "frontend": "...",
  "backend": "...",
  "database": "...",
  "storage": "...",
  "authentication": "...",
  "networking": "...",
  "compute": "...",
  "monitoring": "...",
  "security": "...",
  "scalability": "..."
}}

Do not include Markdown.
Do not include explanations outside the JSON.
"""

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            architecture_text = response.text.strip()

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