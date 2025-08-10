#!/usr/bin/env python3
"""
Test script to verify all dependencies can be imported.
Run this to check if the deployment will work.
"""

import sys

def test_imports():
    """Test importing all required packages."""
    success = True
    failed_imports = []
    
    # Test core dependencies
    packages_to_test = [
        'streamlit',
        'yaml', 
        'cv2',
        'PIL',
        'numpy',
        'torch',
        'transformers',
        'librosa',
        'moviepy',
        'pandas',
        'sklearn',
        'scipy',
        'plotly',
        'matplotlib',
        'requests'
    ]
    
    print("Testing package imports...")
    print("-" * 40)
    
    for package in packages_to_test:
        try:
            if package == 'yaml':
                import yaml
            elif package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
            success = False
    
    print("-" * 40)
    
    if success:
        print("🎉 All imports successful! Deployment should work.")
    else:
        print(f"⚠️  {len(failed_imports)} packages failed to import:")
        for pkg in failed_imports:
            print(f"   - {pkg}")
        print("\nCheck your requirements.txt file.")
    
    return success

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
