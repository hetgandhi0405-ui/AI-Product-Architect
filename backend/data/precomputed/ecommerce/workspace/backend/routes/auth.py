# Authentication & JWT Handlers
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user_email: str

@router.post("/login", response_model=TokenResponse)
def login(creds: LoginRequest):
    return {
        "access_token": "jwt_token_sample_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "token_type": "bearer",
        "expires_in": 3600,
        "user_email": creds.email
    }

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(creds: LoginRequest):
    return {
        "status": "user_created",
        "email": creds.email,
        "role": "user",
        "message": "User registered successfully"
    }

@router.get("/me")
def get_current_user():
    return {
        "email": "admin@cloud-architect.io",
        "role": "administrator",
        "is_active": True,
        "permissions": ["read", "write", "deploy"]
    }
