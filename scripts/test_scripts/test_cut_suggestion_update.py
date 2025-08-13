#!/usr/bin/env python3
"""
Test script to verify that CutSuggestion.update() method works correctly.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cut_suggestion_update():
    """Test that CutSuggestion has a working update method."""
    print("🧪 Testing CutSuggestion.update() method...")
    
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
        
        # Test the update method exists
        if hasattr(original, 'update'):
            print("✅ update method exists")
            
            # Test updating existing fields
            original.update({
                'timestamp': 15.0,
                'confidence': 0.95,
                'reason': "updated scene change"
            })
            
            # Verify updates worked
            assert original.timestamp == 15.0
            assert original.confidence == 0.95
            assert original.reason == "updated scene change"
            print("✅ Existing field updates work correctly")
            
            # Test updating with new fields (should go to metadata)
            original.update({
                'user_edited': True,
                'type': 'manual',
                'custom_field': 'test_value'
            })
            
            # Verify new fields went to metadata
            assert original.metadata['user_edited'] == True
            assert original.metadata['type'] == 'manual'
            assert original.metadata['custom_field'] == 'test_value'
            print("✅ New field updates go to metadata correctly")
            
            # Test updating metadata directly
            original.update({
                'metadata': {'updated': True, 'version': 2}
            })
            
            # Verify metadata update
            assert original.metadata == {'updated': True, 'version': 2}
            print("✅ Metadata field update works correctly")
            
            # Test get method if it exists
            if hasattr(original, 'get'):
                print("✅ get method exists")
                
                # Test getting existing attributes
                assert original.get('timestamp') == 15.0
                assert original.get('confidence') == 0.95
                print("✅ get method works for attributes")
                
                # Test getting metadata values
                assert original.get('updated') == True
                assert original.get('version') == 2
                print("✅ get method works for metadata")
                
                # Test getting non-existent values with default
                assert original.get('nonexistent') is None
                assert original.get('nonexistent', 'default') == 'default'
                print("✅ get method handles defaults correctly")
            
            return True
        else:
            print("❌ update method not found")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_interactive_timeline_scenario():
    """Test the exact scenario from interactive timeline editor."""
    print("\n🧪 Testing interactive timeline editor scenario...")
    
    try:
        from src.suggestions.cut_suggester import CutSuggestion
        
        # Simulate cut suggestions list
        cut_suggestions = [
            CutSuggestion(
                timestamp=10.0,
                confidence=0.8,
                reason="scene change",
                suggestion_type="scene_change",
                metadata={"detected_at": "10s"}
            )
        ]
        
        cut_idx = 0
        
        # Simulate the exact update call from the timeline editor
        cut_suggestions[cut_idx].update({
            'timestamp': 12.5,
            'confidence': 0.9,
            'reason': "user adjusted scene change",
            'type': 'manual',
            'user_edited': True
        })
        
        # Verify the update worked
        suggestion = cut_suggestions[cut_idx]
        assert suggestion.timestamp == 12.5
        assert suggestion.confidence == 0.9
        assert suggestion.reason == "user adjusted scene change"
        assert suggestion.metadata['type'] == 'manual'
        assert suggestion.metadata['user_edited'] == True
        
        print("✅ Interactive timeline editor scenario works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Interactive timeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_cut_suggestion_update()
    success2 = test_interactive_timeline_scenario()
    
    if success1 and success2:
        print("\n🎉 All tests passed! CutSuggestion.update() is working correctly.")
        print("✅ Basic update functionality - WORKING")
        print("✅ Interactive timeline scenario - WORKING")
        print("✅ Metadata handling - WORKING")
    else:
        print("\n💥 Tests failed. CutSuggestion.update() needs to be fixed.")
