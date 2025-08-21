import requests
import json
import traceback

# Test the enhanced recommendations API
url = "http://127.0.0.1:8002/api/recommendations/generate"
data = {
    "filename": "travel_vlog_example.mp4",
    "metadata": {
        "duration": 150,
        "width": 1920,
        "height": 1080,
        "size": 75000000
    }
}

print("🔄 Testing enhanced AI recommendations...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    print("🔄 Making request...")
    response = requests.post(url, json=data, timeout=30)
    print(f"✅ Response received! Status: {response.status_code}")
    
    if response.headers.get('content-type', '').startswith('application/json'):
        result = response.json()
        print(f"\n📋 Success: {result.get('success', False)}")
        if result.get('success'):
            recs = result['recommendations']
            print(f"📋 Overall Score: {recs.get('overall_score', 'N/A')}")
            print(f"📋 Sentiment: {recs.get('sentiment', 'N/A')}")
            print(f"📋 Cuts: {len(recs['editing_recommendations'].get('cuts', []))}")
            print(f"📋 Music: {len(recs['editing_recommendations'].get('music', []))}")
            print(f"📋 Filters: {len(recs['editing_recommendations'].get('filters', []))}")
            print(f"📋 Quality Improvements: {len(recs.get('quality_improvements', []))}")
            print(f"📋 Engagement Tips: {len(recs.get('engagement_tips', []))}")
            print(f"📋 Platform Optimizations: {len(recs.get('platform_optimization', {}))}")
            
            # Show a sample cut recommendation
            if recs['editing_recommendations'].get('cuts'):
                cut = recs['editing_recommendations']['cuts'][0]
                print(f"\n🎬 Sample Cut Recommendation:")
                print(f"   Type: {cut.get('type')}")
                print(f"   Reason: {cut.get('reason')}")
                print(f"   Impact: {cut.get('expected_impact', 'N/A')}")
                print(f"   Priority: {cut.get('priority')}")
                
        else:
            print(f"❌ Error in response: {result.get('error', 'Unknown error')}")
    else:
        print(f"\n📄 Non-JSON Response: {response.text[:500]}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request Error: {e}")
except Exception as e:
    print(f"❌ Other Error: {e}")
    print(f"❌ Traceback: {traceback.format_exc()}")
