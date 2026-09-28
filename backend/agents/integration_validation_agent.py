import os
import json
import time

from google import genai
from backend.agents.state import AgentState


client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


def integration_validation_agent(state: AgentState) -> AgentState:
    """
    Perform final cross-agent integration validation.

    This agent checks whether the outputs produced by the
    different specification agents are consistent with each other.
    """

    requirements = state.get("requirements", "")
    product_plan = state.get("product_plan", {})
    ui_specification = state.get("ui_specification", {})
    api_specification = state.get("api_specification", {})
    database_specification = state.get("database_specification", {})
    architecture = state.get("architecture", {})

    infrastructure = architecture.get("infrastructure", {})
    terraform = architecture.get("terraform", {})
    code_quality = architecture.get("code_quality", {})
    test_specification = architecture.get(
        "test_specification",
        {}
    )

    prompt = f"""
You are a senior software integration architect.

Perform a final cross-agent integration validation for an
AI-generated software product.

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

INFRASTRUCTURE:
{infrastructure}

TERRAFORM:
{terraform}

CODE QUALITY REPORT:
{code_quality}

TEST SPECIFICATION:
{test_specification}

Validate whether these generated specifications can work
together as one implementable software product.

Perform these checks:

1. Product → UI
   - Required product features should have corresponding UI pages,
     components, forms, or user flows.

2. Product → API
   - Important product features should have supporting API endpoints.

3. API → Database
   - APIs that require persistent data should have corresponding
     database tables or models.

4. Architecture → Infrastructure
   - Required architecture components should have corresponding
     infrastructure resources.

5. Infrastructure → Terraform
   - Important infrastructure resources should be represented
     in the Terraform specification.

6. Code Quality → Testing
   - Important quality and security concerns should be covered
     by the testing specification.

7. Overall consistency
   - Identify contradictions between the generated specifications.
   - Identify missing components that could prevent implementation.

Rules:
- Do not generate application code.
- Do not generate SQL.
- Do not generate Terraform code.
- Do not redesign the architecture.
- Report only meaningful issues.
- Minor differences that do not prevent implementation should be
  reported as warnings instead of issues.
- If everything is consistent, return an empty issues list.
- Return ONLY valid JSON.
- Do not use Markdown.
- Do not use code fences.

Use exactly this structure:

{{
    "status": "VALID",
    "score": 95,
    "checks": {{
        "product_ui": "PASS",
        "product_api": "PASS",
        "api_database": "PASS",
        "architecture_infrastructure": "PASS",
        "infrastructure_terraform": "PASS",
        "quality_testing": "PASS",
        "overall_consistency": "PASS"
    }},
    "issues": [],
    "warnings": [],
    "summary": "All generated specifications are consistent and implementation-ready."
}}

Status must be one of:

- VALID
- NEEDS_REVIEW
- INVALID

Score must be an integer from 0 to 100.

Each check must be one of:

- PASS
- WARNING
- FAIL
"""

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            validation_text = response.text.strip()

            if validation_text.startswith("```"):
                validation_text = validation_text.replace(
                    "```json",
                    ""
                )
                validation_text = validation_text.replace(
                    "```",
                    ""
                )
                validation_text = validation_text.strip()

            integration_report = json.loads(
                validation_text
            )

            state["architecture"][
                "integration_validation"
            ] = integration_report

            return state

        except Exception as error:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt

                print(
                    "Integration validation request failed. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:
                raise error

    return state