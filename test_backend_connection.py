import requests
import time

# Test if backend is responding
url = "http://127.0.0.1:8002/api/analyze/analyze-filename"
data = {
    "filename": "test_video.mp4",
    "metadata": {"duration": 120}
}

print("🔧 Testing backend connection...")
time.sleep(1)  # Give backend time to settle

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"✅ Backend responding! Status: {response.status_code}")
    result = response.json()
    print(f"✅ Analysis endpoint working: {result.get('success', False)}")
    if result.get('success'):
        print(f"✅ Analysis data received: {len(result.get('analysis', {}))} sections")
        print(f"✅ Recommendations received: {len(result.get('recommendations', []))} items")
except requests.exceptions.ConnectionError:
    print("❌ Connection failed: Backend not running or wrong port")
except requests.exceptions.Timeout:
    print("❌ Connection timeout: Backend taking too long to respond")
except Exception as e:
    print(f"❌ Backend connection failed: {e}")

print("✅ Test completed")
