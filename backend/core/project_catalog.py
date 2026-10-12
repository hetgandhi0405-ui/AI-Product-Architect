"""
Canonical Project Catalog and Matching Engine for AI Product Architect.
Defines the 10 precomputed enterprise projects, their canonical prompts,
matching rules, and persistence layout.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import re


REPO_ROOT = Path(__file__).resolve().parents[2]
PRECOMPUTED_DIR = REPO_ROOT / "data" / "precomputed"


CANONICAL_PROJECTS: List[Dict[str, Any]] = [
    {
        "key": "task-management",
        "project_id": "proj-task-management",
        "project_name": "Task Management System",
        "canonical_prompt": "Build a task management application with user roles, projects, task assignments, priorities, due dates, status tracking, search, and task filtering.",
        "domain_id": "task_management",
        "primary_entity": "Task",
        "entities": ["User", "Project", "Task", "Category"],
        "api_prefix": "/api/tasks",
        "has_redis": False,
        "keywords": [
            "task", "tasks", "todo", "kanban", "assignment", "assignments",
            "priority", "priorities", "due date", "due dates", "task filtering",
            "status tracking", "project management", "work item"
        ],
        "description": "Collaborative task and project management platform with role-based access, task assignments, status workflows, priorities, and deadline filters."
    },
    {
        "key": "ecommerce",
        "project_id": "proj-ecommerce",
        "project_name": "E-Commerce Platform",
        "canonical_prompt": "Build an e-commerce platform with product listings, categories, product search, shopping cart, order management, inventory tracking, and a safe sandbox checkout workflow.",
        "domain_id": "ecommerce",
        "primary_entity": "Product",
        "entities": ["User", "Product", "Order", "OrderItem"],
        "api_prefix": "/api/products",
        "has_redis": False,
        "keywords": [
            "ecommerce", "e-commerce", "shopping", "cart", "product listings",
            "categories", "order management", "inventory tracking", "checkout",
            "sandbox checkout", "storefront", "catalog", "shop"
        ],
        "description": "High-conversion online retail storefront with product catalog, cart persistence, inventory tracking, and secure sandbox checkout."
    },
    {
        "key": "learning-management-system",
        "project_id": "proj-lms",
        "project_name": "Student Learning Management System",
        "canonical_prompt": "Build a student learning management system with students, instructors, courses, enrollment, lessons, quizzes, and learning progress.",
        "domain_id": "lms",
        "primary_entity": "Course",
        "entities": ["User", "Course", "Enrollment", "Assignment", "Submission"],
        "api_prefix": "/api/courses",
        "has_redis": False,
        "keywords": [
            "lms", "learning management", "students", "instructors", "courses",
            "enrollment", "lessons", "quizzes", "learning progress", "curriculum",
            "grading", "student", "instructor", "course"
        ],
        "description": "Academic learning management system supporting instructors, students, course enrollments, interactive lessons, quizzes, and student progress tracking."
    },
    {
        "key": "hospital-appointment",
        "project_id": "proj-hospital",
        "project_name": "Hospital Appointment System",
        "canonical_prompt": "Build a hospital appointment system with patient registration, doctor profiles, availability, appointment booking, cancellation, and appointment status tracking.",
        "domain_id": "hospital",
        "primary_entity": "Doctor",
        "entities": ["User", "Doctor", "Patient", "Appointment"],
        "api_prefix": "/api/doctors",
        "has_redis": False,
        "keywords": [
            "hospital", "appointment", "patient", "patients", "doctor", "doctors",
            "availability", "booking", "cancellation", "clinic", "clinical",
            "slot availability", "medical", "appointment status"
        ],
        "description": "Healthcare patient appointment booking platform with doctor availability schedules, double-booking conflict prevention, and synthetic patient records."
    },
    {
        "key": "personal-finance",
        "project_id": "proj-finance",
        "project_name": "Personal Finance Tracker",
        "canonical_prompt": "Build a personal finance tracker with transactions, categories, budgets, monthly summaries, filtering, and expense charts.",
        "domain_id": "finance",
        "primary_entity": "Transaction",
        "entities": ["User", "Category", "Transaction", "Budget"],
        "api_prefix": "/api/transactions",
        "has_redis": False,
        "keywords": [
            "finance", "personal finance", "transactions", "categories", "budgets",
            "monthly summaries", "expense charts", "income", "expenses", "spending",
            "budget", "transaction", "csv export"
        ],
        "description": "Personal finance management application with expense and income transaction tracking, category budgets, monthly aggregates, and CSV export."
    },
    {
        "key": "smart-home",
        "project_id": "proj-smart-home",
        "project_name": "Smart Home Dashboard",
        "canonical_prompt": "Build a smart home dashboard with rooms, devices, device status, monitoring, and device controls with a simulated IoT integration when hardware is unavailable.",
        "domain_id": "iot",
        "primary_entity": "Device",
        "entities": ["User", "Device", "SensorReading", "AlertRule"],
        "api_prefix": "/api/devices",
        "has_redis": False,
        "keywords": [
            "smart home", "iot", "dashboard", "rooms", "devices", "device status",
            "monitoring", "device controls", "simulated iot", "sensors", "sensor reading",
            "mqtt", "telemetry", "thermostat"
        ],
        "description": "Smart home IoT monitoring dashboard managing rooms, connected devices, simulated sensor telemetry ingestion, and interactive control toggles."
    },
    {
        "key": "real-time-analytics",
        "project_id": "proj-analytics",
        "project_name": "Real-Time Analytics Dashboard",
        "canonical_prompt": "Build a real-time analytics dashboard with event ingestion, aggregation, time-based filtering, charts, and activity summaries.",
        "domain_id": "analytics",
        "primary_entity": "Event",
        "entities": ["User", "StreamSource", "Event", "MetricAggregation"],
        "api_prefix": "/api/events",
        "has_redis": True,
        "keywords": [
            "analytics", "real-time analytics", "realtime analytics", "event ingestion",
            "aggregation", "time-based filtering", "charts", "activity summaries",
            "stream buffer", "redis stream", "events_per_sec", "metrics"
        ],
        "description": "High-throughput real-time event analytics platform with Redis streaming buffers, metric aggregation time buckets, and live telemetry charts."
    },
    {
        "key": "customer-support-ticket",
        "project_id": "proj-support-tickets",
        "project_name": "Customer Support Ticket System",
        "canonical_prompt": "Build a customer support ticket system with ticket creation, assignment, priorities, comments, search, and status tracking.",
        "domain_id": "support_ticket",
        "primary_entity": "Ticket",
        "entities": ["User", "Department", "Ticket", "TicketComment"],
        "api_prefix": "/api/tickets",
        "has_redis": False,
        "keywords": [
            "support ticket", "ticket", "tickets", "customer support", "helpdesk",
            "ticket creation", "assignment", "priorities", "comments", "ticket comment",
            "sla", "status tracking"
        ],
        "description": "Enterprise customer support helpdesk with ticket ticketing lifecycles, agent assignment, threaded comments, and SLA response time tracking."
    },
    {
        "key": "employee-attendance",
        "project_id": "proj-attendance",
        "project_name": "Employee Attendance Management",
        "canonical_prompt": "Build an employee attendance management system with employee records, check-in/check-out, attendance history, daily summaries, and leave requests.",
        "domain_id": "hr_attendance",
        "primary_entity": "Employee",
        "entities": ["User", "Employee", "Attendance", "LeaveRequest"],
        "api_prefix": "/api/employees",
        "has_redis": False,
        "keywords": [
            "attendance", "employee attendance", "employee records", "check-in",
            "check-out", "clock-in", "clock-out", "attendance history", "daily summaries",
            "leave requests", "leave", "hr", "workforce"
        ],
        "description": "Human resources workforce management system featuring employee directories, daily clock-in/out attendance logging, and leave request approval workflows."
    },
    {
        "key": "website-uptime-monitoring",
        "project_id": "proj-uptime-monitor",
        "project_name": "Website Uptime Monitoring",
        "canonical_prompt": "Build a website uptime monitoring system with website registration, health checks, uptime history, failure events, and alert simulation.",
        "domain_id": "uptime_monitoring",
        "primary_entity": "MonitoredUrl",
        "entities": ["User", "MonitoredUrl", "UptimeCheck", "Incident"],
        "api_prefix": "/api/monitors",
        "has_redis": False,
        "keywords": [
            "uptime", "uptime monitoring", "website uptime", "website registration",
            "health checks", "uptime history", "failure events", "alert simulation",
            "monitored url", "downtime", "probe", "latency"
        ],
        "description": "Website availability and latency monitoring platform with synthetic URL health checks, incident outage logs, and simulated alert dispatches."
    }
]

# Lookup map by key and domain_id
PROJECTS_BY_KEY = {p["key"]: p for p in CANONICAL_PROJECTS}
PROJECTS_BY_DOMAIN = {p["domain_id"]: p for p in CANONICAL_PROJECTS}
PROJECTS_BY_ID = {p["project_id"]: p for p in CANONICAL_PROJECTS}


def _tokenize(text: str) -> List[str]:
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    words = cleaned.split()
    # Filter stopwords
    stop = {"a", "an", "the", "and", "or", "with", "for", "in", "on", "at", "by", "from", "to", "of", "build", "create", "make", "app", "application", "system", "platform"}
    return [w for w in words if w not in stop and len(w) > 2]


def match_canonical_project(prompt: str, project_name: str = "") -> Optional[Dict[str, Any]]:
    """
    Intelligently determine whether a user prompt matches one of the 10 canonical projects.
    Returns the matching project catalog dictionary or None if no match.
    """
    if not prompt or not prompt.strip():
        return None

    raw_text = (prompt + " " + (project_name or "")).lower().strip()
    prompt_tokens = set(_tokenize(raw_text))

    best_match = None
    best_score = 0.0

    for proj in CANONICAL_PROJECTS:
        canonical_p = proj["canonical_prompt"].lower()
        
        # 1. Exact or near-exact string match
        if canonical_p in raw_text or raw_text in canonical_p:
            return proj

        # 2. Key phrase match
        for phrase in proj["keywords"]:
            if " " in phrase and phrase in raw_text:
                score = 3.0  # High bonus for exact multi-word key phrases
                if score > best_score:
                    best_score = score
                    best_match = proj

        # 3. Token overlap scoring
        canonical_tokens = set(_tokenize(canonical_p))
        overlap = len(prompt_tokens & canonical_tokens)
        if overlap > 0:
            jaccard = overlap / len(prompt_tokens | canonical_tokens)
            score = overlap + jaccard * 5.0
            if score > best_score:
                best_score = score
                best_match = proj

    # Threshold for match
    if best_match and best_score >= 2.0:
        return best_match

    # Fallback: check with domain analyzer
    try:
        from backend.core.domain_analyzer import analyze_domain
        spec = analyze_domain(prompt, project_name)
        if spec.domain_id in PROJECTS_BY_DOMAIN:
            return PROJECTS_BY_DOMAIN[spec.domain_id]
    except Exception:
        pass

    return None


def get_precomputed_project_dir(key: str) -> Path:
    return PRECOMPUTED_DIR / key


def load_precomputed_project_data(key: str) -> Optional[Dict[str, Any]]:
    """
    Load the precomputed result.json for a canonical project.
    """
    proj_dir = get_precomputed_project_dir(key)
    result_path = proj_dir / "result.json"
    if result_path.exists():
        try:
            with open(result_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def get_precomputed_manifest() -> Dict[str, Any]:
    manifest_path = PRECOMPUTED_DIR / "manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"projects": {}, "count": 0}
