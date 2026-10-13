# SQLAlchemy Models for Smart Home Dashboard
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

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=0)
    name = Column(String(255), nullable=False)
    device_type = Column(String(100), nullable=False, index=True)
    room = Column(String(100), nullable=False)
    ip_address = Column(String(45), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, nullable=False, default=0)
    metric = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False, default=0.0)
    unit = Column(String(20), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, nullable=False, default=0)
    metric = Column(String(100), nullable=False)
    condition = Column(String(20), nullable=False)
    threshold = Column(Float, nullable=False, default=0.0)
    is_active = Column(Boolean, default=True)

