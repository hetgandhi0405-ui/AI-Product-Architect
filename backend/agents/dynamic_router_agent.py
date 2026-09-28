from typing import Any, Dict
import json
import os

from google import genai

from backend.agents.state import AgentState


MODEL_NAME = "gemini-3.5-flash-lite"


VALID_AGENTS = {
    "requirement",
    "suggestion",
    "product_planner",
    "ui_ux_spec",
    "api_spec",
    "database_spec",
    "architecture",
    "integration",
    "plugin_tool",
    "code_generation_contract",
    "code_quality",
    "test",
    "dependency",
    "environment_config",
    "integration_validation",
    "diagram",
    "infrastructure",
    "terraform",
    "validation",
    "self_correction",
}


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set."
        )

    return genai.Client(api_key=api_key)


def _extract_json(text: str) -> Dict[str, Any]:
    """
    Extract a JSON object from the Gemini response.
    """

    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

        if text.startswith("json"):
            text = text[4:].strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "No JSON object found in model response."
        )

    return json.loads(
        text[start:end + 1]
    )


def _clean_agent_list(value: Any):
    """
    Keep only valid agent names and remove duplicates.
    """

    if not isinstance(value, list):
        return []

    cleaned = []

    for agent in value:
        if not isinstance(agent, str):
            continue

        agent = agent.strip()

        if agent in VALID_AGENTS and agent not in cleaned:
            cleaned.append(agent)

    return cleaned


def _normalize_routing_result(
    result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate and normalize the routing decision returned
    by the LLM.
    """

    selected_agents = _clean_agent_list(
        result.get("selected_agents", [])
    )

    optional_agents = _clean_agent_list(
        result.get("optional_agents", [])
    )

    skipped_agents = _clean_agent_list(
        result.get("skipped_agents", [])
    )

    priority_order = _clean_agent_list(
        result.get("priority_order", [])
    )

    # An agent cannot be both selected and optional/skipped.
    optional_agents = [
        agent
        for agent in optional_agents
        if agent not in selected_agents
    ]

    skipped_agents = [
        agent
        for agent in skipped_agents
        if agent not in selected_agents
        and agent not in optional_agents
    ]

    # Priority order can contain only selected agents.
    priority_order = [
        agent
        for agent in priority_order
        if agent in selected_agents
    ]

    # Make sure every selected agent appears in the
    # priority order.
    for agent in selected_agents:
        if agent not in priority_order:
            priority_order.append(agent)

    result["selected_agents"] = selected_agents
    result["optional_agents"] = optional_agents
    result["skipped_agents"] = skipped_agents
    result["priority_order"] = priority_order

    result["project_type"] = str(
        result.get(
            "project_type",
            "General Software Application"
        )
    )

    result["complexity"] = str(
        result.get(
            "complexity",
            "Medium"
        )
    )

    routing_reasons = result.get(
        "routing_reasons",
        {}
    )

    if not isinstance(routing_reasons, dict):
        routing_reasons = {}

    # Keep reasons only for valid agents.
    result["routing_reasons"] = {
        key: value
        for key, value in routing_reasons.items()
        if key in VALID_AGENTS
    }

    result["routing_summary"] = str(
        result.get(
            "routing_summary",
            ""
        )
    )

    return result


def dynamic_router_agent(
    state: AgentState
) -> AgentState:
    """
    Analyze project requirements and determine which
    specialized agents should participate in the workflow.

    The router produces a routing plan only.
    It does not execute agents itself.
    """

    project_name = state.get(
        "project_name",
        ""
    )

    requirements = state.get(
        "requirements",
        ""
    )

    product_plan = state.get(
        "product_plan",
        {}
    )

    architecture = state.get(
        "architecture",
        {}
    )

    prompt = f"""
You are the Dynamic Agent Router inside an
autonomous AI software product generation platform.

Your task is to analyze the project and determine
which specialized AI agents are relevant.

PROJECT NAME:
{project_name}

PROJECT REQUIREMENTS:
{requirements}

PRODUCT PLAN:
{json.dumps(product_plan, indent=2)}

CURRENT ARCHITECTURE:
{json.dumps(architecture, indent=2)}

Available agents:

1. requirement
2. suggestion
3. product_planner
4. ui_ux_spec
5. api_spec
6. database_spec
7. architecture
8. integration
9. plugin_tool
10. code_generation_contract
11. code_quality
12. test
13. dependency
14. environment_config
15. integration_validation
16. diagram
17. infrastructure
18. terraform
19. validation
20. self_correction

IMPORTANT:
You MUST use ONLY the exact agent names listed above.

Never invent, rename, abbreviate, or create an
additional agent name.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "project_type": "",
  "complexity": "",
  "selected_agents": [],
  "optional_agents": [],
  "skipped_agents": [],
  "routing_reasons": {{}},
  "priority_order": [],
  "routing_summary": ""
}}

Rules:

1. Always select the core agents required to produce
   a valid software product.

2. Select specialized agents based on actual project
   requirements.

3. Do not select an agent merely because it exists.

4. For example:

   E-commerce may require:
   - plugin_tool
   - integration
   - test
   - infrastructure

   Healthcare may require:
   - security-related architectural considerations
   - integration_validation
   - validation

   AI applications may require:
   - plugin_tool
   - integration
   - infrastructure

   Real-time applications may require:
   - integration
   - infrastructure
   - test

5. Keep the routing decision explainable.

6. "selected_agents" contains agents that should run.

7. "optional_agents" contains useful agents that may
   be enabled depending on implementation choices.

8. "skipped_agents" contains agents that are not useful
   for this particular project.

9. "priority_order" contains selected agents in a
   sensible execution order.

10. Every agent name MUST exactly match the available
    agent list.

11. Never return names such as:
    "spec"
    "security_agent"
    "payment_agent"
    "frontend_agent"
    unless that exact name exists in the available
    agent list.

12. Do not generate application code.

13. Do not generate Terraform.

14. Do not execute external tools.

15. This agent is responsible only for routing analysis.
"""

    client = _get_client()

    last_error = None

    for _ in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            result = _extract_json(
                response.text
            )

            result = _normalize_routing_result(
                result
            )

            architecture = state.get(
                "architecture",
                {}
            )

            architecture[
                "dynamic_routing"
            ] = result

            state["architecture"] = architecture

            return state

        except Exception as error:
            last_error = error

    raise RuntimeError(
        "Dynamic Agent Router failed after 3 attempts: "
        f"{last_error}"
    )