#!/usr/bin/env python3
"""
Test the frontend API connection to see exact data flow
"""
import requests
import json

# Test the exact API call the frontend makes
url = "http://127.0.0.1:8002/api/analyze/analyze-filename"
data = {
    "filename": "test_video.mp4"
}

print("🔧 Testing frontend API call...")
print(f"URL: {url}")
print(f"Request data: {json.dumps(data, indent=2)}")
print()

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"✅ Response Status: {response.status_code}")
    print(f"✅ Response Headers: {dict(response.headers)}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Response JSON:")
        print(json.dumps(result, indent=2))
        print()
        
        # Check if analysis data exists
        if result.get('success') and result.get('analysis'):
            analysis = result['analysis']
            print("📊 Analysis sections found:")
            print(f"  - Scenes: {len(analysis.get('scenes', []))}")
            print(f"  - Emotions: {len(analysis.get('emotions', []))}")
            print(f"  - Audio: {'Yes' if analysis.get('audio_analysis') else 'No'}")
            print(f"  - Recommendations: {len(result.get('recommendations', []))}")
        else:
            print("❌ No analysis data in response")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"Response text: {response.text}")
        
except Exception as e:
    print(f"❌ Request failed: {e}")

print("\n✅ Test completed")
