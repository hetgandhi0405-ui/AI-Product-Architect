from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import requirements, projects


app = FastAPI(
    title="AI Product Architect API",
    description="Backend API for AI-powered cloud product generation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pathlib import Path
from fastapi.staticfiles import StaticFiles

app.include_router(
    requirements.router,
    prefix="/api"
)

app.include_router(
    projects.router,
    prefix="/api"
)

_frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if _frontend_dir.exists():
    app.mount("/frontend", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")



@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/", response_class=HTMLResponse)
@app.get("/ui", response_class=HTMLResponse)
@app.get("/generator", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def generator_ui():
    """
    Autonomous AI Product-to-Cloud Deployment and Optimization Platform Dashboard.
    Renders interactive UI covering all pipeline sections and tabs.
    """
    index_file = _frontend_dir / "index.html"
    if index_file.exists():
        return HTMLResponse(
            content=index_file.read_text(encoding="utf-8"),
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    return HTMLResponse(content="<h1>AI Product Architect</h1><p>Frontend file not found at frontend/index.html</p>", status_code=404)


@app.get("/preview/{project_id}", response_class=HTMLResponse)
def project_preview(project_id: str):
    """
    Live interactive deployment preview for the generated product.
    """
    from backend.routes.preview_html import render_project_preview_html
    return HTMLResponse(
        content=render_project_preview_html(project_id),
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


