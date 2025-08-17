"""
VideoCraft AI Video Editor - Main FastAPI Application
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from app.api import upload
# Temporarily commenting out AI-dependent imports for initial setup
# from app.api import video_analysis, audio_analysis, emotion_detection
# from app.api import music_recommendation, background_removal, video_editing
from app.core.config import settings
from app.core.logging_config import setup_logging


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting VideoCraft AI Video Editor...")
    
    # Create necessary directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("processed", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    # Initialize AI models (lazy loading for better startup time)
    logger.info("📦 AI models will be loaded on first use...")
    
    yield
    
    logger.info("🔄 Shutting down VideoCraft...")


# Create FastAPI app
app = FastAPI(
    title="VideoCraft AI Video Editor",
    description="Comprehensive AI-powered video editing platform with intelligent analysis and recommendations",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
# Temporarily commenting out AI-dependent routers for initial setup
# app.include_router(video_analysis.router, prefix="/api/analyze", tags=["video-analysis"])
# app.include_router(audio_analysis.router, prefix="/api/audio", tags=["audio-analysis"])
# app.include_router(emotion_detection.router, prefix="/api/emotion", tags=["emotion-detection"])
# app.include_router(music_recommendation.router, prefix="/api/music", tags=["music-recommendation"])
# app.include_router(background_removal.router, prefix="/api/background", tags=["background-removal"])
# app.include_router(video_editing.router, prefix="/api/edit", tags=["video-editing"])

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/processed", StaticFiles(directory="processed"), name="processed")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>VideoCraft AI Video Editor</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            .feature { margin: 10px 0; padding: 10px; background: #ecf0f1; border-radius: 5px; }
            .api-link { color: #3498db; text-decoration: none; }
            .api-link:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 VideoCraft AI Video Editor</h1>
            <p>Welcome to the AI-powered video editing platform!</p>
            
            <h2>🚀 Features</h2>
            <div class="feature">🤖 AI-powered video analysis and scene detection</div>
            <div class="feature">😊 Real-time emotion detection and sentiment analysis</div>
            <div class="feature">🎵 Intelligent music recommendation based on content</div>
            <div class="feature">🖼️ Advanced background removal and replacement</div>
            <div class="feature">✂️ Smart cut suggestions and automated editing</div>
            <div class="feature">🗣️ Audio transcription and analysis</div>
            
            <h2>📚 API Documentation</h2>
            <p><a href="/api/docs" class="api-link">Interactive API Documentation (Swagger)</a></p>
            <p><a href="/api/redoc" class="api-link">Alternative API Documentation (ReDoc)</a></p>
            
            <h2>🔧 Quick Start</h2>
            <p>1. Upload a video file using <code>POST /api/upload/video</code></p>
            <p>2. Analyze the video with <code>POST /api/analyze/video</code></p>
            <p>3. Get AI recommendations and suggestions</p>
            <p>4. Apply edits and enhancements</p>
            <p>5. Download your processed video</p>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "VideoCraft AI Video Editor",
        "version": "1.0.0"
    }


@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "VideoCraft AI Video Editor API",
        "version": "1.0.0",
        "description": "Comprehensive AI-powered video editing platform",
        "features": [
            "Video content analysis",
            "Emotion detection",
            "Audio processing and transcription",
            "Music recommendation",
            "Background removal",
            "Intelligent video editing",
            "Scene detection",
            "Script analysis"
        ],
        "endpoints": {
            "upload": "/api/upload/*",
            "video_analysis": "/api/analyze/*",
            "audio_analysis": "/api/audio/*",
            "emotion_detection": "/api/emotion/*",
            "music_recommendation": "/api/music/*",
            "background_removal": "/api/background/*",
            "video_editing": "/api/edit/*"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )
