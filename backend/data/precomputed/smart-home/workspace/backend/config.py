# Smart Home Dashboard - Configuration Settings
import os
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "Smart Home Dashboard"
    environment: str = os.getenv("ENVIRONMENT", "production")
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/smart-home-dashboard")
    # redis_url not required for this domain tier
    secret_key: str = os.getenv("SECRET_KEY", "ai-architect-secret-key-2026")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

settings = Settings()
