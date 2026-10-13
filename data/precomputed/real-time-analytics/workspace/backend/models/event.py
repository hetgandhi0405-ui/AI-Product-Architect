# SQLAlchemy Models for Real-Time Analytics Dashboard
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

class StreamSource(Base):
    __tablename__ = "stream_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    api_key_hash = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    events_per_sec = Column(Integer, nullable=False, default=0)

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, nullable=False, default=0)
    event_type = Column(String(100), nullable=False, index=True)
    payload_json = Column(String(255), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=False)

class MetricAggregation(Base):
    __tablename__ = "metric_aggregations"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    window_interval = Column(String(20), nullable=False)
    count = Column(Integer, nullable=False, default=0)
    sum_value = Column(Float, nullable=False, default=0.0)
    avg_value = Column(Float, nullable=False, default=0.0)
    window_end = Column(DateTime, nullable=False, default=datetime.utcnow)

