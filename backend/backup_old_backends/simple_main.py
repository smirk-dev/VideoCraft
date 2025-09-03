"""
Simplified VideoCraft backend for testing frontend functionality
Now with Real AI Integration using multiple models
"""
import os
import logging
import asyncio
import time
import random
from datetime import datetime
from typing import Dict, Any, List
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

# Import real AI services with better error handling
AI_AVAILABLE = False
get_ai_analysis = None
generate_ai_recommendations = None
ai_service = None

try:
    # Try importing AI services
    import sys
    import importlib.util
    
    spec = importlib.util.spec_from_file_location("ai_services", "ai_services.py")
    if spec and spec.loader:
        ai_services = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ai_services)
        
        get_ai_analysis = ai_services.get_ai_analysis
        generate_ai_recommendations = ai_services.generate_ai_recommendations
        ai_service = ai_services.ai_service
        AI_AVAILABLE = True
        print("✅ Real AI services loaded successfully")
    else:
        raise ImportError("Could not find ai_services module")
        
except Exception as e:
    AI_AVAILABLE = False
    print(f"⚠️ AI services not available: {e}")
    print("Using fallback simulation mode")
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
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
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
    """Perform AI analysis on video by filename"""
    try:
        filename = request.get("filename", "unknown.mp4")
        logger.info(f"🔍 Analyzing video: {filename}")
        
        # Check if we have a real video file to analyze
        video_path = None
        possible_paths = [
            os.path.join("uploads", filename),
            os.path.join("temp", filename),
            os.path.join("..", "uploads", filename),
            filename  # Direct path
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                video_path = path
                break
        
        if AI_AVAILABLE and get_ai_analysis and video_path and os.path.exists(video_path):
            # Use real AI analysis
            logger.info(f"🤖 Using REAL AI analysis on: {video_path}")
            
            try:
                # Get comprehensive AI analysis
                ai_analysis = await get_ai_analysis(video_path)
                
                # Convert AI analysis to expected format
                analysis_result = {
                    'object_detection': {
                        'detected_objects': {obj['object']: obj['count'] for obj in ai_analysis.objects},
                        'total_unique_objects': len(ai_analysis.objects),
                        'most_common_object': ai_analysis.objects[0]['object'] if ai_analysis.objects else 'Unknown',
                        'confidence_scores': {obj['object']: obj['confidence'] for obj in ai_analysis.objects}
                    },
                    'scene_analysis': {
                        'scene_types': {scene['scene']: i+1 for i, scene in enumerate(ai_analysis.scenes)},
                        'scene_confidence': ai_analysis.scenes[0]['confidence'] if ai_analysis.scenes else 0.5,
                        'scene_transitions': len(ai_analysis.scenes)
                    },
                    'emotion_analysis': {
                        'emotion_scores': {emotion['emotion']: emotion['confidence'] for emotion in ai_analysis.emotions},
                        'dominant_emotion': ai_analysis.emotions[0]['emotion'] if ai_analysis.emotions else 'Neutral',
                        'emotion_confidence': ai_analysis.emotions[0]['confidence'] if ai_analysis.emotions else 0.5,
                        'emotional_timeline': ai_analysis.emotions
                    },
                    'motion_analysis': {
                        'motion_intensity': ai_analysis.motion_analysis.get('average_motion', 3.0),
                        'motion_type': ai_analysis.motion_analysis.get('motion_type', 'medium'),
                        'camera_movement': ai_analysis.motion_analysis.get('camera_stability', 'stable')
                    },
                    'audio_analysis': {
                        'tempo': ai_analysis.audio_features.get('tempo', 120),
                        'has_music': ai_analysis.audio_features.get('has_music', False),
                        'is_speech_heavy': ai_analysis.audio_features.get('is_speech_heavy', False),
                        'energy_level': ai_analysis.audio_features.get('energy_mean', 0.5),
                        'audio_quality': 'high' if ai_analysis.audio_features.get('dynamic_range', 0.5) > 0.3 else 'medium'
                    },
                    'sentiment_analysis': ai_analysis.sentiment,
                    'technical_quality': ai_analysis.technical_quality,
                    'ai_insights': [
                        f"Real AI detected {len(ai_analysis.objects)} object types",
                        f"Emotional tone: {ai_analysis.sentiment.get('overall_sentiment', 'Unknown')}",
                        f"Motion level: {ai_analysis.motion_analysis.get('motion_type', 'Unknown')}",
                        f"Quality: {ai_analysis.technical_quality.get('quality_rating', 'Unknown')}"
                    ],
                    'processing_info': {
                        'ai_models_used': True,
                        'analysis_type': 'real_ai',
                        'models': ['FER', 'MediaPipe', 'Librosa', 'OpenCV', 'Transformers']
                    }
                }
                
                logger.info("✅ Real AI analysis completed successfully")
                
            except Exception as ai_error:
                logger.error(f"❌ Real AI analysis failed: {ai_error}")
                # Fallback to simulation
                analysis_result = generate_dynamic_analysis(filename)
                analysis_result['processing_info'] = {
                    'ai_models_used': False,
                    'analysis_type': 'simulation_fallback',
                    'ai_error': str(ai_error)
                }
        else:
            # Use simulation analysis
            if not AI_AVAILABLE:
                logger.info(f"🎭 Using SIMULATION analysis (AI not available): {filename}")
            else:
                logger.info(f"🎭 Using SIMULATION analysis (file not found): {filename}")
            
            analysis_result = generate_dynamic_analysis(filename)
            analysis_result['processing_info'] = {
                'ai_models_used': False,
                'analysis_type': 'simulation',
                'reason': 'AI models not available' if not AI_AVAILABLE else 'Video file not found'
            }
        
        # Simulate processing time
        await asyncio.sleep(random.uniform(1.0, 2.5))
        
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

# Project management endpoints
projects_storage = []  # In-memory storage for demo purposes

@app.post("/api/projects/save")
async def save_project(request: dict):
    """Save a video editing project"""
    try:
        project_data = {
            "id": request.get("id") or f"project_{int(time.time())}_{random.randint(1000, 9999)}",
            "name": request.get("name", "Untitled Project"),
            "description": request.get("description", ""),
            "video_filename": request.get("video_filename"),
            "video_metadata": request.get("video_metadata", {}),
            "editing_data": request.get("editing_data", {}),
            "date_created": request.get("date_created") or datetime.now().isoformat(),
            "date_modified": datetime.now().isoformat(),
            "status": request.get("status", "draft"),
            "thumbnail": request.get("thumbnail", "/api/placeholder/320/180"),
            "duration": request.get("duration", "0:00"),
            "file_size": request.get("file_size", "0 MB"),
            "clips": request.get("clips", 1)
        }
        
        # Check if project already exists (update vs create)
        existing_index = next((i for i, p in enumerate(projects_storage) if p["id"] == project_data["id"]), None)
        
        if existing_index is not None:
            # Update existing project
            projects_storage[existing_index] = project_data
            logger.info(f"Updated project: {project_data['name']}")
        else:
            # Create new project
            projects_storage.insert(0, project_data)  # Add to beginning for recent-first order
            logger.info(f"Created new project: {project_data['name']}")
        
        return {
            "success": True,
            "project_id": project_data["id"],
            "message": "Project saved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to save project: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/projects/list")
async def list_projects():
    """Get all saved projects"""
    try:
        return {
            "success": True,
            "projects": projects_storage
        }
    except Exception as e:
        logger.error(f"Failed to list projects: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get a specific project by ID"""
    try:
        project = next((p for p in projects_storage if p["id"] == project_id), None)
        if project:
            return {
                "success": True,
                "project": project
            }
        else:
            return {
                "success": False,
                "error": "Project not found"
            }
    except Exception as e:
        logger.error(f"Failed to get project: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project by ID"""
    try:
        global projects_storage
        original_length = len(projects_storage)
        projects_storage = [p for p in projects_storage if p["id"] != project_id]
        
        if len(projects_storage) < original_length:
            logger.info(f"Deleted project: {project_id}")
            return {
                "success": True,
                "message": "Project deleted successfully"
            }
        else:
            return {
                "success": False,
                "error": "Project not found"
            }
    except Exception as e:
        logger.error(f"Failed to delete project: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# AI Recommendations endpoint
@app.post("/api/recommendations/generate")
async def generate_recommendations(request: dict):
    """Generate AI-powered editing recommendations"""
    try:
        filename = request.get("filename", "unknown.mp4")
        metadata = request.get("metadata", {})
        
        logger.info(f"🎯 Generating recommendations for: {filename}")
        
        # Check if we have a real video file to analyze
        video_path = None
        possible_paths = [
            os.path.join("uploads", filename),
            os.path.join("temp", filename),
            os.path.join("..", "uploads", filename),
            filename
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                video_path = path
                break
        
        if AI_AVAILABLE and get_ai_analysis and generate_ai_recommendations and video_path and os.path.exists(video_path):
            # Use real AI recommendations
            logger.info(f"🤖 Using REAL AI recommendations on: {video_path}")
            
            try:
                # Get AI analysis first
                ai_analysis = await get_ai_analysis(video_path)
                
                # Generate AI recommendations
                duration = metadata.get('duration', ai_analysis.technical_quality.get('duration_seconds', 120))
                ai_recommendations = await generate_ai_recommendations(ai_analysis, duration)
                
                # Convert to expected format
                recommendations = {
                    'cut_suggestions': [
                        {
                            'timestamp': rec.timestamp,
                            'confidence': rec.confidence,
                            'reason': rec.reasoning,
                            'type': rec.category
                        }
                        for rec in ai_recommendations if rec.type == 'cut'
                    ],
                    'music_recommendations': [
                        {
                            'genre': rec.implementation.get('type', 'ambient'),
                            'mood': rec.category,
                            'confidence': rec.confidence,
                            'reasoning': rec.reasoning,
                            'timestamp': rec.timestamp
                        }
                        for rec in ai_recommendations if rec.type == 'music'
                    ],
                    'effects_suggestions': [
                        {
                            'effect_type': rec.implementation.get('action', 'filter'),
                            'confidence': rec.confidence,
                            'description': rec.description,
                            'category': rec.category,
                            'parameters': rec.implementation
                        }
                        for rec in ai_recommendations if rec.type == 'effect'
                    ],
                    'transition_suggestions': [
                        {
                            'timestamp': rec.timestamp,
                            'type': rec.implementation.get('type', 'fade'),
                            'confidence': rec.confidence,
                            'reasoning': rec.reasoning
                        }
                        for rec in ai_recommendations if rec.type == 'transition'
                    ],
                    'sentiment_analysis': ai_analysis.sentiment,
                    'overall_recommendations': [rec.description for rec in ai_recommendations[:5]],
                    'ai_insights': [
                        f"Analyzed with {len(ai_analysis.emotions)} emotion detections",
                        f"Found {len(ai_analysis.objects)} object types",
                        f"Overall sentiment: {ai_analysis.sentiment.get('overall_sentiment', 'Unknown')}",
                        f"Quality rating: {ai_analysis.technical_quality.get('quality_rating', 'Unknown')}"
                    ],
                    'processing_info': {
                        'ai_models_used': True,
                        'analysis_type': 'real_ai_recommendations',
                        'recommendations_count': len(ai_recommendations)
                    }
                }
                
                logger.info(f"✅ Generated {len(ai_recommendations)} real AI recommendations")
                
            except Exception as ai_error:
                logger.error(f"❌ Real AI recommendations failed: {ai_error}")
                # Fallback to simulation
                recommendations = generate_dynamic_recommendations(filename, metadata)
                recommendations['processing_info'] = {
                    'ai_models_used': False,
                    'analysis_type': 'simulation_fallback',
                    'ai_error': str(ai_error)
                }
        else:
            # Use simulation recommendations
            if not AI_AVAILABLE:
                logger.info(f"🎭 Using SIMULATION recommendations (AI not available): {filename}")
            else:
                logger.info(f"🎭 Using SIMULATION recommendations (file not found): {filename}")
                
            recommendations = generate_dynamic_recommendations(filename, metadata)
            recommendations['processing_info'] = {
                'ai_models_used': False,
                'analysis_type': 'simulation',
                'reason': 'AI models not available' if not AI_AVAILABLE else 'Video file not found'
            }
        
        # Simulate processing time
        await asyncio.sleep(random.uniform(1.5, 3.0))
        
        return {
            "success": True,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Recommendations generation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def generate_dynamic_recommendations(filename: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Generate AI recommendations based on video filename and metadata"""
    
    # Use filename and metadata to create intelligent recommendations
    filename_lower = filename.lower()
    duration = metadata.get('duration', 120)  # Default 2 minutes
    
    # Analyze content type from filename
    is_tutorial = any(word in filename_lower for word in ['tutorial', 'howto', 'guide', 'learn'])
    is_vlog = any(word in filename_lower for word in ['vlog', 'day', 'life', 'routine'])
    is_music = any(word in filename_lower for word in ['music', 'song', 'beat', 'audio'])
    is_nature = any(word in filename_lower for word in ['nature', 'outdoor', 'landscape', 'beach'])
    is_event = any(word in filename_lower for word in ['wedding', 'party', 'celebration', 'event'])
    
    # Base sentiment analysis
    sentiment_score = 0.5
    sentiment_type = 'neutral'
    
    if any(word in filename_lower for word in ['happy', 'fun', 'joy', 'celebration', 'success']):
        sentiment_score = random.uniform(0.7, 0.9)
        sentiment_type = 'positive'
    elif any(word in filename_lower for word in ['sad', 'serious', 'documentary', 'news']):
        sentiment_score = random.uniform(0.2, 0.5)
        sentiment_type = 'negative'
    else:
        sentiment_score = random.uniform(0.4, 0.8)
        sentiment_type = random.choice(['positive', 'neutral'])
    
    # Generate cut recommendations
    cuts = []
    num_cuts = min(4, max(1, int(duration / 30)))  # Roughly one cut per 30 seconds
    
    for i in range(num_cuts):
        cut_time = random.uniform(10, duration - 10)
        cut_types = ['scene_change', 'audio_silence', 'engagement', 'transition']
        cut_type = random.choice(cut_types)
        
        cuts.append({
            'id': f'cut_{i+1}',
            'timestamp': f"{int(cut_time//60)}:{int(cut_time%60):02d}",
            'reason': get_cut_reason(cut_type, is_tutorial, is_vlog),
            'confidence': random.uniform(0.6, 0.95),
            'type': cut_type,
            'description': get_cut_description(cut_type, filename_lower)
        })
    
    # Generate music recommendations
    music_recs = []
    if duration > 30:
        if is_tutorial:
            music_recs = [
                {
                    'id': 'music_1',
                    'genre': 'Corporate',
                    'mood': 'Professional',
                    'start_time': '0:00',
                    'end_time': f"{int(duration//60)}:{int(duration%60):02d}",
                    'confidence': 0.87,
                    'description': 'Subtle background music for educational content',
                    'suggested_tracks': ['Corporate Inspire', 'Learning Flow', 'Focus Background']
                }
            ]
        elif is_nature:
            music_recs = [
                {
                    'id': 'music_1',
                    'genre': 'Ambient Nature',
                    'mood': 'Peaceful',
                    'start_time': '0:00',
                    'end_time': f"{int(duration//60)}:{int(duration%60):02d}",
                    'confidence': 0.92,
                    'description': 'Natural ambient sounds to enhance outdoor footage',
                    'suggested_tracks': ['Forest Sounds', 'Ocean Waves', 'Mountain Breeze']
                }
            ]
        elif is_event:
            music_recs = [
                {
                    'id': 'music_1',
                    'genre': 'Upbeat Pop',
                    'mood': 'Celebratory',
                    'start_time': '0:00',
                    'end_time': f"{int(duration//2//60)}:{int(duration//2%60):02d}",
                    'confidence': 0.89,
                    'description': 'Energetic music for event highlights',
                    'suggested_tracks': ['Celebration Time', 'Happy Moments', 'Joyful Vibes']
                },
                {
                    'id': 'music_2',
                    'genre': 'Emotional',
                    'mood': 'Heartfelt',
                    'start_time': f"{int(duration//2//60)}:{int(duration//2%60):02d}",
                    'end_time': f"{int(duration//60)}:{int(duration%60):02d}",
                    'confidence': 0.85,
                    'description': 'Emotional music for touching moments',
                    'suggested_tracks': ['Heartstrings', 'Tender Moments', 'Memories']
                }
            ]
        else:
            music_recs = [
                {
                    'id': 'music_1',
                    'genre': 'Electronic',
                    'mood': 'Dynamic',
                    'start_time': '0:00',
                    'end_time': f"{int(duration//60)}:{int(duration%60):02d}",
                    'confidence': 0.78,
                    'description': 'Modern electronic music to enhance visual content',
                    'suggested_tracks': ['Digital Pulse', 'Modern Beat', 'Tech Vibes']
                }
            ]
    
    # Generate filter recommendations
    filters = []
    if is_nature:
        filters.extend([
            {
                'id': 'filter_1',
                'name': 'Nature Enhancement',
                'type': 'color_correction',
                'confidence': 0.91,
                'description': 'Enhance natural colors and increase vibrancy',
                'settings': {'saturation': 1.2, 'vibrance': 1.15}
            },
            {
                'id': 'filter_2',
                'name': 'Golden Hour',
                'type': 'color_grading',
                'confidence': 0.83,
                'description': 'Warm color grading for cinematic outdoor look',
                'settings': {'temperature': 300, 'tint': 10}
            }
        ])
    elif is_tutorial:
        filters.extend([
            {
                'id': 'filter_1',
                'name': 'Clarity Boost',
                'type': 'sharpening',
                'confidence': 0.88,
                'description': 'Increase clarity for better text and detail visibility',
                'settings': {'sharpen': 1.3, 'clarity': 1.2}
            }
        ])
    else:
        filters.extend([
            {
                'id': 'filter_1',
                'name': 'Auto Color Correction',
                'type': 'color_correction',
                'confidence': 0.76,
                'description': 'Automatic color and exposure correction',
                'settings': {'auto_color': True, 'auto_exposure': True}
            }
        ])
    
    # Generate emotional peaks
    emotional_peaks = []
    for i in range(random.randint(2, 4)):
        peak_time = random.uniform(15, duration - 15)
        emotions = ['excitement', 'surprise', 'satisfaction', 'curiosity', 'anticipation']
        if sentiment_type == 'positive':
            emotions = ['excitement', 'joy', 'satisfaction', 'amazement']
        elif sentiment_type == 'negative':
            emotions = ['concern', 'tension', 'sadness', 'empathy']
        
        emotional_peaks.append({
            'timestamp': f"{int(peak_time//60)}:{int(peak_time%60):02d}",
            'emotion': random.choice(emotions),
            'intensity': random.uniform(0.6, 0.95)
        })
    
    # Calculate overall score
    overall_score = int(random.uniform(65, 92))
    if is_tutorial or is_nature:
        overall_score = int(random.uniform(75, 95))
    
    return {
        'overall_score': overall_score,
        'sentiment': sentiment_type,
        'editing_recommendations': {
            'cuts': cuts,
            'music': music_recs,
            'filters': filters,
            'pacing': {
                'overall_rating': 'good' if overall_score > 75 else 'needs_improvement',
                'slow_segments': [
                    {
                        'start': f"{int(duration*0.6//60)}:{int(duration*0.6%60):02d}",
                        'end': f"{int(duration*0.75//60)}:{int(duration*0.75%60):02d}",
                        'suggestion': 'Consider speeding up by 1.2x or adding more dynamic cuts'
                    }
                ] if duration > 60 else [],
                'fast_segments': [
                    {
                        'start': f"{int(duration*0.2//60)}:{int(duration*0.2%60):02d}",
                        'end': f"{int(duration*0.35//60)}:{int(duration*0.35%60):02d}",
                        'suggestion': 'Slow down slightly for better comprehension'
                    }
                ] if is_tutorial else []
            }
        },
        'sentiment_analysis': {
            'overall_sentiment': sentiment_type,
            'confidence': sentiment_score,
            'emotional_peaks': emotional_peaks,
            'recommended_tone': get_tone_recommendation(sentiment_type, is_tutorial, is_vlog, is_event)
        },
        'engagement_metrics': {
            'predicted_retention': random.uniform(0.65, 0.88),
            'hook_strength': random.uniform(0.7, 0.92),
            'climax_timing': f"{int(duration*0.6//60)}:{int(duration*0.6%60):02d}",
            'recommended_length': f"{int(duration*0.85//60)}:{int(duration*0.85%60):02d}",
            'improvements': get_engagement_improvements(filename_lower, is_tutorial, is_vlog)
        }
    }

def get_cut_reason(cut_type: str, is_tutorial: bool, is_vlog: bool) -> str:
    reasons = {
        'scene_change': 'Natural scene transition detected',
        'audio_silence': 'Extended silence period detected',
        'engagement': 'Low engagement moment identified',
        'transition': 'Perfect transition point for smooth flow'
    }
    
    if is_tutorial and cut_type == 'scene_change':
        return 'Topic transition detected - good cut point'
    elif is_vlog and cut_type == 'engagement':
        return 'Static moment - consider cutting for better pacing'
    
    return reasons.get(cut_type, 'Recommended cut point')

def get_cut_description(cut_type: str, filename: str) -> str:
    if 'outdoor' in filename:
        return 'Transition from indoor to outdoor scene detected'
    elif 'tutorial' in filename:
        return 'Step completion detected - natural break point'
    elif 'music' in filename:
        return 'Beat change detected - good sync point'
    else:
        return 'Visual composition change detected'

def get_tone_recommendation(sentiment: str, is_tutorial: bool, is_vlog: bool, is_event: bool) -> str:
    if is_tutorial:
        return 'Maintain professional tone. Add engaging elements during technical sections.'
    elif is_vlog:
        return 'Keep personal and authentic. Consider adding more dynamic moments.'
    elif is_event:
        return 'Maintain celebratory energy. Build towards emotional climax.'
    elif sentiment == 'positive':
        return 'Great positive energy! Consider amplifying peak moments.'
    else:
        return 'Consider adding more engaging elements to boost overall sentiment.'

def get_engagement_improvements(filename: str, is_tutorial: bool, is_vlog: bool) -> List[str]:
    base_improvements = [
        'Add text overlays at key information points',
        'Include call-to-action elements',
        'Optimize thumbnail for click-through',
        'Consider mobile viewing optimization'
    ]
    
    if is_tutorial:
        base_improvements.extend([
            'Add step-by-step text indicators',
            'Include progress markers',
            'Highlight important tools or materials'
        ])
    elif is_vlog:
        base_improvements.extend([
            'Add location tags or timestamps',
            'Include mood or energy indicators',
            'Consider split-screen for reactions'
        ])
    
    return base_improvements[:4]  # Return top 4 suggestions

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
