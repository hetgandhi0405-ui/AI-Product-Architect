import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.routes.preview_html import render_project_preview_html

projects = [
    'proj-attendance',
    'proj-ecommerce',
    'proj-lms',
    'proj-hospital',
    'proj-finance',
    'proj-smart-home',
    'proj-analytics',
    'proj-support-tickets',
    'proj-task-management',
    'proj-uptime-monitor'
]

for pid in projects:
    html = render_project_preview_html(pid)
    title_m = re.search(r'class="brand-title">([^<]+)<', html)
    entity_m = re.search(r'<span>Create ([^<]+)<', html)
    title = title_m.group(1) if title_m else 'UNKNOWN'
    entity = entity_m.group(1) if entity_m else 'UNKNOWN'
    print(f"{pid:<22} -> Title: {title:<36} | Entity: {entity}")
