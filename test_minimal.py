import requests
import json

url = "http://127.0.0.1:8004/api/recommendations/generate"
data = {
    "filename": "test_enhanced.mp4",
    "metadata": {"duration": 120, "width": 1920, "height": 1080}
}

print("🧪 Testing minimal enhanced backend...")
try:
    response = requests.post(url, json=data, timeout=10)
    print(f"✅ Status: {response.status_code}")
    result = response.json()
    print(f"✅ Success: {result.get('success')}")
    if result.get('success'):
        print(f"✅ Enhanced features working! Score: {result['recommendations']['overall_score']}")
    else:
        print(f"❌ Error: {result.get('error')}")
except Exception as e:
    print(f"❌ Exception: {e}")
