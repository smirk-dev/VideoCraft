"""
Database models for project persistence
Uses SQLAlchemy with SQLite for simplicity, can be upgraded to PostgreSQL
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """User model for authentication and project ownership"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    analysis_reports = relationship("AnalysisReport", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    """Project model for video editing projects"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    thumbnail_path = Column(String(500))
    
    # Video information
    original_filename = Column(String(255), nullable=False)
    video_path = Column(String(500), nullable=False)
    video_metadata = Column(JSON)  # Store video info like duration, resolution, etc.
    
    # Editing data
    editing_data = Column(JSON)  # Store trim points, cuts, filters
    
    # Project metadata
    status = Column(String(20), default="active")  # active, archived, deleted
    tags = Column(JSON)  # Array of tags
    category = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    analysis_reports = relationship("AnalysisReport", back_populates="project", cascade="all, delete-orphan")
    exports = relationship("ExportRecord", back_populates="project", cascade="all, delete-orphan")


class AnalysisReport(Base):
    """AI analysis reports for videos"""
    __tablename__ = "analysis_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Analysis data
    analysis_type = Column(String(50), nullable=False)  # scene, emotion, object, etc.
    analysis_data = Column(JSON, nullable=False)  # Actual analysis results
    confidence_score = Column(Integer)  # Overall confidence (0-100)
    processing_time = Column(Integer)  # Processing time in seconds
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="analysis_reports")
    user = relationship("User", back_populates="analysis_reports")


class ExportRecord(Base):
    """Record of video exports"""
    __tablename__ = "export_records"
    
    id = Column(Integer, primary_key=True, index=True)
    export_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Export details
    export_type = Column(String(20), nullable=False)  # video, pdf, json
    output_filename = Column(String(255), nullable=False)
    output_path = Column(String(500))
    file_size = Column(Integer)  # Size in bytes
    quality = Column(String(20))  # high, medium, low
    format = Column(String(10))  # mp4, avi, pdf, json
    
    # Processing info
    processing_time = Column(Integer)  # Processing time in seconds
    applied_operations = Column(JSON)  # What operations were applied
    
    # Status
    status = Column(String(20), default="completed")  # processing, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="exports")


class SharedProject(Base):
    """Shared project links"""
    __tablename__ = "shared_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    share_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Share details
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    share_type = Column(String(20), nullable=False)  # public, private, password
    password_hash = Column(String(255))  # For password-protected shares
    expires_at = Column(DateTime)  # Optional expiration
    access_count = Column(Integer, default=0)
    max_access_count = Column(Integer)  # Optional access limit
    
    # Permissions
    can_download = Column(Boolean, default=True)
    can_view_analysis = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime)
    
    # Relationships
    project = relationship("Project")


class UserSession(Base):
    """User session management"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session data
    ip_address = Column(String(45))
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User")
