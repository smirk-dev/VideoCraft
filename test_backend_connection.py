import requests

# Test if backend is responding
url = "http://127.0.0.1:8005/api/analyze"
data = {
    "filename": "test_video.mp4",
    "metadata": {"duration": 120}
}

try:
    response = requests.post(url, json=data, timeout=5)
    print(f"✅ Backend responding! Status: {response.status_code}")
    result = response.json()
    print(f"✅ Analysis endpoint working: {result.get('success', False)}")
except Exception as e:
    print(f"❌ Backend connection failed: {e}")
