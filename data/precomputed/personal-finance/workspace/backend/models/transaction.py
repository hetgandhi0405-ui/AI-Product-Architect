# SQLAlchemy Models for Personal Finance Tracker
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

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=0)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    color = Column(String(30), nullable=False)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=0)
    category_id = Column(Integer, nullable=False, default=0)
    amount = Column(Float, nullable=False, default=0.0)
    transaction_type = Column(String(50), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=0)
    category_id = Column(Integer, nullable=False, default=0)
    monthly_limit = Column(Float, nullable=False, default=0.0)
    current_spent = Column(Float, nullable=False, default=0.0)
    month_year = Column(String(20), nullable=False)

