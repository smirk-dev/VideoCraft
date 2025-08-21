import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "VideoCraft Backend is running!", "status": "OK"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/analyze")
async def analyze_video(request: Dict[str, Any]):
    filename = request.get('filename', 'unknown')
    logger.info(f"Analyzing: {filename}")
    
    return {
        "success": True,
        "analysis": {
            "scene_analysis": [
                {"timestamp": "00:00", "description": "Opening scene", "score": 0.85},
                {"timestamp": "00:30", "description": "Main content", "score": 0.92},
                {"timestamp": "01:00", "description": "Conclusion", "score": 0.78}
            ],
            "emotion_detection": {
                "overall_sentiment": "positive",
                "confidence": 0.89
            },
            "video_quality": {
                "resolution": "1080p",
                "quality_score": 0.88
            }
        }
    }

@app.post("/api/analyze/analyze-filename")
async def analyze_by_filename(request: Dict[str, Any]):
    filename = request.get('filename', 'unknown')
    logger.info(f"Analyzing by filename: {filename}")
    
    return {
        "success": True,
        "analysis": {
            "scene_analysis": [
                {"timestamp": "00:00", "description": "Opening scene", "score": 0.85},
                {"timestamp": "00:30", "description": "Main content", "score": 0.92},
                {"timestamp": "01:00", "description": "Conclusion", "score": 0.78}
            ],
            "emotion_detection": {
                "overall_sentiment": "positive",
                "confidence": 0.89
            },
            "video_quality": {
                "resolution": "1080p",
                "quality_score": 0.88
            }
        }
    }

@app.post("/api/recommendations/generate")
async def generate_recommendations(request: Dict[str, Any]):
    filename = request.get('filename', 'unknown')
    logger.info(f"Generating recommendations for: {filename}")
    
    return {
        "success": True,
        "recommendations": {
            "smart_cuts": {
                "cuts": [
                    {
                        "type": "trim_beginning",
                        "timestamp": "00:00-00:03",
                        "reason": "Remove slow intro",
                        "priority": "high",
                        "confidence": 0.89
                    }
                ]
            },
            "engagement_optimization": {
                "tips": [
                    {
                        "category": "retention",
                        "tip": "Move key benefit to 00:07",
                        "priority": "critical",
                        "confidence": 0.96
                    }
                ]
            }
        }
    }

if __name__ == "__main__":
    print("🚀 Starting VideoCraft Backend...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info",
        access_log=True
    )
