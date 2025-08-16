#!/usr/bin/env python3
"""
Test script to verify that the script parsing functionality works with fallbacks.
"""
import sys
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Test the components initialization
def test_script_parsing():
    """Test the script parsing with offline fallbacks (assert-based)."""
    from main import load_config, initialize_components

    config = load_config()
    components = initialize_components(config)

    # Validate script_parser presence
    script_parser = components.get('script_parser')
    assert script_parser is not None, "script_parser component missing"
    assert hasattr(script_parser, 'parse_script_file'), "parse_script_file method missing"

    # Parse script
    result = script_parser.parse_script_file("test_script.txt")
    # Basic structural assertions
    assert result is not None, "parse_script_file returned None"
    if isinstance(result, dict):
        # Expect at least one key like 'dialogue' or similar (soft check)
        assert len(result.keys()) > 0, "Parsed result dict is empty"

if __name__ == "__main__":
    test_script_parsing()
    print("\n🎉 All tests passed! Script parsing is working correctly.")
