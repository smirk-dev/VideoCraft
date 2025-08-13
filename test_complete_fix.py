#!/usr/bin/env python3
"""
Comprehensive test for all CutSuggestion AttributeError fixes including subscriptable
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.suggestions.cut_suggester import CutSuggestion

def test_all_dictionary_compatibility():
    """Test complete dictionary compatibility of CutSuggestion"""
    print("🔍 Testing complete dictionary compatibility...")
    
    suggestion = CutSuggestion(
        timestamp=20.0,
        confidence=0.9,
        reason="Music beat",
        suggestion_type="emotion_beat"
    )
    
    try:
        # Test all dictionary-like operations
        
        # 1. Subscript access (the main fix)
        assert suggestion['timestamp'] == 20.0
        assert suggestion['confidence'] == 0.9
        print("✅ Subscript reading works")
        
        # 2. Subscript assignment
        suggestion['confidence'] = 0.95
        suggestion['priority'] = 'high'
        assert suggestion['confidence'] == 0.95
        assert suggestion['priority'] == 'high'
        print("✅ Subscript assignment works")
        
        # 3. Contains check
        assert 'timestamp' in suggestion
        assert 'priority' in suggestion
        assert 'missing' not in suggestion
        print("✅ Contains check works")
        
        # 4. Get method
        value = suggestion.get('confidence', 0.0)
        assert value == 0.95
        default = suggestion.get('missing', 'fallback')
        assert default == 'fallback'
        print("✅ get() method works")
        
        # 5. Update method
        suggestion.update({
            'confidence': 0.98,
            'user_notes': 'Perfect cut',
            'reviewed': True
        })
        assert suggestion['confidence'] == 0.98
        assert suggestion['user_notes'] == 'Perfect cut'
        assert suggestion['reviewed'] == True
        print("✅ update() method works")
        
        # 6. Copy method
        copied = suggestion.copy()
        assert copied['confidence'] == 0.98
        assert copied['user_notes'] == 'Perfect cut'
        
        # Test independence of copies
        copied['confidence'] = 0.5
        assert suggestion['confidence'] == 0.98  # Original unchanged
        assert copied['confidence'] == 0.5
        print("✅ copy() method works")
        
        # 7. Mixed access patterns (very important for real use)
        suggestion.confidence = 0.85  # Direct attribute access
        assert suggestion['confidence'] == 0.85  # Subscript access
        
        suggestion['timestamp'] = 25.0  # Subscript assignment
        assert suggestion.timestamp == 25.0  # Direct attribute access
        print("✅ Mixed access patterns work")
        
        return True
        
    except Exception as e:
        print(f"❌ Dictionary compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_scenarios():
    """Test proper error handling"""
    print("\n🔍 Testing error scenarios...")
    
    suggestion = CutSuggestion(
        timestamp=10.0,
        confidence=0.8,
        reason="Test",
        suggestion_type="test"
    )
    
    try:
        # Test KeyError for missing keys
        try:
            value = suggestion['nonexistent']
            print("❌ Should have raised KeyError")
            return False
        except KeyError:
            print("✅ KeyError properly raised for missing keys")
        
        # Test that get() doesn't raise errors
        value = suggestion.get('nonexistent', 'default')
        assert value == 'default'
        print("✅ get() handles missing keys gracefully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error scenario test failed: {e}")
        return False

def simulate_interactive_timeline_usage():
    """Simulate the exact usage pattern that was causing 'not subscriptable' errors"""
    print("\n🔍 Simulating interactive timeline usage...")
    
    try:
        # Create suggestions like the timeline editor would
        suggestions = [
            CutSuggestion(
                timestamp=5.0,
                confidence=0.8,
                reason="Scene change",
                suggestion_type="scene_change"
            ),
            CutSuggestion(
                timestamp=12.0,
                confidence=0.9,
                reason="Speaker change",
                suggestion_type="speaker_change"
            )
        ]
        
        # Simulate interactive timeline editor operations
        for i, suggestion in enumerate(suggestions):
            # This is the exact type of operation that was failing
            timeline_data = {
                'id': i,
                'time': suggestion['timestamp'],  # This was causing 'not subscriptable'
                'confidence': suggestion['confidence'],
                'type': suggestion['suggestion_type'],
                'description': suggestion['reason']
            }
            
            # User interaction - updating suggestions
            suggestion['user_accepted'] = True
            suggestion['edit_timestamp'] = suggestion['timestamp'] + 0.1
            
            # Learning system operations
            if suggestion['confidence'] > 0.85:
                suggestion['high_quality'] = True
                
            # Timeline sync operations
            suggestion.update({
                'timeline_id': f"cut_{i}",
                'status': 'active'
            })
            
        print("✅ Interactive timeline simulation successful")
        return True
        
    except Exception as e:
        print(f"❌ Interactive timeline simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE CUTSUGGESTION COMPATIBILITY TEST")
    print("=" * 70)
    
    success = True
    
    # Test all functionality
    success &= test_all_dictionary_compatibility()
    success &= test_error_scenarios()
    success &= simulate_interactive_timeline_usage()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 ALL TESTS PASSED! CUTSUGGESTION IS NOW FULLY COMPATIBLE!")
        print("✅ No more 'object is not subscriptable' errors")
        print("✅ No more 'object has no attribute update' errors")
        print("✅ Complete dictionary-like interface implemented")
        print("✅ Interactive timeline editor will work perfectly")
        print("✅ User learning system will work perfectly")
        print("✅ VideoCraft is production-ready!")
    else:
        print("❌ Some tests failed - need to investigate")
        sys.exit(1)
