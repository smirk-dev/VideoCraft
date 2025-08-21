from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationsRequest(BaseModel):
    filename: str
    metadata: Optional[Dict[str, Any]] = None

app = FastAPI(title="VideoCraft Test Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/recommendations/generate")
async def generate_recommendations(request: RecommendationsRequest):
    """Test the enhanced recommendations endpoint"""
    try:
        logger.info(f"Testing enhanced recommendations for: {request.filename}")
        
        # Extract metadata for intelligent analysis
        metadata = request.metadata or {}
        duration = metadata.get('duration', 120)
        width = metadata.get('width', 1920)
        height = metadata.get('height', 1080)
        
        logger.info(f"Metadata: duration={duration}, width={width}, height={height}")
        
        # Basic calculations
        aspect_ratio = width / height if height > 0 else 16/9
        is_portrait = aspect_ratio < 1
        video_length_category = "short" if duration < 60 else "medium" if duration < 300 else "long"
        
        logger.info(f"Analysis: aspect_ratio={aspect_ratio}, is_portrait={is_portrait}, category={video_length_category}")
        
        # Simple test recommendations
        recommendations = {
            "overall_score": 85,
            "sentiment": "positive",
            "editing_recommendations": {
                "cuts": [
                    {
                        "id": "test_cut_1",
                        "type": "Trim Beginning",
                        "reason": "Remove first 3 seconds for better engagement",
                        "timestamp": "00:00-00:03",
                        "priority": "high",
                        "confidence": 0.89,
                        "expected_impact": "Increases retention by 15-20%"
                    }
                ],
                "music": [],
                "filters": [],
                "pacing": {"slow_segments": [], "fast_segments": []}
            },
            "quality_improvements": ["Test improvement 1", "Test improvement 2"],
            "engagement_tips": ["Test tip 1", "Test tip 2"],
            "platform_optimization": {
                "youtube": {
                    "recommended": True,
                    "optimizations": ["Perfect for YouTube"],
                    "content_tips": []
                }
            }
        }
        
        logger.info("Test recommendations generated successfully")
        
        return {
            "success": True,
            "recommendations": recommendations,
            "processing_time": "0.5 seconds"
        }
        
    except Exception as e:
        logger.error(f"Test recommendations failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": f"Test failed: {str(e)}",
            "recommendations": None
        }

if __name__ == "__main__":
    logger.info("🧪 Starting VideoCraft Test Backend...")
    uvicorn.run(
        "test_backend:app",
        host="127.0.0.1",
        port=8003,
        reload=False,
        log_level="info"
    )
