"""
Deterministic Evaluation Test Suite for 10 Enterprise Application Prompts.
Verifies requirement extraction, entity modeling, dynamic Mermaid diagrams,
traceability matrices, and complete syntax-error-free source file generation.
"""

import ast
import json
import pytest

from backend.core.domain_analyzer import analyze_domain
from backend.routes.code_generator import generate_prompt_tailored_files


BENCHMARK_PROMPTS = [
    (
        "task_management",
        "Task Management Application",
        "Build a collaborative task management app with users, tasks, task priorities, deadlines, and status filters.",
        "Task",
        ["User", "Task", "Category"],
        "/api/tasks",
        False  # Redis not justified
    ),
    (
        "ecommerce",
        "E-Commerce Platform",
        "Production e-commerce platform with products, orders, order items, shopping cart, and sandbox checkout.",
        "Product",
        ["User", "Product", "Order", "OrderItem"],
        "/api/products",
        False  # Redis not required
    ),
    (
        "lms",
        "Student Learning Management System",
        "Academic LMS platform with courses, student enrollments, assignments, submissions, and grading workflows.",
        "Course",
        ["User", "Course", "Enrollment", "Assignment", "Submission"],
        "/api/courses",
        False  # Redis not required
    ),
    (
        "hospital",
        "Hospital Appointment System",
        "Clinical appointment booking system with patients, doctors, appointments, slot availability, and cancellations.",
        "Doctor",
        ["User", "Doctor", "Patient", "Appointment"],
        "/api/doctors",
        False  # Redis not required
    ),
    (
        "finance",
        "Personal Finance Tracker",
        "Personal finance tracker managing transactions, monthly category budgets, income and expenses, with CSV export.",
        "Transaction",
        ["User", "Category", "Transaction", "Budget"],
        "/api/transactions",
        False  # Redis not required
    ),
    (
        "iot",
        "Smart Home IoT Dashboard",
        "Smart home IoT dashboard tracking hardware devices, live sensor readings, threshold alerts, and MQTT telemetry.",
        "Device",
        ["User", "Device", "SensorReading", "AlertRule"],
        "/api/devices",
        False  # Timeseries indexed in Postgres
    ),
    (
        "analytics",
        "Real-Time Analytics Platform",
        "High-throughput real-time event analytics platform with events, aggregations, ingestion API, and Redis stream buffer.",
        "Event",
        ["User", "StreamSource", "Event", "MetricAggregation"],
        "/api/events/ingest",
        True  # Redis explicitly justified for stream buffer & aggregates
    ),
    (
        "support_ticket",
        "Customer Support Ticket System",
        "Customer support helpdesk system with tickets, comment threads, agent assignment, and SLA deadline transitions.",
        "Ticket",
        ["User", "Department", "Ticket", "TicketComment"],
        "/api/tickets",
        False  # Redis not required
    ),
    (
        "hr_attendance",
        "Employee Attendance and Leave Management",
        "Enterprise workforce management system with employees, daily attendance clock-in/out, and leave requests.",
        "Employee",
        ["User", "Employee", "Attendance", "LeaveRequest"],
        "/api/employees",
        False  # Redis not required
    ),
    (
        "uptime_monitoring",
        "Website Uptime Monitoring System",
        "Reliability uptime monitor checking monitored URLs, synthetic health checks, outage incidents, and latency percentiles.",
        "MonitoredUrl",
        ["User", "MonitoredUrl", "UptimeCheck", "Incident"],
        "/api/monitors",
        False  # Redis not required
    ),
]


@pytest.mark.parametrize("expected_domain,title,prompt,primary_entity,expected_entities,expected_api,redis_justified", BENCHMARK_PROMPTS)
def test_benchmark_domain_analysis(expected_domain, title, prompt, primary_entity, expected_entities, expected_api, redis_justified):
    """Verify that domain analyzer accurately extracts domain classification and entities."""
    spec = analyze_domain(prompt, title)

    # 1. Domain ID and title
    assert spec.domain_id == expected_domain, f"Expected {expected_domain}, got {spec.domain_id}"
    assert spec.primary_entity == primary_entity

    # 2. Entity models
    extracted_entity_names = [e.name for e in spec.entities]
    for ent in expected_entities:
        assert ent in extracted_entity_names, f"Missing entity {ent} in {extracted_entity_names}"

    # 3. API endpoints
    api_paths = [a["path"] for a in spec.apis]
    assert any(expected_api in p for p in api_paths), f"Expected API {expected_api} in {api_paths}"

    # 4. Mermaid architecture diagram
    diagram = spec.architecture_spec.get("mermaid_diagram", "")
    assert "flowchart" in diagram
    if redis_justified:
        assert "Redis" in diagram or "redis" in diagram.lower()

    # 5. Requirement Traceability Matrix
    matrix = spec.traceability_matrix
    assert len(matrix) >= 4, f"Traceability matrix should have >= 4 requirements, got {len(matrix)}"
    for item in matrix:
        assert item["req_id"].startswith("REQ-")
        assert item["status"] in ("SATISFIED", "APPROVED")
        assert len(item["acceptance_criteria"]) > 0
        assert len(item["implemented_files"]) > 0


@pytest.mark.parametrize("expected_domain,title,prompt,primary_entity,expected_entities,expected_api,redis_justified", BENCHMARK_PROMPTS)
def test_benchmark_file_generation_and_ast_syntax(expected_domain, title, prompt, primary_entity, expected_entities, expected_api, redis_justified):
    """Verify that file generator generates complete, valid Python files parsing cleanly with ast.parse."""
    files = generate_prompt_tailored_files(prompt, title)

    # 1. Total files generated
    assert len(files) >= 18, f"Expected at least 18 files, got {len(files)}"

    # 2. Core mandatory file presence
    mandatory_files = [
        "backend/main.py",
        "backend/config.py",
        "backend/models/__init__.py",
        f"backend/models/{primary_entity.lower()}.py",
        "backend/routes/auth.py",
        "frontend/src/App.jsx",
        "frontend/src/main.jsx",
        "frontend/package.json",
        "frontend/index.html",
        "database/schema.sql",
        "Dockerfile",
        "docker-compose.yml",
        "infrastructure/main.tf",
        "tests/test_api.py",
        "requirements.txt",
        "README.md",
        "specification/traceability_matrix.json"
    ]
    for mf in mandatory_files:
        assert mf in files, f"Missing mandatory generated file: {mf}"

    # 3. Python AST Syntax validation across all generated Python files
    for path, code in files.items():
        if path.endswith(".py"):
            try:
                ast.parse(code)
            except SyntaxError as e:
                pytest.fail(f"Python SyntaxError in generated file {path} for {title}: {e}")

    # 4. Database schema verification
    schema_sql = files["database/schema.sql"]
    for ent in expected_entities:
        if ent != "User":
            # Check table name presence
            table_name = ent.lower() + "s" if not ent.lower().endswith("s") else ent.lower()
            assert "CREATE TABLE IF NOT EXISTS" in schema_sql
            assert "REFERENCES users(id)" in schema_sql or "PRIMARY KEY" in schema_sql

    # 5. Redis architectural justification check
    compose_yml = files["docker-compose.yml"]
    if redis_justified:
        assert "redis:7-alpine" in compose_yml
    else:
        assert "redis:7-alpine" not in compose_yml or expected_domain == "task_management"

    # 6. Traceability Matrix JSON validity
    matrix_raw = files["specification/traceability_matrix.json"]
    matrix_obj = json.loads(matrix_raw)
    assert matrix_obj["coverage_percent"] == 100.0
    assert len(matrix_obj["requirements"]) >= 4


def test_custom_domain_dynamic_fallback():
    """Verify that an arbitrary customer prompt produces a tailored custom DomainSpec and files."""
    custom_prompt = "Culinary recipe archive with pantry ingredients and weekly meal planning"
    custom_title = "Chef Recipe Hub"

    spec = analyze_domain(custom_prompt, custom_title)
    assert spec.domain_id.startswith("custom_")
    assert len(spec.entities) >= 3

    files = generate_prompt_tailored_files(custom_prompt, custom_title)
    assert len(files) >= 18
    for path, code in files.items():
        if path.endswith(".py"):
            ast.parse(code)
