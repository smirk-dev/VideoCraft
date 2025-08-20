# VideoCraft AI

<div align="center">

**Professional Video Editing with Intelligent Analysis**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18.2+-61DAFB.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](#status)

*A modern video editing platform with AI-powered analysis, built for professionals and creators*

[**Quick Start**](#quick-start) • [**Features**](#features) • [**Documentation**](docs/) • [**API Reference**](#api-reference)

</div>

---

## Features

### Core Capabilities

**🎥 Video Processing**
- Multi-format support (MP4, AVI, MOV, MKV, WebM, FLV)
- Real-time processing with live progress updates
- Advanced export options with quality controls
- Batch processing for multiple files

**🤖 AI-Powered Analysis**
- Intelligent scene detection and classification
- Facial emotion recognition and sentiment analysis
- Object detection and content recognition
- Audio transcription with speech-to-text
- Smart content recommendations

**✂️ Professional Editing**
- Timeline-based editing interface
- Real-time preview with instant feedback
- AI-suggested cuts and transitions
- Background removal and replacement
- Color grading and enhancement tools

**📊 Advanced Analytics**
- Engagement prediction algorithms
- Performance metrics and insights
- Content optimization suggestions
- Detailed analysis reports (PDF/JSON)

---

## Architecture

The project follows a clean, organized structure for maximum maintainability:

```text
VideoCraft/
├── backend/                 # FastAPI Python server
│   ├── app/                # Application logic
│   │   ├── api/           # REST endpoints
│   │   ├── core/          # Configuration
│   │   └── models/        # Data models
│   ├── uploads/           # File storage
│   ├── processed/         # Output files
│   └── simple_main_backup.py  # Production server
├── frontend/               # React application
│   ├── src/               # Source code
│   │   ├── components/    # UI components
│   │   ├── pages/         # Page views
│   │   └── services/      # API services
│   └── build/             # Production build
├── docs/                  # Documentation
├── scripts/               # Setup & start scripts
├── deployment/            # Docker & production
└── config/                # Configuration files
```

## Tech Stack

**Backend:** FastAPI, Python 3.8+, HuggingFace Transformers  
**Frontend:** React 18, Material-UI, Axios  
**AI Models:** DETR, Whisper, RoBERTa, MediaPipe  
**Deployment:** Docker, Nginx, Uvicorn

---

## Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control
- **2GB+ RAM** for AI processing

### Installation

**Option 1: Automated Setup (Recommended)**

```bash
git clone https://github.com/your-username/VideoCraft.git
cd VideoCraft
scripts/start-videocraft.ps1  # Windows PowerShell
# or
scripts/start-videocraft.bat  # Windows Command Prompt
```

**Option 2: Manual Setup**

1. **Clone & Navigate**
```bash
git clone https://github.com/your-username/VideoCraft.git
cd VideoCraft
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd ../frontend
npm install
```

4. **Start Services**
```bash
# Terminal 1 - Backend
cd backend && python simple_main_backup.py

# Terminal 2 - Frontend  
cd frontend && npm start
```

### Access Points

- **Application:** http://localhost:3001
- **API Documentation:** http://localhost:8001/docs
- **Interactive API:** http://localhost:8001/redoc

---

## Complete Usage Guide

### 1. Video Upload

**Drag & Drop Interface**
- Support for files up to 2GB
- Formats: MP4, AVI, MOV, MKV, WebM, FLV, M4V, 3GP
- Batch upload multiple files simultaneously
- Real-time upload progress tracking

**Upload Options:**
```javascript
// Supported formats
const formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'];
const maxSize = 2 * 1024 * 1024 * 1024; // 2GB
```

### 2. AI Analysis Features

**Automatic Processing**
Once uploaded, videos are analyzed using advanced AI:

- **Scene Detection:** Identifies scene changes and transitions
- **Emotion Analysis:** Detects facial expressions and emotional tone
- **Object Recognition:** Identifies people, objects, and activities
- **Audio Transcription:** Converts speech to searchable text
- **Quality Assessment:** Analyzes video and audio quality metrics

**Analysis Results:**
```json
{
  "scenes": [...],
  "emotions": [...],
  "objects": [...],
  "transcription": "...",
  "quality_score": 8.5
}
```

### 3. Professional Editing Tools

**Timeline Editor**
- Drag and drop clips onto timeline
- Precise cutting and trimming tools
- Real-time preview window
- Smooth transition effects
- Layer-based editing

**AI-Powered Enhancements**
- Smart background removal
- Automatic color correction
- Noise reduction for audio
- Intelligent cropping suggestions
- Content-aware scaling

### 4. Export & Sharing

**Multiple Export Formats**
- **Video Export:** MP4, AVI, MOV with quality options
- **PDF Reports:** Comprehensive analysis summaries
- **JSON Data:** Raw analysis data for developers
- **Project Files:** Save editing sessions

**Export API Example:**
```javascript
// Export video with custom settings
await exportService.exportVideo(projectId, {
  format: 'mp4',
  quality: 'high',
  resolution: '1920x1080'
});
```

### 5. Advanced Features

**Batch Processing**
Process multiple videos with consistent settings:

```bash
# API endpoint for batch processing
POST /api/batch/process
{
  "files": ["video1.mp4", "video2.mp4"],
  "settings": {"auto_enhance": true}
}
```

**Custom Workflows**
Create reusable editing templates:

```javascript
const workflow = {
  steps: [
    { type: 'analyze', settings: {...} },
    { type: 'enhance', settings: {...} },
    { type: 'export', format: 'mp4' }
  ]
};
```

---

## API Reference

### Core Endpoints

**Upload & File Management**
```http
POST   /api/upload/video      # Upload video files (up to 2GB)
GET    /api/upload/list       # List uploaded files
DELETE /api/upload/{filename} # Delete specific file
```

**AI Analysis**
```http
POST   /api/analyze/video     # Comprehensive video analysis
POST   /api/analyze/scenes    # Scene detection only
POST   /api/analyze/emotions  # Emotion recognition
POST   /api/analyze/objects   # Object detection
```

**Processing & Enhancement**
```http
POST   /api/process/enhance   # AI-powered enhancement
POST   /api/process/background # Background removal
POST   /api/process/color     # Color correction
POST   /api/process/audio     # Audio enhancement
```

**Export & Output**
```http
POST   /api/export/video      # Export processed video
POST   /api/export/report     # Generate PDF report
POST   /api/export/data       # Export JSON analysis
GET    /api/export/status     # Check export progress
```

### Authentication & Projects

```http
POST   /api/auth/login        # User authentication
GET    /api/projects          # List user projects
POST   /api/projects          # Create new project
PUT    /api/projects/{id}     # Update project
DELETE /api/projects/{id}     # Delete project
```

### Real-time Features

```http
GET    /api/status/{task_id}  # Get processing status
GET    /api/progress/{job_id} # Real-time progress updates
POST   /api/cancel/{task_id}  # Cancel running task
```

---

## Advanced Configuration

### Environment Setup

Create `.env` files for configuration:

**Backend Configuration (backend/.env)**
```env
# Server Settings
HOST=0.0.0.0
PORT=8001
DEBUG=false
WORKERS=4

# File Upload
MAX_UPLOAD_SIZE=2147483648  # 2GB
UPLOAD_DIR=./uploads
TEMP_DIR=./temp

# AI Models
USE_GPU=false
CACHE_DIR=./models_cache
MODEL_TIMEOUT=300

# Database
DATABASE_URL=sqlite:///./videocraft.db
```

**Frontend Configuration (frontend/.env)**
```env
REACT_APP_API_URL=http://localhost:8001
REACT_APP_MAX_FILE_SIZE=2147483648
PORT=3001
BROWSER=none
GENERATE_SOURCEMAP=false
```

### Production Deployment

**Docker Deployment**
```bash
cd deployment/
docker-compose -f docker-compose.production.yml up -d
```

**Manual Production Setup**
```bash
# Build frontend
cd frontend && npm run build

# Start production backend
cd backend && python simple_main_backup.py --production

# Configure Nginx (optional)
cp config/nginx.production.conf /etc/nginx/sites-available/videocraft
```

### Performance Tuning

**Backend Optimization**
```python
# Increase worker processes
uvicorn.run("main:app", workers=4, port=8001)

# Enable caching
CACHE_ENABLED=true
REDIS_URL=redis://localhost:6379
```

**Frontend Optimization**
```javascript
// Code splitting
const LazyComponent = lazy(() => import('./Component'));

// Bundle analysis
npm run build -- --analyze
```

---

## Development Guide

### Project Structure Best Practices

**Backend Organization**
```text
backend/app/
├── api/           # Route handlers
├── core/          # Configuration & utilities
├── models/        # Database models
├── services/      # Business logic
└── dependencies/  # Dependency injection
```

**Frontend Organization**
```text
frontend/src/
├── components/    # Reusable UI components
├── pages/         # Route-level components
├── services/      # API communication
├── hooks/         # Custom React hooks
├── context/       # Global state management
└── utils/         # Helper functions
```

### Adding New Features

**1. Backend API Endpoint**
```python
# backend/app/api/new_feature.py
from fastapi import APIRouter, Depends
from app.services.new_service import NewService

router = APIRouter()

@router.post("/new-feature")
async def create_feature(
    data: FeatureSchema,
    service: NewService = Depends()
):
    return await service.process(data)
```

**2. Frontend Integration**
```javascript
// frontend/src/services/newFeatureAPI.js
import axios from 'axios';

export const newFeatureAPI = {
  async process(data) {
    const response = await axios.post('/api/new-feature', data);
    return response.data;
  }
};
```

**3. React Component**
```jsx
// frontend/src/components/NewFeature.jsx
import { useState } from 'react';
import { newFeatureAPI } from '../services/newFeatureAPI';

export const NewFeature = () => {
  const [result, setResult] = useState(null);
  
  const handleProcess = async (data) => {
    const result = await newFeatureAPI.process(data);
    setResult(result);
  };
  
  return <div>...</div>;
};
```

### Testing

**Backend Tests**
```bash
cd backend
pip install pytest pytest-asyncio
pytest tests/ -v --cov=app
```

**Frontend Tests**
```bash
cd frontend
npm test -- --coverage --watchAll=false
```

**Integration Tests**
```bash
# Full application testing
scripts/test-integration.ps1
```

---

## Troubleshooting

### Common Issues & Solutions

**🔧 Server Won't Start**
```bash
# Check port availability
netstat -ano | findstr :8001
netstat -ano | findstr :3001

# Kill existing processes
taskkill /f /im python.exe
taskkill /f /im node.exe

# Use alternative ports
python simple_main_backup.py --port 8002
npm start -- --port 3002
```

**🔧 Upload Fails**
```bash
# Check disk space
dir c:\ | findstr "bytes free"

# Verify file permissions
icacls uploads /grant Everyone:F

# Clear temporary files
del /q temp\*.*
```

**🔧 AI Models Not Loading**
```bash
# Clear model cache
rmdir /s models_cache
mkdir models_cache

# Reinstall dependencies
pip uninstall transformers torch
pip install transformers torch --no-cache-dir
```

**🔧 Frontend Build Issues**
```bash
# Clear npm cache
npm cache clean --force

# Delete and reinstall
rmdir /s node_modules
del package-lock.json
npm install
```

### Performance Issues

**Memory Optimization**
```python
# Reduce model precision
import torch
model = model.half()  # Use 16-bit precision

# Limit batch size
BATCH_SIZE = 1  # For low-memory systems
```

**Network Optimization**
```javascript
// Implement request caching
const cache = new Map();
const cachedRequest = async (url) => {
  if (cache.has(url)) return cache.get(url);
  const result = await fetch(url);
  cache.set(url, result);
  return result;
};
```

---

## Contributing

### Development Workflow

1. **Fork & Clone**
```bash
git clone https://github.com/YOUR-USERNAME/VideoCraft.git
cd VideoCraft
git remote add upstream https://github.com/ORIGINAL-OWNER/VideoCraft.git
```

2. **Create Feature Branch**
```bash
git checkout -b feature/amazing-new-feature
```

3. **Development Setup**
```bash
# Install development dependencies
pip install -r backend/requirements-dev.txt
npm install --dev

# Enable pre-commit hooks
pre-commit install
```

4. **Make Changes & Test**
```bash
# Run tests
npm test
pytest

# Check code quality
npm run lint
flake8 backend/
```

5. **Submit Pull Request**
```bash
git add .
git commit -m "feat: add amazing new feature"
git push origin feature/amazing-new-feature
```

### Code Standards

**Python (Backend)**
- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for public methods
- Maintain 90%+ test coverage

**JavaScript (Frontend)**
- Use ESLint configuration
- Follow React best practices
- Implement proper error boundaries
- Use TypeScript for complex components

### Pull Request Guidelines

- **Clear Description:** Explain what and why
- **Tests Included:** Cover new functionality
- **Documentation Updated:** Update relevant docs
- **Breaking Changes:** Clearly marked and explained

---

## License & Credits

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Acknowledgments

**AI Models & Libraries**
- [HuggingFace](https://huggingface.co/) for transformer models
- [OpenAI](https://openai.com/) for Whisper speech recognition
- [Google](https://google.github.io/mediapipe/) for MediaPipe framework
- [Facebook Research](https://github.com/facebookresearch) for DETR object detection

**Frameworks & Tools**
- [FastAPI](https://fastapi.tiangolo.com/) for high-performance backend
- [React](https://reactjs.org/) for modern frontend development
- [Material-UI](https://mui.com/) for beautiful UI components
- [Docker](https://docker.com/) for containerization

### Contributors

<div align="center">

**Made with ❤️ by the VideoCraft AI Team**

[Report Bug](https://github.com/your-username/VideoCraft/issues) • [Request Feature](https://github.com/your-username/VideoCraft/issues) • [Join Discord](https://discord.gg/videocraft)

</div>

---

## Status

**Current Version:** 1.0.0  
**Last Updated:** August 2025  
**Production Ready:** ✅  
**Active Development:** ✅

For detailed project status, see [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)
