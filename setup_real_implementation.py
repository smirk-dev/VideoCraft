#!/usr/bin/env python3
"""
VideoCraft Setup Script for Real Implementation
Installs all dependencies and sets up the environment
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a command and handle errors"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    result = run_command("ffmpeg -version", check=False)
    if result and result.returncode == 0:
        print("✅ FFmpeg is installed")
        return True
    else:
        print("❌ FFmpeg not found. Please install FFmpeg:")
        print("   Windows: Download from https://ffmpeg.org/download.html")
        print("   macOS: brew install ffmpeg")
        print("   Ubuntu: sudo apt install ffmpeg")
        return False

def check_node():
    """Check if Node.js is installed"""
    result = run_command("node --version", check=False)
    if result and result.returncode == 0:
        print(f"✅ Node.js is installed: {result.stdout.strip()}")
        return True
    else:
        print("❌ Node.js not found. Please install Node.js from https://nodejs.org/")
        return False

def setup_backend():
    """Set up Python backend"""
    print("\n🔧 Setting up Python backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Create virtual environment
    print("Creating virtual environment...")
    result = run_command("python -m venv venv", cwd=backend_dir)
    if not result:
        return False
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate && pip install -r requirements.txt"
    else:  # macOS/Linux
        activate_cmd = "source venv/bin/activate && pip install -r requirements.txt"
    
    print("Installing Python dependencies...")
    result = run_command(activate_cmd, cwd=backend_dir)
    if not result:
        return False
    
    # Download NLTK data
    print("Downloading NLTK data...")
    nltk_cmd = f"{activate_cmd} && python -c \"import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')\""
    run_command(nltk_cmd, cwd=backend_dir, check=False)
    
    print("✅ Backend setup complete")
    return True

def setup_frontend():
    """Set up React frontend"""
    print("\n🔧 Setting up React frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install npm dependencies
    print("Installing Node.js dependencies...")
    result = run_command("npm install", cwd=frontend_dir)
    if not result:
        print("Trying with yarn...")
        result = run_command("yarn install", cwd=frontend_dir)
        if not result:
            return False
    
    print("✅ Frontend setup complete")
    return True

def create_env_files():
    """Create environment configuration files"""
    print("\n📝 Creating environment configuration...")
    
    # Backend .env
    backend_env = Path("backend/.env")
    if not backend_env.exists():
        with open(backend_env, 'w') as f:
            f.write("""# VideoCraft Backend Configuration
DATABASE_URL=sqlite:///./videocraft.db
UPLOAD_DIR=uploads
PROCESSED_DIR=processed
DEBUG=True
HOST=0.0.0.0
PORT=8001
SECRET_KEY=your-secret-key-change-in-production
""")
        print("✅ Created backend/.env")
    
    # Frontend .env
    frontend_env = Path("frontend/.env")
    if not frontend_env.exists():
        with open(frontend_env, 'w') as f:
            f.write("""# VideoCraft Frontend Configuration
REACT_APP_API_URL=http://localhost:8001
PORT=3000
""")
        print("✅ Created frontend/.env")

def main():
    """Main setup function"""
    print("🎬 VideoCraft Real Implementation Setup")
    print("=" * 50)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    
    if not check_python_version():
        return False
    
    if not check_ffmpeg():
        print("⚠️  FFmpeg is required for video processing. Setup will continue but video processing won't work.")
    
    if not check_node():
        return False
    
    # Setup components
    if not setup_backend():
        print("❌ Backend setup failed")
        return False
    
    if not setup_frontend():
        print("❌ Frontend setup failed")
        return False
    
    # Create configuration files
    create_env_files()
    
    print("\n🎉 Setup complete!")
    print("\n🚀 To start the application:")
    print("1. Backend: cd backend && source venv/bin/activate && python main.py")
    print("2. Frontend: cd frontend && npm start")
    print("\n📱 Application will be available at:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8001")
    print("   API Docs: http://localhost:8001/api/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
