#!/usr/bin/env python3
"""
Test to verify CutSuggestion subscriptable functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.suggestions.cut_suggester import CutSuggestion

def test_subscriptable_functionality():
    """Test that CutSuggestion supports subscript operations"""
    print("🔍 Testing CutSuggestion subscriptable functionality...")
    
    # Create a test suggestion
    suggestion = CutSuggestion(
        timestamp=10.0,
        confidence=0.8,
        reason="Scene transition",
        suggestion_type="scene_change"
    )
    
    try:
        # Test __getitem__ with existing attributes
        timestamp = suggestion['timestamp']
        assert timestamp == 10.0, f"Expected 10.0, got {timestamp}"
        print("✅ suggestion['timestamp'] works")
        
        confidence = suggestion['confidence'] 
        assert confidence == 0.8, f"Expected 0.8, got {confidence}"
        print("✅ suggestion['confidence'] works")
        
        reason = suggestion['reason']
        assert reason == "Scene transition", f"Expected 'Scene transition', got {reason}"
        print("✅ suggestion['reason'] works")
        
        # Test __setitem__ with existing attributes
        suggestion['confidence'] = 0.9
        assert suggestion.confidence == 0.9, f"Expected 0.9, got {suggestion.confidence}"
        assert suggestion['confidence'] == 0.9, f"Expected 0.9, got {suggestion['confidence']}"
        print("✅ suggestion['confidence'] = 0.9 works")
        
        # Test __setitem__ with new metadata keys
        suggestion['custom_field'] = 'test_value'
        assert suggestion['custom_field'] == 'test_value', f"Expected 'test_value', got {suggestion['custom_field']}"
        print("✅ suggestion['custom_field'] = 'test_value' works")
        
        # Test __contains__ 
        assert 'timestamp' in suggestion, "Expected 'timestamp' to be in suggestion"
        assert 'custom_field' in suggestion, "Expected 'custom_field' to be in suggestion"
        assert 'nonexistent_key' not in suggestion, "Expected 'nonexistent_key' to not be in suggestion"
        print("✅ 'key' in suggestion works")
        
        # Test KeyError for non-existent keys
        try:
            value = suggestion['nonexistent_key']
            assert False, "Expected KeyError for non-existent key"
        except KeyError:
            print("✅ KeyError raised for non-existent key")
        
        # Test compatibility with existing methods
        copied = suggestion.copy()
        assert copied['confidence'] == 0.9, f"Expected 0.9, got {copied['confidence']}"
        assert copied['custom_field'] == 'test_value', f"Expected 'test_value', got {copied['custom_field']}"
        print("✅ Subscriptable works with copy()")
        
        suggestion.update({'confidence': 0.7, 'another_field': 'another_value'})
        assert suggestion['confidence'] == 0.7, f"Expected 0.7, got {suggestion['confidence']}"
        assert suggestion['another_field'] == 'another_value', f"Expected 'another_value', got {suggestion['another_field']}"
        print("✅ Subscriptable works with update()")
        
        # Test get method still works
        value = suggestion.get('confidence', 0.5)
        assert value == 0.7, f"Expected 0.7, got {value}"
        
        default_value = suggestion.get('missing_key', 'default')
        assert default_value == 'default', f"Expected 'default', got {default_value}"
        print("✅ get() method still works with subscriptable")
        
        return True
        
    except Exception as e:
        print(f"❌ Subscriptable test failed: {e}")
        return False

def test_real_world_scenario():
    """Test a real-world scenario that might cause 'not subscriptable' error"""
    print("\n🔍 Testing real-world subscriptable scenario...")
    
    try:
        # Simulate how the code might be used in the application
        suggestion = CutSuggestion(
            timestamp=15.5,
            confidence=0.85,
            reason="Dialog pause detected",
            suggestion_type="dialogue_pause"
        )
        
        # Code that might treat it like a dictionary
        data = {
            'time': suggestion['timestamp'],
            'score': suggestion['confidence'],
            'type': suggestion['suggestion_type'],
            'description': suggestion['reason']
        }
        
        # Add some metadata
        suggestion['user_rating'] = 4.5
        suggestion['editor_notes'] = "Good cut point"
        
        # Check if the suggestion contains expected keys
        if 'user_rating' in suggestion and 'editor_notes' in suggestion:
            print("✅ Real-world metadata handling works")
        
        # Update multiple fields at once
        updates = {
            'confidence': 0.95,
            'priority': 'high',
            'reviewed': True
        }
        suggestion.update(updates)
        
        # Verify all updates using subscript access
        assert suggestion['confidence'] == 0.95
        assert suggestion['priority'] == 'high'
        assert suggestion['reviewed'] == True
        
        print("✅ Real-world update scenario works")
        return True
        
    except Exception as e:
        print(f"❌ Real-world scenario failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing CutSuggestion subscriptable fixes...")
    print("=" * 60)
    
    success = True
    
    # Test basic subscriptable functionality
    success &= test_subscriptable_functionality()
    
    # Test real-world scenarios
    success &= test_real_world_scenario()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL SUBSCRIPTABLE TESTS PASSED!")
        print("✅ CutSuggestion is now fully dictionary-compatible")
        print("✅ No more 'object is not subscriptable' errors")
    else:
        print("❌ Some subscriptable tests failed")
        sys.exit(1)
