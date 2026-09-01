from fastapi import FastAPI

from backend.routes import requirements, projects


app = FastAPI(
    title="AI Product Architect API",
    description="Backend API for AI-powered cloud product generation",
    version="1.0.0"
)


app.include_router(
    requirements.router,
    prefix="/api"
)

app.include_router(
    projects.router,
    prefix="/api"
)


@app.get("/")
def root():

    return {
        "project": "AI Product Architect",
        "member": "Member 2",
        "status": "running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }