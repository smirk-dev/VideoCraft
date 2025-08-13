#!/usr/bin/env python3
"""
Test script to verify that the IntelligentContentAnalyzer has the required methods.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_content_analyzer():
    """Test the IntelligentContentAnalyzer for missing methods."""
    print("🧪 Testing IntelligentContentAnalyzer...")
    
    try:
        from src.ai_models.intelligent_content_analyzer import IntelligentContentAnalyzer
        print("✅ IntelligentContentAnalyzer imported successfully")
        
        # Create instance with minimal config
        config = {'ai_models': {'cache_dir': './cache'}}
        analyzer = IntelligentContentAnalyzer(config)
        print("✅ IntelligentContentAnalyzer instance created")
        
        # Check if required methods exist
        required_methods = [
            'analyze_content',
            'adapt_suggestions_to_content',
            'analyze_content_type',
            'generate_adaptive_suggestions'
        ]
        
        for method_name in required_methods:
            if hasattr(analyzer, method_name):
                print(f"✅ Method {method_name} exists")
            else:
                print(f"❌ Method {method_name} is missing")
                return False
        
        # Test the adapt_suggestions_to_content method with dummy data
        dummy_suggestions = [
            {'timestamp': 10.0, 'confidence': 0.8, 'reason': 'scene_change'},
            {'timestamp': 25.0, 'confidence': 0.7, 'reason': 'speaker_change'}
        ]
        
        dummy_analysis = {
            'content_type': 'interview',
            'confidence': 0.9,
            'key_elements': ['talking_heads', 'speech_heavy'],
            'suggested_style': 'conversational',
            'pacing': 'medium',
            'target_audience': 'general'
        }
        
        try:
            adapted = analyzer.adapt_suggestions_to_content(dummy_suggestions, dummy_analysis)
            print("✅ adapt_suggestions_to_content method works correctly")
            print(f"📊 Adapted {len(dummy_suggestions)} suggestions to {len(adapted)} suggestions")
            return True
        except Exception as e:
            print(f"❌ adapt_suggestions_to_content method failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test IntelligentContentAnalyzer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_content_analyzer()
    if success:
        print("\n🎉 All tests passed! IntelligentContentAnalyzer is working correctly.")
    else:
        print("\n💥 Tests failed. There are still issues to resolve.")
