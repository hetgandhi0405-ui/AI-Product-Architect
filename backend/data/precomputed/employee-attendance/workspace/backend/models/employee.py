# SQLAlchemy Models for Employee Attendance Management
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

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=0)
    employee_code = Column(String(50), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    leave_balance = Column(Integer, nullable=False, default=0)

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, nullable=False, default=0)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    clock_in = Column(DateTime, nullable=False, default=datetime.utcnow)
    clock_out = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, index=True)

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, nullable=False, default=0)
    leave_type = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    days_count = Column(Integer, nullable=False, default=0)
    reason = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

