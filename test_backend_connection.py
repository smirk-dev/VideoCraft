import requests

# Test if backend is responding
url = "http://127.0.0.1:8002/api/analyze/analyze-filename"
data = {
    "filename": "test_video.mp4",
    "metadata": {"duration": 120}
}

try:
    response = requests.post(url, json=data, timeout=5)
    print(f"✅ Backend responding! Status: {response.status_code}")
    result = response.json()
    print(f"✅ Analysis endpoint working: {result.get('success', False)}")
    if result.get('success'):
        print(f"✅ Analysis data received: {len(result.get('analysis', {}))} sections")
except Exception as e:
    print(f"❌ Backend connection failed: {e}")
