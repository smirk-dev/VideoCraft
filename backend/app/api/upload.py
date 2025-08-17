"""
File Upload API endpoints for VideoCraft AI Video Editor
"""
import os
import shutil
import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends
from fastapi.responses import JSONResponse
import aiofiles

from ..core.config import settings
from ..core.logging_config import get_logger

router = APIRouter()
logger = get_logger("upload")


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate if file has allowed extension"""
    file_ext = Path(filename).suffix.lower()
    return file_ext in allowed_extensions


def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename while preserving extension"""
    file_ext = Path(original_filename).suffix
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{unique_id}{file_ext}"


async def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    """Save uploaded file to destination with optimized chunking for large files"""
    try:
        async with aiofiles.open(destination, 'wb') as f:
            # Use larger chunk size for better performance with large files
            chunk_size = 1024 * 1024  # 1MB chunks for better performance
            while chunk := await upload_file.read(chunk_size):
                await f.write(chunk)
        return destination
    except Exception as e:
        logger.error(f"Error saving file {upload_file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error saving file")


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """
    Upload a video file for processing
    
    - **file**: Video file to upload
    - **title**: Optional title for the video
    - **description**: Optional description
    """
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    if not validate_file_extension(file.filename, settings.ALLOWED_VIDEO_EXTENSIONS):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_VIDEO_EXTENSIONS)}"
        )
    
    # Check file size
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024*1024):.1f}GB"
        )
    
    try:
        # Generate unique filename
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save file
        await save_upload_file(file, file_path)
        
        # Get file info
        file_info = {
            "id": str(uuid.uuid4()),
            "original_filename": file.filename,
            "filename": unique_filename,
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "content_type": file.content_type,
            "upload_time": datetime.now().isoformat(),
            "title": title or file.filename,
            "description": description,
            "status": "uploaded",
            "processed": False
        }
        
        logger.info(f"Video uploaded successfully: {file.filename} -> {unique_filename}")
        
        return JSONResponse(
            status_code=201,
            content={
                "message": "Video uploaded successfully",
                "data": file_info
            }
        )
        
    except Exception as e:
        logger.error(f"Error uploading video {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error uploading video")


@router.post("/audio")
async def upload_audio(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """
    Upload an audio file for processing
    
    - **file**: Audio file to upload
    - **title**: Optional title for the audio
    - **description**: Optional description
    """
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    if not validate_file_extension(file.filename, settings.ALLOWED_AUDIO_EXTENSIONS):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_AUDIO_EXTENSIONS)}"
        )
    
    try:
        # Generate unique filename
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save file
        await save_upload_file(file, file_path)
        
        # Get file info
        file_info = {
            "id": str(uuid.uuid4()),
            "original_filename": file.filename,
            "filename": unique_filename,
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "content_type": file.content_type,
            "upload_time": datetime.now().isoformat(),
            "title": title or file.filename,
            "description": description,
            "status": "uploaded",
            "processed": False
        }
        
        logger.info(f"Audio uploaded successfully: {file.filename} -> {unique_filename}")
        
        return JSONResponse(
            status_code=201,
            content={
                "message": "Audio uploaded successfully",
                "data": file_info
            }
        )
        
    except Exception as e:
        logger.error(f"Error uploading audio {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error uploading audio")


@router.post("/multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """
    Upload multiple files (videos/audio) for batch processing
    """
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 10:  # Limit batch uploads
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per batch")
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Determine file type
            file_ext = Path(file.filename).suffix.lower()
            
            if file_ext in settings.ALLOWED_VIDEO_EXTENSIONS:
                file_type = "video"
                allowed_extensions = settings.ALLOWED_VIDEO_EXTENSIONS
            elif file_ext in settings.ALLOWED_AUDIO_EXTENSIONS:
                file_type = "audio"
                allowed_extensions = settings.ALLOWED_AUDIO_EXTENSIONS
            else:
                errors.append({
                    "filename": file.filename,
                    "error": f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_VIDEO_EXTENSIONS + settings.ALLOWED_AUDIO_EXTENSIONS)}"
                })
                continue
            
            # Generate unique filename
            unique_filename = generate_unique_filename(file.filename)
            file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
            
            # Save file
            await save_upload_file(file, file_path)
            
            # File info
            file_info = {
                "id": str(uuid.uuid4()),
                "original_filename": file.filename,
                "filename": unique_filename,
                "file_path": file_path,
                "file_size": os.path.getsize(file_path),
                "content_type": file.content_type,
                "file_type": file_type,
                "upload_time": datetime.now().isoformat(),
                "title": title or file.filename,
                "description": description,
                "status": "uploaded",
                "processed": False
            }
            
            uploaded_files.append(file_info)
            logger.info(f"File uploaded successfully: {file.filename} -> {unique_filename}")
            
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
            logger.error(f"Error uploading file {file.filename}: {str(e)}")
    
    return JSONResponse(
        status_code=201,
        content={
            "message": f"Batch upload completed. {len(uploaded_files)} files uploaded successfully.",
            "uploaded_files": uploaded_files,
            "errors": errors
        }
    )


@router.get("/status/{filename}")
async def get_upload_status(filename: str):
    """Get status of uploaded file"""
    
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    file_stat = os.stat(file_path)
    
    return {
        "filename": filename,
        "file_path": file_path,
        "file_size": file_stat.st_size,
        "upload_time": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
        "last_modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
        "exists": True
    }


@router.delete("/delete/{filename}")
async def delete_uploaded_file(filename: str):
    """Delete uploaded file"""
    
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        os.remove(file_path)
        logger.info(f"File deleted successfully: {filename}")
        
        return {
            "message": "File deleted successfully",
            "filename": filename
        }
        
    except Exception as e:
        logger.error(f"Error deleting file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting file")


@router.get("/list")
async def list_uploaded_files():
    """List all uploaded files"""
    
    if not os.path.exists(settings.UPLOAD_DIR):
        return {"files": []}
    
    files = []
    
    try:
        for filename in os.listdir(settings.UPLOAD_DIR):
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                file_ext = Path(filename).suffix.lower()
                
                # Determine file type
                if file_ext in settings.ALLOWED_VIDEO_EXTENSIONS:
                    file_type = "video"
                elif file_ext in settings.ALLOWED_AUDIO_EXTENSIONS:
                    file_type = "audio"
                else:
                    file_type = "unknown"
                
                files.append({
                    "filename": filename,
                    "file_type": file_type,
                    "file_size": file_stat.st_size,
                    "upload_time": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                    "last_modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                })
        
        return {"files": files}
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail="Error listing files")
