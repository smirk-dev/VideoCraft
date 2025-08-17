"""
Simple test server for 2GB upload functionality
"""
import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import aiofiles

app = FastAPI(title="VideoCraft Upload Test Server")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2GB upload limit
MAX_UPLOAD_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

@app.post("/api/upload/video")
async def upload_video(file: UploadFile = File(...)):
    """Test upload endpoint for large files"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file size
    if file.size and file.size > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size: {MAX_UPLOAD_SIZE / (1024*1024*1024):.1f}GB"
        )
    
    try:
        # Create uploads directory
        os.makedirs("uploads", exist_ok=True)
        
        # Save file with larger chunks for performance
        file_path = f"uploads/{file.filename}"
        async with aiofiles.open(file_path, 'wb') as f:
            chunk_size = 1024 * 1024  # 1MB chunks
            while chunk := await file.read(chunk_size):
                await f.write(chunk)
        
        return JSONResponse(
            status_code=201,
            content={
                "message": "Video uploaded successfully",
                "data": {
                    "filename": file.filename,
                    "file_size": os.path.getsize(file_path),
                    "status": "uploaded"
                }
            }
        )
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error uploading video")

@app.get("/")
async def root():
    return {"message": "VideoCraft Upload Test Server - 2GB limit enabled"}

@app.get("/health")
async def health():
    return {"status": "healthy", "max_upload_size": f"{MAX_UPLOAD_SIZE / (1024*1024*1024):.1f}GB"}

if __name__ == "__main__":
    uvicorn.run(
        "test_upload_server:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info",
        # Configuration for large file uploads
        timeout_keep_alive=120,  # 2 minutes
        limit_max_requests=1000,
        backlog=2048
    )
