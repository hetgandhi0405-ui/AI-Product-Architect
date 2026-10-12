# SQLAlchemy Models for Website Uptime Monitoring
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class MonitoredUrl(Base):
    __tablename__ = "monitored_urls"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=0)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False, index=True)
    check_interval_seconds = Column(Integer, nullable=False, default=0)
    expected_status_code = Column(Integer, nullable=False, default=0)
    timeout_seconds = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class UptimeCheck(Base):
    __tablename__ = "uptime_checks"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, nullable=False, default=0)
    status_code = Column(Integer, nullable=False, default=0)
    response_time_ms = Column(Float, nullable=False, default=0.0)
    is_up = Column(Boolean, default=True)
    checked_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, index=True)
    root_cause = Column(String(255), nullable=False)

