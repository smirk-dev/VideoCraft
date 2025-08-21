import requests
import json

url = "http://127.0.0.1:8003/api/recommendations/generate"
data = {
    "filename": "travel_vlog_example.mp4",
    "metadata": {
        "duration": 150,
        "width": 1920,
        "height": 1080,
        "size": 75000000
    }
}

print("🧪 Testing simple backend...")
try:
    response = requests.post(url, json=data, timeout=10)
    print(f"Status: {response.status_code}")
    if response.headers.get('content-type', '').startswith('application/json'):
        result = response.json()
        print(f"Success: {result.get('success')}")
        if result.get('success'):
            print("✅ Test backend works!")
        else:
            print(f"❌ Error: {result.get('error')}")
    else:
        print(f"Non-JSON: {response.text}")
except Exception as e:
    print(f"❌ Exception: {e}")
