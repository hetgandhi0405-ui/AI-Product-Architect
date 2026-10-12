# SQLAlchemy Models for Hospital Appointment System
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

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=0)
    name = Column(String(255), nullable=False)
    specialty = Column(String(100), nullable=False, index=True)
    license_number = Column(String(50), nullable=False, unique=True)
    room_number = Column(String(30), nullable=False)
    is_available = Column(Boolean, default=True)

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=0)
    name = Column(String(255), nullable=False)
    blood_group = Column(String(10), nullable=False)
    emergency_contact = Column(String(100), nullable=False)
    date_of_birth = Column(String(20), nullable=False)

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, nullable=False, default=0)
    patient_id = Column(Integer, nullable=False, default=0)
    appointment_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    reason = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

