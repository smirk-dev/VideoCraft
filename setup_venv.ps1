# VideoCraft Environment Setup Script for Windows
# Run this script in PowerShell to create a clean virtual environment

Write-Host "🎬 VideoCraft Virtual Environment Setup" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+ first." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`n📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv videocraft_env

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
& ".\videocraft_env\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "⬆️ Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install PyTorch packages first
Write-Host "🔥 Installing PyTorch packages..." -ForegroundColor Yellow
python -m pip install torch>=2.6.0
python -m pip install torchaudio>=2.5.1
python -m pip install torchvision>=0.23.0

# Install numpy with constraints
Write-Host "🔢 Installing compatible numpy..." -ForegroundColor Yellow
python -m pip install "numpy>=2.0.2,<2.4.0"

# Install remaining requirements
Write-Host "📋 Installing remaining requirements..." -ForegroundColor Yellow
python -m pip install -r requirements.txt

# Download spacy language model
Write-Host "🗣️ Downloading English language model..." -ForegroundColor Yellow
python -m spacy download en_core_web_sm

# Check for conflicts
Write-Host "`n🔍 Checking for dependency conflicts..." -ForegroundColor Yellow
python -m pip check

Write-Host "`n🎉 Setup complete!" -ForegroundColor Green
Write-Host "To activate this environment in the future, run:" -ForegroundColor Cyan
Write-Host ".\videocraft_env\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "`nTo run VideoCraft:" -ForegroundColor Cyan
Write-Host "python main.py" -ForegroundColor White
