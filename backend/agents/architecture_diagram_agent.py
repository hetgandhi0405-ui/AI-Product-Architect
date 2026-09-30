"""
Phase 5 — Architecture Diagram Generator
==========================================
Generates a Mermaid flowchart diagram from infrastructure_state.json.

The diagram is generated dynamically from the ACTUAL resource graph —
not a static template. Only services present in the architecture are shown.

Output: architecture_diagram (Mermaid LR flowchart string)
"""
from __future__ import annotations

from backend.agents.state import AgentState


# Friendly labels for resource types
_RESOURCE_LABELS = {
    "aws_vpc":                "VPC",
    "aws_alb":                "Load Balancer (ALB)",
    "aws_ecs_fargate":        "ECS Fargate",
    "aws_ec2":                "EC2 Instances",
    "aws_rds":                "RDS Database",
    "aws_elasticache":        "ElastiCache (Redis)",
    "aws_s3_bucket":          "S3 Bucket",
    "aws_wafv2_web_acl":      "WAF",
    "aws_secretsmanager_secret": "Secrets Manager",
    "aws_cloudwatch":         "CloudWatch",
}

# Relationship label display
_EDGE_LABELS = {
    "routes_traffic_to":     "routes →",
    "reads_writes":          "reads/writes →",
    "contains":              "contains",
    "caches_via":            "cache →",
    "stores_to":             "stores →",
    "protects":              "protects →",
    "reads_secrets_from":    "secrets →",
}


def architecture_diagram_agent(state: AgentState) -> AgentState:
    """
    Render a Mermaid flowchart from infrastructure_state.
    Sets state['architecture_diagram'] to a Mermaid LR string.
    """
    infra: dict = state.get("infrastructure_state", {})
    resources: list = infra.get("resources", [])
    relationships: list = infra.get("relationships", [])

    if not resources:
        # Fallback minimal diagram
        diagram = _minimal_fallback_diagram(state)
        state["architecture_diagram"] = diagram
        arch = state.get("architecture", {})
        arch["diagram"] = diagram
        state["architecture"] = arch
        return state

    lines = ["flowchart LR"]

    # ── Add user entry node ──────────────────────────────────────────────────
    lines.append('    USER["👤 User"]')

    # ── Add resource nodes ───────────────────────────────────────────────────
    for res in resources:
        rid = _safe_id(res["id"])
        rtype = res.get("type", "aws_resource")
        label = _RESOURCE_LABELS.get(rtype, rtype.replace("aws_", "").upper())
        name = res.get("name", rid)
        lines.append(f'    {rid}["{label}\\n{name}"]')

    # ── User → WAF or ALB ────────────────────────────────────────────────────
    resource_ids = {r["id"] for r in resources}
    if "waf-main" in resource_ids:
        lines.append("    USER --> waf_main")
        lines.append("    waf_main --> alb_main")
    elif "alb-main" in resource_ids:
        lines.append("    USER --> alb_main")

    # ── Render relationships ──────────────────────────────────────────────────
    for rel in relationships:
        src = _safe_id(rel["from"])
        dst = _safe_id(rel["to"])
        rel_type = rel.get("type", "")
        edge_label = _EDGE_LABELS.get(rel_type, rel_type)

        # Skip user→alb / waf→alb already drawn above
        if rel_type == "protects":
            continue  # drawn above

        lines.append(f'    {src} -->|"{edge_label}"| {dst}')

    # ── Styling ───────────────────────────────────────────────────────────────
    lines.append("    style USER fill:#4CAF50,color:#fff,stroke:#388E3C")
    for res in resources:
        rid = _safe_id(res["id"])
        rtype = res.get("type", "")
        if "alb" in rtype:
            lines.append(f"    style {rid} fill:#2196F3,color:#fff,stroke:#1565C0")
        elif "rds" in rtype:
            lines.append(f"    style {rid} fill:#FF9800,color:#fff,stroke:#E65100")
        elif "elasticache" in rtype:
            lines.append(f"    style {rid} fill:#9C27B0,color:#fff,stroke:#6A1B9A")
        elif "s3" in rtype:
            lines.append(f"    style {rid} fill:#00BCD4,color:#fff,stroke:#006064")
        elif "waf" in rtype:
            lines.append(f"    style {rid} fill:#F44336,color:#fff,stroke:#B71C1C")
        elif "cloudwatch" in rtype:
            lines.append(f"    style {rid} fill:#607D8B,color:#fff,stroke:#37474F")
        else:
            lines.append(f"    style {rid} fill:#1565C0,color:#fff,stroke:#0D47A1")

    diagram = "\n".join(lines)
    state["architecture_diagram"] = diagram

    arch = state.get("architecture", {})
    arch["diagram"] = diagram
    state["architecture"] = arch

    return state


def _safe_id(node_id: str) -> str:
    """Convert node IDs like 'alb-main' to valid Mermaid IDs 'alb_main'."""
    return node_id.replace("-", "_").replace(".", "_").replace(" ", "_")


def _minimal_fallback_diagram(state: AgentState) -> str:
    """Minimal diagram when no infrastructure state is available."""
    project = state.get("project_name", "App")
    return f"""flowchart LR
    USER["👤 User"] --> ALB["Load Balancer"]
    ALB --> APP["FastAPI Backend\\n{project}"]
    APP --> DB["PostgreSQL Database"]
    style USER fill:#4CAF50,color:#fff
    style ALB fill:#2196F3,color:#fff
    style APP fill:#1565C0,color:#fff
    style DB fill:#FF9800,color:#fff"""
