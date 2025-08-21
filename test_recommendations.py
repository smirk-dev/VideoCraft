import requests
import json

# Test the recommendations API
url = "http://127.0.0.1:8002/api/recommendations/generate"
data = {
    "filename": "test_video.mp4",
    "metadata": {
        "duration": 120,
        "resolution": "1920x1080",
        "fps": 30
    }
}

print("🔄 Testing recommendations API...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📊 Response Headers: {dict(response.headers)}")
    
    if response.headers.get('content-type', '').startswith('application/json'):
        result = response.json()
        print(f"\n📋 Response JSON:")
        print(json.dumps(result, indent=2))
        
        # Check the structure specifically
        if 'recommendations' in result:
            recs = result['recommendations']
            print(f"\n🔍 Recommendations structure:")
            print(f"  - Type: {type(recs)}")
            print(f"  - Keys: {list(recs.keys()) if isinstance(recs, dict) else 'Not a dict'}")
            
            if 'editing_recommendations' in recs:
                editing = recs['editing_recommendations']
                print(f"  - editing_recommendations type: {type(editing)}")
                print(f"  - editing_recommendations keys: {list(editing.keys()) if isinstance(editing, dict) else 'Not a dict'}")
                
                for key in ['cuts', 'music', 'filters', 'pacing']:
                    if key in editing:
                        print(f"    - {key}: {len(editing[key])} items" if isinstance(editing[key], list) else f"    - {key}: {type(editing[key])}")
    else:
        print(f"\n📄 Response Text: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
