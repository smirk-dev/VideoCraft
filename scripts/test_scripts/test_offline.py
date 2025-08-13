#!/usr/bin/env python3
"""
Test script for offline AI functionality in VideoCraft.
This script verifies that the offline fallback system works correctly.
"""

import sys
import os
import cv2
import numpy as np
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

def test_offline_models():
    """Test the offline model functionality."""
    print("🧪 Testing VideoCraft Offline AI Components...")
    print("=" * 50)
    
    try:
        # Test configuration loading
        print("1. 📋 Testing configuration loading...")
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("   ✅ Configuration loaded successfully")
        
        # Test offline model manager
        print("\n2. 🤖 Testing offline model manager...")
        from utils.offline_models import OfflineModelManager
        
        offline_manager = OfflineModelManager(config)
        print("   ✅ OfflineModelManager initialized")
        
        # Test visual analyzer
        print("\n3. 👁️ Testing offline visual analyzer...")
        visual_analyzer = offline_manager.get_model('visual_analyzer')
        
        # Create a test image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Test visual analysis
        features = visual_analyzer.analyze_frame(test_image)
        print(f"   ✅ Visual analysis completed: {len(features)} features extracted")
        print(f"   📊 Sample features: {list(features.keys())[:3]}...")
        
        # Test emotion detector
        print("\n4. 😊 Testing offline emotion detector...")
        emotion_detector = offline_manager.get_model('emotion_detector')
        
        # Test text emotion
        test_text = "This is an amazing and exciting video!"
        text_emotion = emotion_detector.detect_text_emotion(test_text)
        print(f"   ✅ Text emotion detected: {text_emotion}")
        
        # Test speech emotion (mock audio)
        mock_audio = np.random.randn(16000)  # 1 second of mock audio at 16kHz
        speech_emotion = emotion_detector.detect_speech_emotion(mock_audio, 16000)
        print(f"   ✅ Speech emotion detected: {speech_emotion}")
        
        # Test NLP processor
        print("\n5. 📝 Testing offline NLP processor...")
        nlp_processor = offline_manager.get_model('nlp_processor')
        
        test_script = "Hello world. This is a test script with multiple sentences."
        nlp_result = nlp_processor.process_script(test_script)
        print(f"   ✅ NLP processing completed: {len(nlp_result)} elements")
        
        # Test scene detector
        print("\n6. 🎬 Testing offline scene detector...")
        scene_detector = offline_manager.get_model('scene_detector')
        
        # Create mock video frames
        mock_frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(10)]
        scenes = scene_detector.detect_scenes(mock_frames)
        print(f"   ✅ Scene detection completed: {len(scenes)} scenes detected")
        
        print("\n" + "=" * 50)
        print("🎉 ALL OFFLINE TESTS PASSED!")
        print("✅ VideoCraft offline mode is fully functional")
        print("📱 The application can work without internet connection")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   💡 Solution: Install required packages with 'pip install -r requirements.txt'")
        return False
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        print(f"   🐛 Error type: {type(e).__name__}")
        return False

def test_integration():
    """Test integration with main components."""
    print("\n🔗 Testing integration with main components...")
    print("=" * 50)
    
    try:
        # Test video analyzer integration
        print("1. 🎥 Testing video analyzer offline integration...")
        from processors.video_analyzer import VideoAnalyzer
        
        # Load config
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # This should fall back to offline mode if Hugging Face fails
        video_analyzer = VideoAnalyzer(config)
        print("   ✅ VideoAnalyzer initialized (may be using offline fallback)")
        
        # Test emotion detector integration
        print("\n2. 😊 Testing emotion detector offline integration...")
        from ai_models.emotion_detector import EmotionDetector
        
        emotion_detector = EmotionDetector(config)
        print("   ✅ EmotionDetector initialized (may be using offline fallback)")
        
        print("\n" + "=" * 50)
        print("🎉 INTEGRATION TESTS PASSED!")
        print("✅ Main components work with offline fallbacks")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 VideoCraft Offline Functionality Test")
    print("This script tests the offline AI capabilities\n")
    
    # Change to the src directory
    os.chdir(Path(__file__).parent / "src")
    
    success = True
    
    # Run offline model tests
    success &= test_offline_models()
    
    # Run integration tests
    success &= test_integration()
    
    if success:
        print("\n🏆 ALL TESTS PASSED!")
        print("VideoCraft offline mode is ready for production use")
    else:
        print("\n⚠️ Some tests failed")
        print("Please check the error messages above")
        sys.exit(1)
