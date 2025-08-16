#!/usr/bin/env python3
"""
Test script to verify that CutSuggestion.copy() method works correctly.
"""
import sys
import os
# Ensure project root (one level up from scripts directory) is on path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def test_cut_suggestion_copy():
    """Test that CutSuggestion has a working copy method (uses asserts, returns None)."""
    # Import directly from module to avoid unnecessary heavy imports
    from src.suggestions.cut_suggester import CutSuggestion

    # Create a test suggestion
    original = CutSuggestion(
        timestamp=10.5,
        confidence=0.85,
        reason="scene change detected",
        suggestion_type="scene_change",
        metadata={"scene_id": 1, "visual_change": 0.7}
    )

    # Ensure copy method exists
    assert hasattr(original, 'copy'), "CutSuggestion missing copy method"

    # Make a copy
    copied = original.copy()

    # Verify the copy is correct
    assert copied.timestamp == original.timestamp
    assert copied.confidence == original.confidence
    assert copied.reason == original.reason
    assert copied.suggestion_type == original.suggestion_type
    assert copied.metadata == original.metadata

    # Verify it's a deep copy
    assert copied is not original
    assert copied.metadata is not original.metadata

    # Test modification independence
    copied.confidence = 0.95
    copied.metadata["modified"] = True
    assert original.confidence == 0.85
    assert "modified" not in original.metadata

if __name__ == "__main__":
    # Run the test manually (will raise AssertionError if it fails)
    test_cut_suggestion_copy()
    print("\n🎉 All tests passed! CutSuggestion.copy() is working correctly.")
