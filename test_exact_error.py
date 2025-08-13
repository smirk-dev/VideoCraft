#!/usr/bin/env python3
"""
Test to verify the exact error scenario is fixed.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_exact_scenario():
    """Test the exact scenario that was causing the error."""
    print("🧪 Testing the exact error scenario...")
    
    try:
        # Import and initialize like main.py does
        from main import load_config, initialize_components
        
        config = load_config()
        components = initialize_components(config)
        
        # Get the content analyzer
        content_analyzer = components['content_analyzer']
        print(f"✅ Content analyzer type: {type(content_analyzer)}")
        
        # Check if it has the required method
        if hasattr(content_analyzer, 'adapt_suggestions_to_content'):
            print("✅ adapt_suggestions_to_content method exists")
        else:
            print("❌ adapt_suggestions_to_content method missing")
            return False
        
        # Simulate the exact call that was failing
        dummy_suggestions = [
            {'timestamp': 10.0, 'confidence': 0.8, 'reason': 'scene_change'},
            {'timestamp': 25.0, 'confidence': 0.7, 'reason': 'speaker_change'}
        ]
        
        # Create dummy analysis similar to what analyze_content would return
        dummy_analysis = {
            'content_type': 'interview',
            'confidence': 0.9,
            'key_elements': ['talking_heads', 'speech_heavy'],
            'suggested_style': 'conversational',
            'pacing': 'medium',
            'target_audience': 'general'
        }
        
        # This is the exact call that was failing
        adapted_suggestions = content_analyzer.adapt_suggestions_to_content(
            dummy_suggestions, dummy_analysis
        )
        
        print("✅ adapt_suggestions_to_content call succeeded!")
        print(f"📊 Original suggestions: {len(dummy_suggestions)}")
        print(f"📊 Adapted suggestions: {len(adapted_suggestions)}")
        
        return True
        
    except AttributeError as e:
        if "'IntelligentContentAnalyzer' object has no attribute 'adapt_suggestions_to_content'" in str(e):
            print(f"❌ The exact error is still happening: {e}")
            return False
        else:
            print(f"❌ Different AttributeError: {e}")
            return False
    except Exception as e:
        print(f"❌ Other error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_exact_scenario()
    if success:
        print("\n🎉 SUCCESS! The exact error scenario has been fixed!")
    else:
        print("\n💥 FAILED! The error scenario still needs to be resolved.")
