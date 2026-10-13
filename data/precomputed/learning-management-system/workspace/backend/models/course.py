# SQLAlchemy Models for Student Learning Management System
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

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    instructor_id = Column(Integer, nullable=False, default=0)
    credits = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=0)
    course_id = Column(Integer, nullable=False, default=0)
    enrolled_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(50), nullable=False)

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, nullable=False, default=0)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    due_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    max_points = Column(Integer, nullable=False, default=0)

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, nullable=False, default=0)
    student_id = Column(Integer, nullable=False, default=0)
    content = Column(String(255), nullable=False)
    grade = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), nullable=False)
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)

