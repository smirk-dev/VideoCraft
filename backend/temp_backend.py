"""
Temporary Simple VideoCraft Backend without MoviePy
For testing export functionality
"""
import os
import logging
import shutil
import uuid
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class VideoProcessingRequest(BaseModel):
    video_filename: str
    editing_data: Dict[str, Any]
    output_filename: Optional[str] = None

class VideoProcessingResponse(BaseModel):
    success: bool
    output_path: Optional[str] = None
    output_filename: Optional[str] = None
    video_info: Optional[Dict] = None
    processing_time: Optional[str] = None
    applied_operations: Optional[Dict] = None
    error: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting VideoCraft Temporary Backend...")
    
    # Ensure directories exist
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('processed', exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    
    yield
    
    logger.info("🔄 Shutting down VideoCraft...")

# Initialize FastAPI app
app = FastAPI(
    title="VideoCraft Temporary Backend",
    description="Temporary backend for testing export functionality",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "VideoCraft Temporary Backend is running"}

# File upload endpoint
@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        # Create unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = Path("uploads") / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded: {unique_filename}")
        
        return {
            "success": True,
            "filename": unique_filename,
            "original_name": file.filename,
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size
        }
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Video processing endpoint - simplified for testing
@app.post("/api/edit/process")
async def process_video(request: VideoProcessingRequest):
    try:
        input_path = Path("uploads") / request.video_filename
        
        if not input_path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # Generate output filename
        output_filename = request.output_filename or f"processed_{request.video_filename}"
        output_path = Path("processed") / output_filename
        
        # For now, just copy the file (no actual processing)
        shutil.copy2(input_path, output_path)
        
        logger.info(f"Video processed (copied): {request.video_filename} -> {output_filename}")
        
        return VideoProcessingResponse(
            success=True,
            output_path=str(output_path),
            output_filename=output_filename,
            video_info={"message": "File copied (processing disabled)"},
            processing_time="0s",
            applied_operations={"copy": True}
        )
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        return VideoProcessingResponse(
            success=False,
            error=str(e)
        )

# Download endpoint
@app.get("/api/edit/download/{filename}")
async def download_processed_video(filename: str):
    file_path = Path("processed") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Processed file not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='application/octet-stream'
    )

# Video file checking endpoint
@app.get("/api/videos/check/{filename}")
async def check_video_file(filename: str):
    """Check if a video file exists and return metadata"""
    try:
        file_path = Path("uploads") / filename
        
        if file_path.exists():
            file_stats = file_path.stat()
            return {
                "exists": True,
                "filename": filename,
                "size": file_stats.st_size,
                "path": str(file_path),
                "modified": file_stats.st_mtime
            }
        else:
            return {
                "exists": False,
                "filename": filename,
                "message": "File not found"
            }
            
    except Exception as e:
        logger.error(f"Error checking file {filename}: {str(e)}")
        return {
            "exists": False,
            "filename": filename,
            "error": str(e)
        }

# Sample video creation endpoint
@app.post("/api/videos/create-sample/{filename}")
async def create_sample_video(filename: str):
    """Create a sample video file for testing"""
    try:
        file_path = Path("uploads") / filename
        
        # Create a simple dummy file for testing
        with open(file_path, "wb") as f:
            # Write a small dummy video file header (just for testing)
            f.write(b"DUMMY_VIDEO_FILE_FOR_TESTING")
            f.write(b"\x00" * 1024)  # Pad with zeros
        
        logger.info(f"Created sample video: {filename}")
        
        return {
            "success": True,
            "filename": filename,
            "path": str(file_path),
            "size": file_path.stat().st_size,
            "message": "Sample video created"
        }
        
    except Exception as e:
        logger.error(f"Error creating sample video {filename}: {str(e)}")
        return {
            "success": False,
            "filename": filename,
            "error": str(e)
        }

# Get video list
@app.get("/api/videos")
async def get_videos():
    """Get list of uploaded videos"""
    try:
        uploads_dir = Path("uploads")
        videos = []
        
        if uploads_dir.exists():
            for file_path in uploads_dir.iterdir():
                if file_path.is_file():
                    videos.append({
                        "filename": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime
                    })
        
        return {"videos": videos}
        
    except Exception as e:
        logger.error(f"Error getting video list: {str(e)}")
        return {"videos": [], "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(
        "temp_backend:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
