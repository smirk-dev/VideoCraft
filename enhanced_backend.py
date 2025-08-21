#!/usr/bin/env python3
"""
Enhanced backend with simpler, more reliable data structure for frontend
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleCORSHandler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            # Add CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Parse the request path
            parsed_path = urllib.parse.urlparse(self.path)
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            logger.info(f"Received POST to {self.path}")
            logger.info(f"Request data: {post_data}")
            
            if '/api/analyze/analyze-filename' in self.path:
                # Return analysis data in the EXACT format the frontend expects
                response = {
                    "success": True,
                    "analysis": {
                        # Emotions - should map to frontend emotions array
                        "emotions": [
                            {"timestamp": "0:15", "emotion": "joy", "confidence": 0.89},
                            {"timestamp": "0:45", "emotion": "excitement", "confidence": 0.76},
                            {"timestamp": "1:15", "emotion": "surprise", "confidence": 0.82}
                        ],
                        
                        # Scene analysis - should map to frontend scenes array
                        "scenes": [
                            {
                                "scene": "Indoor",
                                "confidence": 0.85,
                                "duration": "1:30",
                                "type": "Primary"
                            }
                        ],
                        
                        # Scene changes - should map to frontend sceneChanges array
                        "scene_changes": [
                            {"timestamp": "0:30", "confidence": 0.75, "type": "Cut"},
                            {"timestamp": "1:00", "confidence": 0.80, "type": "Fade"},
                            {"timestamp": "1:30", "confidence": 0.82, "type": "Dissolve"}
                        ],
                        
                        # Audio analysis - should map to frontend audioAnalysis object
                        "audio_analysis": {
                            "avg_volume": 65,
                            "peak_volume": 90,
                            "silent_segments": 2,
                            "music_detected": True,
                            "speech_quality": "Good"
                        },
                        
                        # Motion analysis
                        "motion_analysis": {
                            "motion_type": "moderate",
                            "motion_intensity": 0.6,
                            "camera_movement": "minimal"
                        },
                        
                        # AI suggestions
                        "ai_suggestions": [
                            {
                                "type": "Enhancement",
                                "timestamp": "0:36",
                                "reason": "Great emotional peak detected - consider highlighting this moment",
                                "confidence": 0.85
                            },
                            {
                                "type": "Audio",
                                "timestamp": "1:05",
                                "reason": "Audio quality is excellent in this segment",
                                "confidence": 0.90
                            }
                        ],
                        
                        # Video insights
                        "insights": [
                            "Analysis completed successfully",
                            "Strong emotional engagement detected",
                            "Good audio quality throughout",
                            "3 scene transitions identified",
                            "Recommended for social media content"
                        ]
                    },
                    
                    # Top-level recommendations
                    "recommendations": [
                        {
                            "type": "cut",
                            "suggestion": "Create a highlights reel from 30-90 seconds",
                            "confidence": 0.92,
                            "platform": "instagram"
                        },
                        {
                            "type": "filter",
                            "suggestion": "Apply slight saturation boost for better engagement",
                            "confidence": 0.78,
                            "platform": "tiktok"
                        },
                        {
                            "type": "audio",
                            "suggestion": "Current audio levels are optimal",
                            "confidence": 0.87,
                            "platform": "youtube"
                        }
                    ]
                }
                
            elif '/api/recommendations/generate' in self.path or '/api/recommendations' in self.path:
                # Return basic recommendations
                response = {
                    "success": True,
                    "recommendations": [
                        {
                            "type": "cut",
                            "suggestion": "Create a highlights reel from 30-90 seconds",
                            "confidence": 0.92,
                            "platform": "instagram"
                        },
                        {
                            "type": "filter",
                            "suggestion": "Apply slight saturation boost for better engagement",
                            "confidence": 0.78,
                            "platform": "tiktok"
                        },
                        {
                            "type": "audio",
                            "suggestion": "Current audio levels are optimal",
                            "confidence": 0.87,
                            "platform": "youtube"
                        }
                    ]
                }
            
            elif '/api/projects' in self.path:
                # Return project data
                response = {
                    "success": True,
                    "projects": [
                        {
                            "id": 1,
                            "name": "Current Video Project",
                            "filename": "test_video.mp4",
                            "created_at": "2025-08-22T00:00:00Z",
                            "status": "active"
                        }
                    ]
                }
            else:
                response = {"success": False, "error": f"Endpoint not found: {self.path}"}
            
            # Send response
            response_json = json.dumps(response)
            self.wfile.write(response_json.encode('utf-8'))
            logger.info(f"Response sent successfully: {len(response_json)} bytes")
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))

def run_server():
    """Start the enhanced HTTP server"""
    port = 8002
    server = HTTPServer(('0.0.0.0', port), SimpleCORSHandler)
    logger.info(f"🚀 Enhanced backend running on http://localhost:{port}")
    logger.info("✅ CORS enabled for all origins")
    logger.info("📡 Endpoints available:")
    logger.info("   POST /api/analyze/analyze-filename")
    logger.info("   POST /api/recommendations/generate")
    logger.info("   POST /api/projects/")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
        server.shutdown()

if __name__ == "__main__":
    run_server()
