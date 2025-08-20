#!/usr/bin/env python3
"""
Install AI dependencies for VideoCraft
This script will install the required AI/ML packages
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("🚀 Installing AI dependencies for VideoCraft...")
    
    # Core AI packages
    ai_packages = [
        "torch",
        "torchvision", 
        "transformers==4.35.0",
        "opencv-python==4.8.1.78",
        "librosa==0.10.1", 
        "moviepy==1.0.3",
        "numpy==1.24.3",
        "scipy==1.11.4",
        "Pillow==10.0.1",
        "soundfile==0.12.1",
        "fer==22.5.1",
        "nltk==3.8.1",
        "mediapipe==0.10.7",
        "scikit-learn==1.3.2",
        "pandas==2.1.3"
    ]
    
    # Optional packages (install if possible)
    optional_packages = [
        "rembg==2.0.50",  # Background removal
        "spacy==3.7.2",   # Advanced NLP
    ]
    
    success_count = 0
    total_packages = len(ai_packages)
    
    print(f"Installing {total_packages} core AI packages...")
    
    for package in ai_packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installation Summary:")
    print(f"✅ Successfully installed: {success_count}/{total_packages} core packages")
    
    if success_count == total_packages:
        print("🎉 All core AI packages installed successfully!")
        
        # Try optional packages
        print("\n🔧 Installing optional packages...")
        optional_success = 0
        for package in optional_packages:
            if install_package(package):
                optional_success += 1
        
        print(f"✅ Optional packages installed: {optional_success}/{len(optional_packages)}")
        
    else:
        print("⚠️ Some packages failed to install. AI features may be limited.")
    
    print("\n🎯 AI Setup Complete!")
    print("The backend will automatically detect available AI models and use them.")
    print("If AI models are not available, the system will fallback to simulation mode.")

if __name__ == "__main__":
    main()
