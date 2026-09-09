import os
import json
import time

from google import genai
from backend.agents.state import AgentState


client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


def database_spec_agent(state: AgentState) -> AgentState:
    """
    Generate a structured database specification from
    the product plan and API specification.
    """

    requirements = state["requirements"]
    product_plan = state.get("product_plan", {})
    api_specification = state.get("api_specification", {})

    prompt = f"""
You are a senior database architect.

Design the database specification for this application.

CUSTOMER REQUIREMENTS:
{requirements}

PRODUCT PLAN:
{product_plan}

API SPECIFICATION:
{api_specification}

Create a practical relational database design.

Identify:

1. Database type
2. Tables
3. Columns for each table
4. Primary keys
5. Foreign keys
6. Relationships
7. Important indexes

Rules:

- Design the database according to the actual requirements.
- Tables must support the product features and APIs.
- Do not create unrelated tables.
- Use a relational database where appropriate.
- Use clear table and column names.
- Every table must have a primary key.
- Use foreign keys where relationships exist.
- Do not generate SQL code.
- Do not generate cloud architecture.
- Do not generate Terraform.
- Return ONLY valid JSON.

Use exactly this structure:

{{
    "database_type": "PostgreSQL",
    "tables": [
        {{
            "name": "users",
            "purpose": "...",
            "columns": [
                {{
                    "name": "id",
                    "type": "UUID",
                    "primary_key": true,
                    "nullable": false
                }}
            ],
            "relationships": [],
            "indexes": []
        }}
    ]
}}

Do not use Markdown.
Do not use code fences.
"""

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            database_text = response.text.strip()

            if database_text.startswith("```"):
                database_text = database_text.replace(
                    "```json", ""
                )
                database_text = database_text.replace(
                    "```", ""
                )
                database_text = database_text.strip()

            database_specification = json.loads(
                database_text
            )

            state["database_specification"] = (
                database_specification
            )

            return state

        except Exception as error:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt

                print(
                    f"Database specification request failed. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)
            else:
                raise error

    return state
