"""
Project Management API with real database persistence
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models.database import Project, User, AnalysisReport, ExportRecord
from ..core.logging_config import get_logger

router = APIRouter()
logger = get_logger("projects")


class ProjectCreate(BaseModel):
    """Model for creating new projects"""
    title: str
    description: Optional[str] = None
    original_filename: str
    video_path: str
    video_metadata: Dict[str, Any]
    editing_data: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []
    category: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Model for updating projects"""
    title: Optional[str] = None
    description: Optional[str] = None
    editing_data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    """Model for project responses"""
    id: int
    project_id: str
    title: str
    description: Optional[str]
    thumbnail_path: Optional[str]
    original_filename: str
    video_metadata: Dict[str, Any]
    editing_data: Dict[str, Any]
    status: str
    tags: List[str]
    category: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_accessed: datetime


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    user_id: int = 1,  # For now, default user - will be replaced with auth
    db: Session = Depends(get_db)
):
    """Create a new video editing project"""
    try:
        # Create new project record
        db_project = Project(
            title=project.title,
            description=project.description,
            original_filename=project.original_filename,
            video_path=project.video_path,
            video_metadata=project.video_metadata,
            editing_data=project.editing_data,
            tags=project.tags,
            category=project.category,
            owner_id=user_id
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        logger.info(f"Created new project: {db_project.project_id}")
        
        return ProjectResponse(
            id=db_project.id,
            project_id=db_project.project_id,
            title=db_project.title,
            description=db_project.description,
            thumbnail_path=db_project.thumbnail_path,
            original_filename=db_project.original_filename,
            video_metadata=db_project.video_metadata,
            editing_data=db_project.editing_data,
            status=db_project.status,
            tags=db_project.tags or [],
            category=db_project.category,
            created_at=db_project.created_at,
            updated_at=db_project.updated_at,
            last_accessed=db_project.last_accessed
        )
        
    except Exception as e:
        logger.error(f"Failed to create project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    user_id: int = 1,  # For now, default user
    search: Optional[str] = Query(None, description="Search projects by title"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query("active", description="Filter by status"),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """Get user's projects with filtering and search"""
    try:
        query = db.query(Project).filter(Project.owner_id == user_id)
        
        # Apply filters
        if status:
            query = query.filter(Project.status == status)
        
        if category:
            query = query.filter(Project.category == category)
        
        if search:
            query = query.filter(Project.title.ilike(f"%{search}%"))
        
        # Apply pagination
        projects = query.offset(offset).limit(limit).all()
        
        return [
            ProjectResponse(
                id=project.id,
                project_id=project.project_id,
                title=project.title,
                description=project.description,
                thumbnail_path=project.thumbnail_path,
                original_filename=project.original_filename,
                video_metadata=project.video_metadata,
                editing_data=project.editing_data,
                status=project.status,
                tags=project.tags or [],
                category=project.category,
                created_at=project.created_at,
                updated_at=project.updated_at,
                last_accessed=project.last_accessed
            )
            for project in projects
        ]
        
    except Exception as e:
        logger.error(f"Failed to get projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """Get specific project by ID"""
    try:
        project = db.query(Project).filter(
            Project.project_id == project_id,
            Project.owner_id == user_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update last accessed time
        project.last_accessed = datetime.utcnow()
        db.commit()
        
        return ProjectResponse(
            id=project.id,
            project_id=project.project_id,
            title=project.title,
            description=project.description,
            thumbnail_path=project.thumbnail_path,
            original_filename=project.original_filename,
            video_metadata=project.video_metadata,
            editing_data=project.editing_data,
            status=project.status,
            tags=project.tags or [],
            category=project.category,
            created_at=project.created_at,
            updated_at=project.updated_at,
            last_accessed=project.last_accessed
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """Update project"""
    try:
        project = db.query(Project).filter(
            Project.project_id == project_id,
            Project.owner_id == user_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update fields
        update_data = project_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        project.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(project)
        
        logger.info(f"Updated project: {project_id}")
        
        return ProjectResponse(
            id=project.id,
            project_id=project.project_id,
            title=project.title,
            description=project.description,
            thumbnail_path=project.thumbnail_path,
            original_filename=project.original_filename,
            video_metadata=project.video_metadata,
            editing_data=project.editing_data,
            status=project.status,
            tags=project.tags or [],
            category=project.category,
            created_at=project.created_at,
            updated_at=project.updated_at,
            last_accessed=project.last_accessed
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """Delete project"""
    try:
        project = db.query(Project).filter(
            Project.project_id == project_id,
            Project.owner_id == user_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        db.delete(project)
        db.commit()
        
        logger.info(f"Deleted project: {project_id}")
        
        return JSONResponse(
            status_code=200,
            content={"message": "Project deleted successfully"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
