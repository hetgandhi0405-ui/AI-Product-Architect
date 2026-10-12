# Real-Time Analytics Dashboard - Configuration Settings
import os
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "Real-Time Analytics Dashboard"
    environment: str = os.getenv("ENVIRONMENT", "production")
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/real-time-analytics-dashboard")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    secret_key: str = os.getenv("SECRET_KEY", "ai-architect-secret-key-2026")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

settings = Settings()
