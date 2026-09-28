import json
import os
import time

from google import genai

from backend.agents.state import AgentState


MODEL_NAME = "gemini-3.5-flash-lite"


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set."
        )

    return genai.Client(api_key=api_key)


def _extract_json(text: str):
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

        if text.lower().startswith("json"):
            text = text[4:].strip()

    return json.loads(text)


def security_agent(state: AgentState) -> AgentState:
    requirements = state.get("requirements", "")
    product_plan = state.get("product_plan", {})
    api_specification = state.get(
        "api_specification",
        {}
    )
    database_specification = state.get(
        "database_specification",
        {}
    )
    architecture = state.get(
        "architecture",
        {}
    )
    dependency_specification = state.get(
        "dependency_specification",
        {}
    )
    environment_configuration = state.get(
        "environment_configuration",
        {}
    )
    infrastructure = architecture.get(
        "infrastructure",
        {}
    )

    prompt = f"""
You are a Security Architect Agent inside an
AI-powered software architecture system.

Analyze the generated product specifications and
identify security requirements, risks, weaknesses,
and recommended controls.

PROJECT REQUIREMENTS:
{requirements}

PRODUCT PLAN:
{json.dumps(product_plan, indent=2)}

API SPECIFICATION:
{json.dumps(api_specification, indent=2)}

DATABASE SPECIFICATION:
{json.dumps(database_specification, indent=2)}

ARCHITECTURE:
{json.dumps(architecture, indent=2)}

INFRASTRUCTURE:
{json.dumps(infrastructure, indent=2)}

DEPENDENCY SPECIFICATION:
{json.dumps(dependency_specification, indent=2)}

ENVIRONMENT CONFIGURATION:
{json.dumps(environment_configuration, indent=2)}

Analyze these security areas:

1. Authentication
2. Authorization
3. API security
4. Database security
5. Cloud and infrastructure security
6. Network security
7. Secrets and configuration
8. Dependency security
9. Logging and monitoring
10. Data protection
11. Input validation
12. Rate limiting
13. Error handling
14. Security testing

For every identified issue provide:

- issue_id
- category
- severity
- title
- description
- affected_component
- recommendation

Severity must be one of:

CRITICAL
HIGH
MEDIUM
LOW
INFO

Return ONLY valid JSON using this structure:

{{
  "status": "PASS",
  "risk_level": "LOW",
  "security_score": 0,
  "issues": [],
  "recommendations": [],
  "security_controls": {{
    "authentication": [],
    "authorization": [],
    "api_security": [],
    "database_security": [],
    "cloud_security": [],
    "network_security": [],
    "secrets_management": [],
    "monitoring": [],
    "data_protection": []
  }},
  "summary": ""
}}

Rules:

1. Do not generate application code.
2. Do not generate credentials or real secrets.
3. Do not invent vulnerabilities that are unrelated
   to the generated architecture.
4. Base findings on the supplied specifications.
5. Treat missing security controls as potential
   issues when they are relevant.
6. Security score must be between 0 and 100.
7. PASS means no significant security issues were found.
8. REVIEW means issues or important warnings exist.
9. Do not claim legal or regulatory compliance.
10. Return JSON only.
"""

    last_error = None

    for attempt in range(3):
        try:
            client = _get_client()

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            security_report = _extract_json(
                response.text
            )

            state["architecture"][
                "security_analysis"
            ] = security_report

            return state

        except Exception as exc:
            last_error = exc

            if attempt < 2:
                time.sleep(1)

    raise RuntimeError(
        "Security Agent failed after 3 attempts: "
        f"{last_error}"
    )
