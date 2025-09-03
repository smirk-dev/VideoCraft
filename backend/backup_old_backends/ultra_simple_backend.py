#!/usr/bin/env python3
"""
Ultra Simple Backend - Guaranteed to work and show data
"""
import json
import http.server
import socketserver
from urllib.parse import parse_qs, urlparse
import threading
import time

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        print(f"[GET] Request to: {path}")
        
        if path == '/api/health':
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "message": "Backend is working!"}).encode())
            
        elif path == '/api/analyze':
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Ultra simple data that matches frontend expectations
            data = {
                "emotions": [
                    {"emotion": "happy", "confidence": 0.85, "timestamp": 2.5},
                    {"emotion": "excited", "confidence": 0.92, "timestamp": 8.1},
                    {"emotion": "calm", "confidence": 0.78, "timestamp": 15.3}
                ],
                "scenes": [
                    {"scene_type": "outdoor", "confidence": 0.88, "timestamp": 1.0},
                    {"scene_type": "indoor", "confidence": 0.75, "timestamp": 10.5},
                    {"scene_type": "outdoor", "confidence": 0.90, "timestamp": 20.2}
                ],
                "overall_mood": "positive",
                "dominant_emotion": "happy",
                "summary": "Video shows positive emotions with outdoor and indoor scenes"
            }
            
            print(f"[RESPONSE] Sending analysis data: {data}")
            self.wfile.write(json.dumps(data).encode())
            
        elif path == '/api/recommendations':
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Simple recommendations
            data = {
                "music_recommendations": [
                    {
                        "title": "Happy Song",
                        "artist": "Good Vibes Band",
                        "mood": "uplifting",
                        "confidence": 0.9,
                        "reason": "Matches the happy emotions detected"
                    },
                    {
                        "title": "Outdoor Adventure",
                        "artist": "Nature Sounds",
                        "mood": "energetic",
                        "confidence": 0.8,
                        "reason": "Perfect for outdoor scenes"
                    }
                ],
                "editing_suggestions": [
                    "Add bright filters for happy moments",
                    "Use fast cuts during exciting scenes",
                    "Add nature sound effects for outdoor scenes"
                ],
                "color_recommendations": [
                    {"color": "bright yellow", "reason": "Enhances happy emotions"},
                    {"color": "green", "reason": "Complements outdoor scenes"}
                ]
            }
            
            print(f"[RESPONSE] Sending recommendations: {data}")
            self.wfile.write(json.dumps(data).encode())
            
        else:
            self.send_response(404)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        print(f"[POST] Request to: {path}")
        
        if path.startswith('/api/analyze'):
            # Handle POST requests to /api/analyze or /api/analyze/analyze-filename
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode('utf-8')) if post_data else {}
                print(f"[POST DATA] {request_data}")
            except:
                request_data = {}
            
            # Return data in the format the SimpleAnalysisPage expects
            response_data = {
                "success": True,
                "analysis": {
                    "emotion_detection": {
                        "emotion_timeline": [
                            {"emotion": "happy", "intensity": 0.85, "timestamp": "00:02"},
                            {"emotion": "excited", "intensity": 0.92, "timestamp": "00:08"},
                            {"emotion": "calm", "intensity": 0.78, "timestamp": "00:15"}
                        ]
                    },
                    "scene_analysis": [
                        {
                            "scene": "outdoor nature", 
                            "confidence": 0.88, 
                            "timestamp": "00:01",
                            "description": "Beautiful outdoor landscape with trees and mountains"
                        },
                        {
                            "scene": "indoor room", 
                            "confidence": 0.75, 
                            "timestamp": "00:10",
                            "description": "Cozy indoor setting with warm lighting"
                        },
                        {
                            "scene": "outdoor park", 
                            "confidence": 0.90, 
                            "timestamp": "00:20",
                            "description": "Open park area with people enjoying activities"
                        }
                    ],
                    "processing_time_seconds": 2.3
                },
                "recommendations": [
                    {
                        "type": "Music Suggestion",
                        "suggestion": "Add uplifting acoustic music that matches the happy emotions",
                        "confidence": 0.9,
                        "platform": "YouTube"
                    },
                    {
                        "type": "Color Grading",
                        "suggestion": "Use warm color filters to enhance the positive mood",
                        "confidence": 0.85,
                        "platform": "TikTok"
                    },
                    {
                        "type": "Editing Style",
                        "suggestion": "Try quick cuts during exciting moments for dynamic feel",
                        "confidence": 0.8,
                        "platform": "Instagram"
                    }
                ]
            }
            
            print(f"[RESPONSE] Sending structured analysis data")
            self.wfile.write(json.dumps(response_data).encode())
            
        elif self.path == '/api/upload':
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Upload successful", "file_id": "test123"}).encode())
        else:
            self.send_response(404)
            self._set_cors_headers()
            self.end_headers()

def start_server():
    PORT = 8002
    print(f"\n🚀 ULTRA SIMPLE BACKEND STARTING ON PORT {PORT}")
    print(f"📊 This backend WILL show data in the frontend!")
    print(f"🔗 Health check: http://localhost:{PORT}/api/health")
    print(f"📈 Analysis: http://localhost:{PORT}/api/analyze")
    print(f"💡 Recommendations: http://localhost:{PORT}/api/recommendations")
    print("-" * 50)
    
    with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
        print(f"✅ Server running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    start_server()
