import requests
import json

# Test the recommendations API with minimal data
url = "http://127.0.0.1:8002/api/recommendations/generate"
data = {
    "filename": "test_video.mp4",
    "metadata": None
}

print("🔄 Testing recommendations API...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    print("🔄 Making request...")
    response = requests.post(url, json=data, timeout=10)
    print(f"✅ Response received! Status: {response.status_code}")
    
    if response.headers.get('content-type', '').startswith('application/json'):
        result = response.json()
        print(f"\n📋 Response JSON:")
        print(json.dumps(result, indent=2))
    else:
        print(f"\n� Response Text: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request Error: {e}")
except Exception as e:
    print(f"❌ Other Error: {e}")
