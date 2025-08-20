# VideoCraft Real Implementation Setup
# PowerShell script for Windows users

Write-Host "🎬 VideoCraft Real Implementation Setup" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Check Python
Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check FFmpeg
try {
    ffmpeg -version 2>$null | Out-Null
    Write-Host "✅ FFmpeg is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ FFmpeg not found. Please install FFmpeg from https://ffmpeg.org/" -ForegroundColor Red
    Write-Host "   Download and add to PATH" -ForegroundColor Yellow
}

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Setup Backend
Write-Host "`n🔧 Setting up Python backend..." -ForegroundColor Yellow

Set-Location backend

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Cyan
python -m venv venv

# Activate and install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"
pip install -r requirements.txt

# Download NLTK data
Write-Host "Downloading NLTK data..." -ForegroundColor Cyan
python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"

Set-Location ..

# Setup Frontend
Write-Host "`n🔧 Setting up React frontend..." -ForegroundColor Yellow

Set-Location frontend

Write-Host "Installing Node.js dependencies..." -ForegroundColor Cyan
npm install

Set-Location ..

# Create environment files
Write-Host "`n📝 Creating environment configuration..." -ForegroundColor Yellow

# Backend .env
if (-not (Test-Path "backend\.env")) {
    @"
# VideoCraft Backend Configuration
DATABASE_URL=sqlite:///./videocraft.db
UPLOAD_DIR=uploads
PROCESSED_DIR=processed
DEBUG=True
HOST=0.0.0.0
PORT=8001
SECRET_KEY=your-secret-key-change-in-production
"@ | Out-File -FilePath "backend\.env" -Encoding UTF8
    Write-Host "✅ Created backend\.env" -ForegroundColor Green
}

# Frontend .env
if (-not (Test-Path "frontend\.env")) {
    @"
# VideoCraft Frontend Configuration
REACT_APP_API_URL=http://localhost:8001
PORT=3001
"@ | Out-File -FilePath "frontend\.env" -Encoding UTF8
    Write-Host "✅ Created frontend\.env" -ForegroundColor Green
}

Write-Host "`n🎉 Setup complete!" -ForegroundColor Green
Write-Host "`n🚀 To start the application:" -ForegroundColor Cyan
Write-Host "1. Backend: cd backend; python simple_main.py" -ForegroundColor White
Write-Host "2. Frontend: cd frontend; npm start" -ForegroundColor White
Write-Host "`n📱 Application will be available at:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3001" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8001" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8001/api/docs" -ForegroundColor White
