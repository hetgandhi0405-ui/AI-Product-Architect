import os
import json
import time

from google import genai
from backend.agents.state import AgentState


client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


def test_agent(state: AgentState) -> AgentState:
    """
    Generate a structured testing specification for the
    generated product.
    """

    requirements = state.get("requirements", "")
    product_plan = state.get("product_plan", {})
    ui_specification = state.get("ui_specification", {})
    api_specification = state.get("api_specification", {})
    database_specification = state.get("database_specification", {})
    architecture = state.get("architecture", {})

    prompt = f"""
You are a senior software test architect.

Create a practical testing specification for the following
AI-generated product.

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

Create tests that verify whether the generated product
can be implemented correctly.

Cover these areas:

1. Functional testing
2. API testing
3. Authentication and authorization testing
4. Database testing
5. Integration testing
6. Security testing
7. Edge case testing
8. Performance considerations

For every test case include:

- test_id
- category
- test_name
- objective
- input
- expected_result
- priority

Rules:
- Do not generate actual test code.
- Do not generate SQL.
- Do not generate Terraform.
- Do not generate application code.
- Tests must be relevant to the supplied product.
- Do not create unrelated test cases.
- Use realistic test scenarios.
- Return ONLY valid JSON.
- Do not use Markdown.
- Do not use code fences.

Use exactly this structure:

{{
    "testing_strategy": "Automated and manual testing",
    "test_cases": [
        {{
            "test_id": "TC001",
            "category": "Functional",
            "test_name": "User registration",
            "objective": "Verify that a new user can register.",
            "input": {{
                "email": "valid@example.com",
                "password": "ValidPassword123"
            }},
            "expected_result": "User account is created successfully.",
            "priority": "HIGH"
        }}
    ],
    "coverage": {{
        "functional": true,
        "api": true,
        "authentication": true,
        "database": true,
        "integration": true,
        "security": true,
        "edge_cases": true,
        "performance": true
    }},
    "summary": "..."
}}

Priority must be one of:

- HIGH
- MEDIUM
- LOW
"""

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            test_text = response.text.strip()

            if test_text.startswith("```"):
                test_text = test_text.replace("```json", "")
                test_text = test_text.replace("```", "")
                test_text = test_text.strip()

            test_specification = json.loads(test_text)

            state["architecture"]["test_specification"] = (
                test_specification
            )

            return state

        except Exception as error:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt

                print(
                    f"Test specification request failed. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:
                raise error

    return state