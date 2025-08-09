#!/usr/bin/env python3
"""
Setup script for VideoCraft project.
This script helps manage dependencies and resolve version conflicts.
"""

import subprocess
import sys
import os

def run_command(command, description=""):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    if description:
        print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=False, text=True)
        print(f"✅ Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description}")
        print(f"Command failed with exit code: {e.returncode}")
        return False

def main():
    """Main setup function."""
    print("🎬 VideoCraft Setup Script")
    print("This script will set up your VideoCraft environment with compatible dependencies.")
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Error: requirements.txt not found. Please run this script from the VideoCraft directory.")
        sys.exit(1)
    
    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip", 
               "Upgrading pip to latest version")
    
    # Install core PyTorch packages first (in correct order)
    print("\n🔥 Installing PyTorch packages...")
    torch_packages = [
        "torch>=2.6.0",
        "torchaudio>=2.5.1", 
        "torchvision>=0.23.0"
    ]
    
    for package in torch_packages:
        run_command(f"{sys.executable} -m pip install --upgrade '{package}'",
                   f"Installing {package}")
    
    # Install numpy with version constraints
    run_command(f"{sys.executable} -m pip install 'numpy>=2.0.2,<2.4.0'",
               "Installing compatible numpy version")
    
    # Install remaining requirements
    run_command(f"{sys.executable} -m pip install -r requirements.txt",
               "Installing remaining requirements")
    
    # Download spacy language model
    run_command(f"{sys.executable} -m spacy download en_core_web_sm",
               "Downloading English language model for spacy")
    
    # Check for conflicts
    print("\n🔍 Checking for dependency conflicts...")
    result = subprocess.run(f"{sys.executable} -m pip check", 
                          shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ No dependency conflicts found!")
    else:
        print("⚠️  Some dependency conflicts detected:")
        print(result.stdout)
        print("\nNote: Some conflicts may be from packages not used in VideoCraft.")
        print("Consider creating a virtual environment for this project.")
    
    print("\n🎉 Setup complete!")
    print("You can now run: python main.py")

if __name__ == "__main__":
    main()
