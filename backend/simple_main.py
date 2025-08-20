"""
Simplified VideoCraft backend for testing frontend functionality
This version avoids heavy AI dependencies while providing working endpoints
"""
import os
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import random
import time
from datetime import datetime

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple models
class AnalysisRequest(BaseModel):
    video_filename: str
    analysis_types: Optional[List[str]] = ['objects', 'scenes', 'emotions', 'motion']
    project_id: Optional[str] = None

class AnalysisResponse(BaseModel):
    success: bool
    analysis_id: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting VideoCraft Simple Backend...")
    
    # Create necessary directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("processed", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    yield
    logger.info("🔄 Shutting down VideoCraft...")

# Create FastAPI app
app = FastAPI(
    title="VideoCraft AI Video Editor (Simple)",
    description="Simplified video editing platform for testing",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002", "http://127.0.0.1:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_dynamic_analysis(video_filename: str) -> Dict[str, Any]:
    """Generate dynamic analysis based on video filename and current time"""
    
    # Use filename and timestamp to create semi-realistic variations
    seed = hash(video_filename + str(int(time.time() / 3600)))  # Changes every hour
    random.seed(seed)
    
    # Dynamic object detection
    object_categories = [
        {'person': 15, 'face': 8, 'hand': 12},
        {'car': 10, 'road': 20, 'traffic_light': 5},
        {'building': 25, 'window': 18, 'door': 7},
        {'tree': 30, 'grass': 15, 'sky': 10},
        {'computer': 8, 'keyboard': 5, 'screen': 3},
        {'food': 12, 'table': 6, 'plate': 9}
    ]
    
    selected_objects = random.choice(object_categories)
    
    # Dynamic scene analysis  
    scene_categories = [
        {'outdoor': 25, 'nature': 15},
        {'indoor': 30, 'room': 20},
        {'urban': 22, 'street': 18},
        {'office': 28, 'workplace': 12},
        {'kitchen': 20, 'cooking': 15}
    ]
    
    selected_scenes = random.choice(scene_categories)
    
    # Dynamic emotions
    emotion_sets = [
        {'joy': 0.7, 'excitement': 0.2, 'surprise': 0.1},
        {'neutral': 0.6, 'calm': 0.3, 'peaceful': 0.1},
        {'focused': 0.5, 'concentration': 0.3, 'determined': 0.2},
        {'happy': 0.6, 'satisfied': 0.25, 'content': 0.15}
    ]
    
    selected_emotions = random.choice(emotion_sets)
    dominant_emotion = max(selected_emotions.items(), key=lambda x: x[1])
    
    # Dynamic motion analysis
    motion_intensities = ['low', 'moderate', 'high', 'dynamic', 'static']
    camera_movements = ['minimal', 'detected', 'significant', 'smooth', 'shaky']
    
    motion_intensity = random.uniform(5.0, 25.0)
    motion_type = random.choice(motion_intensities)
    camera_movement = random.choice(camera_movements)
    
    # File-based insights
    filename_lower = video_filename.lower()
    insights = [
        f"Analysis completed for {video_filename}",
        f"Processing time: {random.uniform(2.5, 8.7):.2f} seconds",
        f"Analyzed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ]
    
    if 'outdoor' in filename_lower or 'nature' in filename_lower:
        insights.append("Outdoor scene detected based on filename analysis")
    elif 'indoor' in filename_lower or 'room' in filename_lower:
        insights.append("Indoor environment identified")
    
    if 'meeting' in filename_lower or 'presentation' in filename_lower:
        insights.append("Professional content detected")
    
    return {
        'object_detection': {
            'detected_objects': selected_objects,
            'total_unique_objects': len(selected_objects),
            'most_common_object': max(selected_objects.items(), key=lambda x: x[1])[0],
            'average_objects_per_frame': sum(selected_objects.values()) / len(selected_objects)
        },
        'scene_analysis': {
            'scene_types': selected_scenes,
            'dominant_scene': max(selected_scenes.items(), key=lambda x: x[1])[0],
            'scene_confidence': round(random.uniform(0.75, 0.95), 2),
            'scene_transitions': random.randint(2, 6)
        },
        'emotion_analysis': {
            'emotion_scores': selected_emotions,
            'dominant_emotion': dominant_emotion[0],
            'emotion_confidence': dominant_emotion[1],
            'emotional_intensity': round(random.uniform(0.3, 0.8), 2)
        },
        'motion_analysis': {
            'motion_intensity': round(motion_intensity, 1),
            'motion_type': motion_type,
            'camera_movement': camera_movement
        },
        'insights': insights,
        'processing_time_seconds': round(random.uniform(3.2, 9.8), 2),
        'analysis_timestamp': datetime.now().isoformat(),
        'total_frames_analyzed': random.randint(25, 45)
    }

@app.get("/")
async def root():
    return {"message": "VideoCraft Simple Backend is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "VideoCraft Simple Backend"}

@app.get("/api/health")
async def api_health_check():
    """API health check for frontend connectivity"""
    return {
        "status": "healthy", 
        "service": "VideoCraft Simple Backend",
        "api_version": "1.0.0",
        "endpoints_available": True,
        "cors_enabled": True
    }

@app.post("/api/analyze/analyze-real", response_model=AnalysisResponse)
async def analyze_video_real(request: AnalysisRequest):
    """Perform dynamic analysis on video"""
    try:
        logger.info(f"Analyzing video: {request.video_filename}")
        
        # Simulate processing time
        await asyncio.sleep(random.uniform(1.0, 3.0))
        
        # Generate dynamic analysis
        analysis_result = generate_dynamic_analysis(request.video_filename)
        
        return AnalysisResponse(
            success=True,
            analysis_id=f"analysis_{int(time.time())}",
            analysis=analysis_result
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return AnalysisResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/analyze/analyze-filename")
async def analyze_video_filename(request: dict):
    """Perform dynamic analysis on video by filename"""
    try:
        filename = request.get("filename", "unknown.mp4")
        logger.info(f"Analyzing video by filename: {filename}")
        
        # Simulate processing time
        await asyncio.sleep(random.uniform(1.0, 3.0))
        
        # Generate dynamic analysis
        analysis_result = generate_dynamic_analysis(filename)
        
        return {
            "success": True,
            "analysis_id": f"analysis_{int(time.time())}",
            "analysis": analysis_result
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import sys
    
    # Handle command line arguments for port
    port = 8001
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            if "--port" in sys.argv:
                try:
                    port = int(sys.argv[sys.argv.index("--port") + 1])
                except (IndexError, ValueError):
                    pass
    
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
