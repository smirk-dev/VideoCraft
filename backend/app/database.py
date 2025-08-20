"""
Database configuration and connection management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models.database import Base
import os

# Database URL - using SQLite for simplicity, can be changed to PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./videocraft.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
