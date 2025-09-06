#!/usr/bin/env python3
"""
VideoCraft Backend Startup Script
Run this to start the backend server
"""
import os
import sys
import subprocess

def check_python():
    """Check if Python is available"""
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print(f"✅ Python {version.major}.{version.minor} detected")
            return True
        else:
            print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
            return False
    except:
        print("❌ Python not found")
        return False

def install_dependencies():
    """Install required packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def start_server():
    """Start the Flask server"""
    print("🚀 Starting VideoCraft Backend...")
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

def main():
    print("\n" + "="*50)
    print("🎬 VIDEOCRAFT BACKEND STARTUP")
    print("="*50)
    
    # Check Python
    if not check_python():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
