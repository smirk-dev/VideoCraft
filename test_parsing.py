#!/usr/bin/env python3
"""
Test script to verify that the script parsing functionality works with fallbacks.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test the components initialization
def test_script_parsing():
    """Test the script parsing with offline fallbacks."""
    print("🧪 Testing VideoCraft Script Parsing...")
    
    # Load configuration
    try:
        from main import load_config, initialize_components
        config = load_config()
        print("✅ Configuration loaded")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False
    
    # Initialize components
    try:
        components = initialize_components(config)
        print("✅ Components initialized")
        
        # Check if script_parser exists and is not None
        script_parser = components.get('script_parser')
        if script_parser is None:
            print("❌ Script parser is None")
            return False
        print("✅ Script parser component found")
        
    except Exception as e:
        print(f"❌ Failed to initialize components: {e}")
        return False
    
    # Test script parsing
    try:
        script_file = "test_script.txt"
        print(f"📄 Testing script parsing on {script_file}...")
        
        # Check if the method exists
        if not hasattr(script_parser, 'parse_script_file'):
            print("❌ parse_script_file method not found")
            return False
        print("✅ parse_script_file method exists")
        
        # Try to parse the script
        result = script_parser.parse_script_file(script_file)
        print("✅ Script parsing completed successfully")
        print(f"📊 Result type: {type(result)}")
        
        if result:
            print(f"📊 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Script parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_script_parsing()
    if success:
        print("\n🎉 All tests passed! Script parsing is working correctly.")
    else:
        print("\n💥 Tests failed. There are still issues to resolve.")
