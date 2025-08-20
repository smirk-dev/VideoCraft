#!/usr/bin/env python3
"""
VideoCraft AI Video Editor - Quick Start Script
This script helps set up and run the VideoCraft application quickly.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print the VideoCraft banner"""
    banner = """
    ╔══════════════════════════════════════════╗
    ║           VideoCraft AI Editor           ║
    ║     AI-Powered Video Editing Platform    ║
    ╚══════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def check_system_requirements():
    """Check system requirements"""
    print("\n🔍 Checking system requirements...")
    
    # Check Python
    check_python_version()
    
    # Check if we're in the right directory
    if not os.path.exists("backend/main.py"):
        print("❌ Please run this script from the VideoCraft project root directory")
        sys.exit(1)
    print("✅ Project structure verified")
    
    # Check if FFmpeg is available (optional but recommended)
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ FFmpeg detected")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  FFmpeg not found - video processing may be limited")
        print("   Install FFmpeg from: https://ffmpeg.org/download.html")

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Python dependencies installed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("Try installing manually with: pip install -r requirements.txt")
        return False
    
    return True

def install_frontend_dependencies():
    """Install frontend dependencies"""
    print("\n🌐 Installing frontend dependencies...")
    
    # Check if Node.js is available
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Node.js/npm not found - frontend will not be available")
        print("   Install Node.js from: https://nodejs.org/")
        return False
    
    try:
        # Change to frontend directory and install
        os.chdir("frontend")
        subprocess.run(["npm", "install"], check=True)
        os.chdir("..")
        print("✅ Frontend dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install frontend dependencies: {e}")
        os.chdir("..")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating necessary directories...")
    
    directories = [
        "uploads",
        "processed", 
        "temp",
        "logs",
        "static"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created/verified directory: {directory}")

def create_env_file():
    """Create environment file if it doesn't exist"""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print("\n⚙️  Creating environment configuration...")
        
        env_content = """# VideoCraft AI Video Editor Environment Configuration

# Application Settings
DEBUG=True
HOST=0.0.0.0
PORT=8000

# File Upload Settings
MAX_UPLOAD_SIZE=524288000  # 500MB

# AI Model Settings
USE_GPU=False
HF_CACHE_DIR=./models_cache

# API Keys (Optional - for enhanced features)
OPENAI_API_KEY=
HUGGINGFACE_API_KEY=

# Database (Optional)
DATABASE_URL=sqlite:///./videocraft.db

# Redis (Optional)
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-change-in-production

# Logging
LOG_LEVEL=INFO
"""
        
        with open(env_file, "w") as f:
            f.write(env_content)
        
        print(f"✅ Created {env_file} - you can modify settings there")
    else:
        print(f"✅ Found existing {env_file}")

def start_backend():
    """Start the FastAPI backend"""
    print("\n🚀 Starting VideoCraft AI backend...")
    print("Backend will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/api/docs")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        os.chdir("backend")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 VideoCraft backend stopped")
    finally:
        os.chdir("..")

def start_frontend():
    """Start the React frontend"""
    print("\n🌐 Starting VideoCraft frontend...")
    print("Frontend will be available at: http://localhost:3000")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        os.chdir("frontend")
        subprocess.run(["npm", "start"])
    except KeyboardInterrupt:
        print("\n👋 VideoCraft frontend stopped")
    except FileNotFoundError:
        print("❌ Frontend not available - Node.js/npm not found")
    finally:
        os.chdir("..")

def show_usage_info():
    """Show usage information"""
    print("""
📚 Usage Information:

1. Backend API Server:
   python setup.py --backend

2. Frontend Development Server:
   python setup.py --frontend

3. Full Setup (install dependencies):
   python setup.py --setup

4. Quick Start (backend only):
   python setup.py

API Endpoints:
- Upload: POST /api/upload/video or /api/upload/audio
- Analysis: POST /api/analyze/video
- Emotions: POST /api/emotion/video
- Music: POST /api/music/recommend
- Background: POST /api/background/remove
- Editing: POST /api/edit/trim

Documentation: http://localhost:8000/api/docs
""")

def main():
    """Main function"""
    print_banner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--setup":
            check_system_requirements()
            create_directories()
            create_env_file()
            
            if install_dependencies():
                install_frontend_dependencies()
                print("\n🎉 VideoCraft setup completed successfully!")
                print("\nRun 'python setup.py --backend' to start the backend server")
                print("Run 'python setup.py --frontend' to start the frontend server")
            
        elif command == "--backend":
            start_backend()
            
        elif command == "--frontend":
            start_frontend()
            
        elif command == "--help":
            show_usage_info()
            
        else:
            print(f"Unknown command: {command}")
            show_usage_info()
    
    else:
        # Default: quick start backend
        print("🚀 Quick Start Mode - Starting backend server...")
        print("Run 'python setup.py --help' for more options")
        check_system_requirements()
        create_directories()
        create_env_file()
        start_backend()

if __name__ == "__main__":
    main()
