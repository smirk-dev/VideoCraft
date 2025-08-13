#!/usr/bin/env python3
"""
Test script to verify that CutSuggestion.copy() method works correctly.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cut_suggestion_copy():
    """Test that CutSuggestion has a working copy method."""
    print("🧪 Testing CutSuggestion.copy() method...")
    
    try:
        from src.suggestions.cut_suggester import CutSuggestion
        print("✅ CutSuggestion imported successfully")
        
        # Create a test suggestion
        original = CutSuggestion(
            timestamp=10.5,
            confidence=0.85,
            reason="scene change detected",
            suggestion_type="scene_change",
            metadata={"scene_id": 1, "visual_change": 0.7}
        )
        print("✅ Original CutSuggestion created")
        
        # Test the copy method
        if hasattr(original, 'copy'):
            print("✅ copy method exists")
            
            # Make a copy
            copied = original.copy()
            print("✅ copy() method executed successfully")
            
            # Verify the copy is correct
            assert copied.timestamp == original.timestamp
            assert copied.confidence == original.confidence
            assert copied.reason == original.reason
            assert copied.suggestion_type == original.suggestion_type
            assert copied.metadata == original.metadata
            print("✅ Copy values match original")
            
            # Verify it's a different object (deep copy)
            assert copied is not original
            assert copied.metadata is not original.metadata
            print("✅ Copy is a separate object (deep copy)")
            
            # Test modification independence
            copied.confidence = 0.95
            copied.metadata["modified"] = True
            
            assert original.confidence == 0.85
            assert "modified" not in original.metadata
            print("✅ Modifications to copy don't affect original")
            
            return True
        else:
            print("❌ copy method not found")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cut_suggestion_copy()
    if success:
        print("\n🎉 All tests passed! CutSuggestion.copy() is working correctly.")
    else:
        print("\n💥 Tests failed. CutSuggestion.copy() needs to be fixed.")
