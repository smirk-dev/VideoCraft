import json
import logging
import os
import uuid
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import random
import time

from fastapi import FastAPI, File, UploadFile, HTTPException, status, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Simple main without AI imports
app = FastAPI(title="VideoCraft Backend")

# Enable CORS for frontend communication  
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Setup directories
UPLOAD_DIR = Path("uploads")
TEMP_DIR = Path("temp") 
PROCESSED_DIR = Path("processed")

for directory in [UPLOAD_DIR, TEMP_DIR, PROCESSED_DIR]:
    directory.mkdir(exist_ok=True)

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
    message: Optional[str] = None

class RecommendationRequest(BaseModel):
    video_filename: str
    analysis_data: Optional[Dict[str, Any]] = None

class RecommendationResponse(BaseModel):
    success: bool
    recommendations: Dict[str, Any]

# In-memory storage for simplicity
analysis_storage = {}
recommendation_storage = {}

def generate_mock_analysis():
    """Generate realistic mock analysis data"""
    return {
        "video_info": {
            "duration": round(random.uniform(30, 300), 2),
            "fps": random.choice([24, 30, 60]),
            "resolution": random.choice(["1920x1080", "1280x720", "3840x2160"]),
            "format": "mp4",
            "size_mb": round(random.uniform(10, 500), 2)
        },
        "scene_analysis": {
            "total_scenes": random.randint(3, 12),
            "scene_changes": [
                {
                    "timestamp": round(random.uniform(0, 60), 2),
                    "confidence": round(random.uniform(0.7, 0.95), 2),
                    "scene_type": random.choice(["indoor", "outdoor", "transition", "close-up"])
                }
                for _ in range(random.randint(3, 8))
            ],
            "scene_types": ["indoor", "outdoor", "transition", "close-up"],
            "dominant_scene": random.choice(["indoor", "outdoor"])
        },
        "object_detection": {
            "detected_objects": [
                {
                    "object": obj,
                    "confidence": round(random.uniform(0.6, 0.95), 2),
                    "frequency": random.randint(1, 20),
                    "timestamps": [round(random.uniform(0, 60), 2) for _ in range(random.randint(1, 5))]
                }
                for obj in random.sample([
                    "person", "car", "building", "tree", "chair", "table", 
                    "laptop", "phone", "book", "cup", "dog", "cat"
                ], random.randint(3, 8))
            ]
        },
        "emotion_analysis": {
            "detected_emotions": [
                {
                    "emotion": emotion,
                    "confidence": round(random.uniform(0.5, 0.9), 2),
                    "timestamp": round(random.uniform(0, 60), 2),
                    "duration": round(random.uniform(1, 5), 2)
                }
                for emotion in random.sample([
                    "happy", "sad", "angry", "surprised", "neutral", "fear", "disgust"
                ], random.randint(2, 5))
            ],
            "dominant_emotion": random.choice(["happy", "neutral", "sad"]),
            "emotion_distribution": {
                "happy": round(random.uniform(0.1, 0.4), 2),
                "neutral": round(random.uniform(0.2, 0.5), 2),
                "sad": round(random.uniform(0.05, 0.2), 2),
                "angry": round(random.uniform(0.0, 0.1), 2),
                "surprised": round(random.uniform(0.05, 0.15), 2)
            }
        },
        "motion_analysis": {
            "motion_intensity": round(random.uniform(0.1, 0.9), 2),
            "camera_movements": [
                {
                    "type": movement,
                    "timestamp": round(random.uniform(0, 60), 2),
                    "intensity": round(random.uniform(0.3, 0.8), 2)
                }
                for movement in random.sample([
                    "pan_left", "pan_right", "tilt_up", "tilt_down", "zoom_in", "zoom_out", "static"
                ], random.randint(2, 4))
            ],
            "stabilization_needed": random.choice([True, False]),
            "average_motion": round(random.uniform(0.2, 0.7), 2)
        },
        "audio_analysis": {
            "has_speech": random.choice([True, False]),
            "music_detected": random.choice([True, False]),
            "noise_level": round(random.uniform(0.1, 0.6), 2),
            "dominant_frequency": random.randint(100, 8000),
            "audio_quality": random.choice(["excellent", "good", "fair", "poor"]),
            "segments": [
                {
                    "start": round(random.uniform(0, 30), 2),
                    "end": round(random.uniform(30, 60), 2),
                    "type": random.choice(["speech", "music", "silence", "noise"]),
                    "volume": round(random.uniform(0.3, 0.9), 2)
                }
                for _ in range(random.randint(2, 5))
            ]
        },
        "technical_quality": {
            "sharpness": round(random.uniform(0.6, 0.95), 2),
            "brightness": round(random.uniform(0.4, 0.8), 2),
            "contrast": round(random.uniform(0.5, 0.9), 2),
            "color_balance": round(random.uniform(0.6, 0.9), 2),
            "overall_quality": round(random.uniform(0.7, 0.95), 2),
            "issues": random.sample([
                "low_light", "overexposed", "blurry", "shaky", "poor_audio"
            ], random.randint(0, 2))
        }
    }

def generate_mock_recommendations(analysis_data=None):
    """Generate realistic editing recommendations"""
    return {
        "editing_suggestions": [
            {
                "type": "cut",
                "timestamp": round(random.uniform(5, 25), 2),
                "reason": "Scene transition detected",
                "confidence": round(random.uniform(0.7, 0.9), 2),
                "priority": random.choice(["high", "medium", "low"])
            },
            {
                "type": "trim",
                "start": round(random.uniform(0, 5), 2),
                "end": round(random.uniform(55, 60), 2),
                "reason": "Remove silent segments",
                "confidence": round(random.uniform(0.6, 0.8), 2),
                "priority": "medium"
            }
        ],
        "music_recommendations": [
            {
                "genre": genre,
                "mood": random.choice(["upbeat", "calm", "energetic", "melancholic"]),
                "tempo": random.choice(["slow", "medium", "fast"]),
                "timestamp": round(random.uniform(0, 30), 2),
                "duration": round(random.uniform(10, 30), 2),
                "confidence": round(random.uniform(0.6, 0.9), 2)
            }
            for genre in random.sample([
                "ambient", "pop", "electronic", "classical", "jazz", "rock"
            ], random.randint(2, 4))
        ],
        "color_grading": {
            "suggested_adjustments": [
                {
                    "parameter": param,
                    "adjustment": round(random.uniform(-20, 20), 1),
                    "reason": f"Improve {param.replace('_', ' ')}",
                    "timestamp_range": [
                        round(random.uniform(0, 20), 2),
                        round(random.uniform(20, 40), 2)
                    ]
                }
                for param in random.sample([
                    "brightness", "contrast", "saturation", "warmth", "highlights", "shadows"
                ], random.randint(2, 4))
            ],
            "overall_mood": random.choice(["warm", "cool", "neutral", "dramatic"]),
            "style_suggestion": random.choice(["cinematic", "natural", "vintage", "modern"])
        },
        "transitions": [
            {
                "type": transition,
                "timestamp": round(random.uniform(10, 50), 2),
                "duration": round(random.uniform(0.5, 2), 1),
                "reason": "Smooth scene change",
                "confidence": round(random.uniform(0.7, 0.9), 2)
            }
            for transition in random.sample([
                "fade", "dissolve", "cut", "wipe", "slide"
            ], random.randint(2, 4))
        ],
        "text_overlays": [
            {
                "text": text,
                "timestamp": round(random.uniform(0, 50), 2),
                "duration": round(random.uniform(2, 5), 1),
                "position": random.choice(["top", "bottom", "center", "lower_third"]),
                "style": random.choice(["bold", "elegant", "modern", "classic"])
            }
            for text in [
                "Scene Description",
                "Location: Indoor",
                "Key Moment",
                f"Duration: {random.randint(1, 5)} minutes"
            ][:random.randint(1, 3)]
        ],
        "overall_sentiment": {
            "mood": random.choice(["positive", "neutral", "negative", "mixed"]),
            "energy_level": random.choice(["high", "medium", "low"]),
            "recommended_style": random.choice(["dynamic", "calm", "dramatic", "playful"]),
            "target_audience": random.choice(["general", "professional", "creative", "educational"])
        }
    }

@app.get("/")
async def root():
    return {"message": "VideoCraft Backend API", "version": "1.0.0", "ai_enabled": False}

@app.post("/upload", response_model=Dict[str, Any])
async def upload_video(file: UploadFile = File(...)):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Get file info
        file_stats = file_path.stat()
        
        return {
            "success": True,
            "filename": unique_filename,
            "original_filename": file.filename,
            "size": file_stats.st_size,
            "upload_time": datetime.now().isoformat(),
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/analyze/{filename}", response_model=AnalysisResponse)
async def analyze_video_filename(filename: str, request: AnalysisRequest):
    try:
        logger.info(f"Starting analysis for video: {filename}")
        
        # Check if file exists
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Simulate analysis processing time
        await asyncio.sleep(random.uniform(1, 3))
        
        # Generate mock analysis (since AI is not available)
        analysis_result = generate_mock_analysis()
        
        # Store analysis
        analysis_storage[analysis_id] = {
            "video_filename": filename,
            "analysis": analysis_result,
            "timestamp": datetime.now().isoformat(),
            "analysis_types": request.analysis_types
        }
        
        logger.info(f"Analysis completed for {filename}")
        
        return AnalysisResponse(
            success=True,
            analysis_id=analysis_id,
            analysis=analysis_result,
            message="Analysis completed successfully (simulation mode)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/recommendations/{filename}", response_model=RecommendationResponse)
async def get_recommendations(filename: str, request: RecommendationRequest):
    try:
        logger.info(f"Generating recommendations for video: {filename}")
        
        # Check if file exists
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # Simulate processing time
        await asyncio.sleep(random.uniform(1, 2))
        
        # Generate recommendations (simulation mode)
        recommendations = generate_mock_recommendations(request.analysis_data)
        
        # Store recommendations
        recommendation_id = str(uuid.uuid4())
        recommendation_storage[recommendation_id] = {
            "video_filename": filename,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Recommendations generated for {filename}")
        
        return RecommendationResponse(
            success=True,
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recommendation generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {str(e)}")

@app.get("/video/{filename}")
async def get_video(filename: str):
    try:
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = "video/mp4"
        
        return FileResponse(
            path=str(file_path),
            media_type=mime_type,
            filename=filename
        )
    except Exception as e:
        logger.error(f"Video retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video retrieval failed: {str(e)}")

@app.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    try:
        if analysis_id not in analysis_storage:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return analysis_storage[analysis_id]
    except Exception as e:
        logger.error(f"Analysis retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis retrieval failed: {str(e)}")

# Export endpoints
@app.get("/test-export")
async def test_export():
    return {"message": "Export endpoints are working!", "success": True}

class ExportRequest(BaseModel):
    video_filename: str
    export_type: str  # 'video', 'report', 'data', 'analysis'
    editing_data: Optional[Dict[str, Any]] = {}
    quality: Optional[str] = '720p'

@app.post("/export/video")
async def export_video(request: ExportRequest):
    try:
        logger.info(f"Video export requested for: {request.video_filename}")
        
        # Check if video file exists
        file_path = UPLOAD_DIR / request.video_filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # For now, just return the original file
        # In a real implementation, you would apply editing here
        return {
            "success": True,
            "message": "Video export prepared",
            "download_url": f"/video/{request.video_filename}",
            "filename": f"exported_{request.video_filename}",
            "editing_applied": len(request.editing_data or {}) > 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video export failed: {str(e)}")

@app.post("/export/report")
async def export_report(request: ExportRequest):
    try:
        logger.info(f"Report export requested for: {request.video_filename}")
        
        # Generate report data
        report_data = {
            "video_name": request.video_filename,
            "export_date": datetime.now().isoformat(),
            "editing_summary": request.editing_data,
            "analysis_summary": "Comprehensive video analysis completed",
            "recommendations": generate_mock_recommendations().get("editing_suggestions", [])
        }
        
        return {
            "success": True,
            "message": "Report data generated",
            "report_data": report_data,
            "filename": f"report_{request.video_filename.replace('.mp4', '')}.json"
        }
        
    except Exception as e:
        logger.error(f"Report export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report export failed: {str(e)}")

@app.post("/export/analysis")
async def export_analysis(request: ExportRequest):
    try:
        logger.info(f"Analysis export requested for: {request.video_filename}")
        
        # Generate analysis export data
        analysis_data = generate_mock_analysis()
        analysis_export = {
            "video_info": {
                "filename": request.video_filename,
                "export_date": datetime.now().isoformat()
            },
            "analysis_results": analysis_data,
            "export_type": "comprehensive_analysis"
        }
        
        return {
            "success": True,
            "message": "Analysis data prepared for export",
            "analysis_data": analysis_export,
            "filename": f"analysis_{request.video_filename.replace('.mp4', '')}.json"
        }
        
    except Exception as e:
        logger.error(f"Analysis export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis export failed: {str(e)}")

@app.post("/export/data")
async def export_project_data(request: ExportRequest):
    try:
        logger.info(f"Project data export requested for: {request.video_filename}")
        
        # Generate project data
        project_data = {
            "project_info": {
                "video_filename": request.video_filename,
                "created_date": datetime.now().isoformat(),
                "export_date": datetime.now().isoformat(),
                "version": "1.0"
            },
            "editing_data": request.editing_data,
            "settings": {
                "quality": request.quality,
                "format": "mp4"
            }
        }
        
        return {
            "success": True,
            "message": "Project data prepared for export",
            "project_data": project_data,
            "filename": f"project_{request.video_filename.replace('.mp4', '')}.json"
        }
        
    except Exception as e:
        logger.error(f"Project data export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Project data export failed: {str(e)}")

@app.get("/export/download/{filename}")
async def download_export(filename: str):
    try:
        # Check in uploads directory first
        file_path = UPLOAD_DIR / filename
        if file_path.exists():
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                mime_type = "application/octet-stream"
            
            return FileResponse(
                path=str(file_path),
                media_type=mime_type,
                filename=f"exported_{filename}"
            )
        
        # Check in processed directory
        file_path = PROCESSED_DIR / filename
        if file_path.exists():
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                mime_type = "application/octet-stream"
            
            return FileResponse(
                path=str(file_path),
                media_type=mime_type,
                filename=filename
            )
        
        raise HTTPException(status_code=404, detail="Export file not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

if __name__ == "__main__":
    import asyncio
    import uvicorn
    
    print("🚀 Starting VideoCraft Backend (Simulation Mode)")
    print(f"📁 Upload directory: {UPLOAD_DIR.absolute()}")
    print(f"📁 Temp directory: {TEMP_DIR.absolute()}")
    print(f"📁 Processed directory: {PROCESSED_DIR.absolute()}")
    
    uvicorn.run(
        "simple_main_backup:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
