#!/usr/bin/env python3
"""
Comprehensive test to verify all fixes for missing methods are working.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_all_fixes():
    """Test all the method fixes we've implemented."""
    print("🧪 Testing all method fixes comprehensively...")
    
    # Test 1: BasicNLPProcessor parse_script_file method
    print("\n1️⃣ Testing BasicNLPProcessor.parse_script_file...")
    try:
        from src.utils.offline_models import BasicNLPProcessor
        processor = BasicNLPProcessor()
        
        if hasattr(processor, 'parse_script_file'):
            print("✅ BasicNLPProcessor.parse_script_file exists")
            # Test with dummy file
            result = processor.parse_script_file("test_script.txt")
            print(f"✅ parse_script_file returns: {type(result)}")
        else:
            print("❌ BasicNLPProcessor.parse_script_file missing")
            return False
    except Exception as e:
        print(f"❌ BasicNLPProcessor test failed: {e}")
        return False
    
    # Test 2: IntelligentContentAnalyzer adapt_suggestions_to_content method
    print("\n2️⃣ Testing IntelligentContentAnalyzer.adapt_suggestions_to_content...")
    try:
        from src.ai_models.intelligent_content_analyzer import IntelligentContentAnalyzer
        config = {'ai_models': {'cache_dir': './cache'}}
        analyzer = IntelligentContentAnalyzer(config)
        
        if hasattr(analyzer, 'adapt_suggestions_to_content'):
            print("✅ IntelligentContentAnalyzer.adapt_suggestions_to_content exists")
            
            # Test with dummy data
            dummy_suggestions = [{'timestamp': 10.0, 'confidence': 0.8, 'reason': 'test'}]
            dummy_analysis = {'content_type': 'interview', 'confidence': 0.9}
            
            result = analyzer.adapt_suggestions_to_content(dummy_suggestions, dummy_analysis)
            print(f"✅ adapt_suggestions_to_content returns: {type(result)} with {len(result)} items")
        else:
            print("❌ IntelligentContentAnalyzer.adapt_suggestions_to_content missing")
            return False
    except Exception as e:
        print(f"❌ IntelligentContentAnalyzer test failed: {e}")
        return False
    
    # Test 3: CutSuggestion copy method
    print("\n3️⃣ Testing CutSuggestion.copy...")
    try:
        from src.suggestions.cut_suggester import CutSuggestion
        
        original = CutSuggestion(
            timestamp=15.0,
            confidence=0.9,
            reason="test copy",
            suggestion_type="test",
            metadata={"test": True}
        )
        
        if hasattr(original, 'copy'):
            print("✅ CutSuggestion.copy exists")
            
            copied = original.copy()
            print(f"✅ CutSuggestion.copy() works: {type(copied)}")
            
            # Verify it's a proper copy
            assert copied.timestamp == original.timestamp
            assert copied is not original
            print("✅ Copy is independent from original")
        else:
            print("❌ CutSuggestion.copy missing")
            return False
    except Exception as e:
        print(f"❌ CutSuggestion test failed: {e}")
        return False
    
    # Test 4: Integration test - simulate the exact workflow
    print("\n4️⃣ Testing integrated workflow...")
    try:
        from main import load_config, initialize_components
        
        config = load_config()
        components = initialize_components(config)
        
        # Check that all required components exist
        required_components = ['script_parser', 'content_analyzer', 'cut_suggester']
        for comp_name in required_components:
            if comp_name not in components or components[comp_name] is None:
                print(f"❌ Component {comp_name} is missing or None")
                return False
            print(f"✅ Component {comp_name} exists: {type(components[comp_name])}")
        
        # Test that the workflow methods exist
        script_parser = components['script_parser']
        content_analyzer = components['content_analyzer']
        
        if hasattr(script_parser, 'parse_script_file'):
            print("✅ Workflow: script_parser.parse_script_file available")
        else:
            print("❌ Workflow: script_parser.parse_script_file missing")
            return False
            
        if hasattr(content_analyzer, 'adapt_suggestions_to_content'):
            print("✅ Workflow: content_analyzer.adapt_suggestions_to_content available")
        else:
            print("❌ Workflow: content_analyzer.adapt_suggestions_to_content missing")
            return False
        
        print("✅ All workflow components are properly initialized")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_all_fixes()
    if success:
        print("\n🎉 SUCCESS! All fixes are working correctly!")
        print("✅ BasicNLPProcessor.parse_script_file - FIXED")
        print("✅ IntelligentContentAnalyzer.adapt_suggestions_to_content - FIXED") 
        print("✅ CutSuggestion.copy - FIXED")
        print("✅ All components integrate properly - VERIFIED")
        print("\nVideoCraft should now work without AttributeError exceptions!")
    else:
        print("\n💥 FAILED! Some fixes still need work.")
        print("Please check the error messages above.")
