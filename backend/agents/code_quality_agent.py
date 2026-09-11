import os
import json
import time

from google import genai
from backend.agents.state import AgentState


client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


def code_quality_agent(state: AgentState) -> AgentState:
    """
    Review the generated product specifications for consistency,
    completeness, security, and implementation readiness.
    """

    requirements = state.get("requirements", "")
    product_plan = state.get("product_plan", {})
    ui_specification = state.get("ui_specification", {})
    api_specification = state.get("api_specification", {})
    database_specification = state.get("database_specification", {})
    architecture = state.get("architecture", {})
    integration = architecture.get("integration", {})

    prompt = f"""
You are a senior software architect and code quality reviewer.

Review the following AI-generated product specifications.

CUSTOMER REQUIREMENTS:
{requirements}

PRODUCT PLAN:
{product_plan}

UI/UX SPECIFICATION:
{ui_specification}

API SPECIFICATION:
{api_specification}

DATABASE SPECIFICATION:
{database_specification}

ARCHITECTURE:
{architecture}

INTEGRATION REPORT:
{integration}

Perform a practical quality review.

Check:

1. Feature consistency
   - Product features should be supported by UI pages and user flows.

2. API consistency
   - APIs should support the required product features.
   - HTTP methods and endpoints should be reasonable.

3. Database consistency
   - Required application data should have appropriate database tables.
   - API operations should have corresponding data models where needed.

4. Architecture consistency
   - Architecture should support the product requirements.
   - Required infrastructure components should exist.

5. Security
   - Identify obvious missing authentication, authorization, data protection,
     or other important security considerations.

6. Completeness
   - Identify important missing components that could prevent implementation.

7. Integration
   - Consider the existing integration report.

Rules:
- Do not generate application code.
- Do not generate SQL.
- Do not generate Terraform.
- Do not redesign the entire architecture.
- Report only meaningful issues.
- Distinguish critical issues from warnings.
- If the system is consistent, return an empty issues list.
- Return ONLY valid JSON.
- Do not use Markdown.
- Do not use code fences.

Use exactly this structure:

{{
    "status": "PASS",
    "score": 90,
    "issues": [],
    "warnings": [],
    "security_review": {{
        "status": "PASS",
        "issues": []
    }},
    "consistency_checks": {{
        "feature_ui": "PASS",
        "feature_api": "PASS",
        "api_database": "PASS",
        "architecture": "PASS",
        "integration": "PASS"
    }},
    "summary": "..."
}}

Status must be either:
- PASS
- NEEDS_REVIEW
- FAIL

Score must be an integer from 0 to 100.
"""

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            quality_text = response.text.strip()

            if quality_text.startswith("```"):
                quality_text = quality_text.replace("```json", "")
                quality_text = quality_text.replace("```", "")
                quality_text = quality_text.strip()

            quality_report = json.loads(quality_text)

            state["architecture"]["code_quality"] = quality_report

            return state

        except Exception as error:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(
                    f"Code quality request failed. "
                    f"Retrying in {wait_time} seconds..."
                )
                time.sleep(wait_time)
            else:
                raise error

    return state