# VideoCraft - AI-Powered Video Analysis Platform

## 🚀 Deployment Guide

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Docker (optional, for containerized deployment)

### Environment Setup

#### Backend (.env)
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# AI Configuration
AI_MODE=simulation  # Set to 'real' for production AI models
ENABLE_REAL_AI=False

# File Storage
UPLOAD_DIR=./uploads
TEMP_DIR=./temp
PROCESSED_DIR=./processed
MAX_FILE_SIZE=100MB

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001", "https://your-domain.com"]
```

#### Frontend (.env.production)
```bash
REACT_APP_API_URL=https://your-api-domain.com
REACT_APP_VERSION=1.0.0
GENERATE_SOURCEMAP=false
```

### Deployment Options

#### Option 1: Docker Deployment (Recommended)
```bash
# Build and start with Docker Compose
docker-compose up -d --build

# Services will be available at:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

#### Option 2: Manual Deployment

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn simple_main_backup:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend:**
```bash
cd frontend
npm install
npm run build
npm install -g serve
serve -s build -l 3000
```

#### Option 3: Production Server (Nginx + PM2)

**Install PM2:**
```bash
npm install -g pm2
```

**Backend Process:**
```bash
cd backend
pm2 start "uvicorn simple_main_backup:app --host 0.0.0.0 --port 8000" --name videocraft-backend
```

**Frontend with Nginx:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /path/to/videocraft/frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Security Considerations

1. **HTTPS Setup** - Use SSL certificates for production
2. **File Upload Limits** - Configure appropriate file size limits
3. **CORS Configuration** - Restrict origins in production
4. **Rate Limiting** - Implement API rate limiting
5. **Input Validation** - All file uploads are validated

### Monitoring & Logging

- Backend logs are available via uvicorn
- Frontend errors can be tracked with error monitoring services
- File upload/processing metrics available in backend logs

### Performance Optimization

- Static files served with caching headers
- Video processing happens asynchronously
- Frontend code is optimized and minified
- API responses are compressed

### Scaling

- Backend can be horizontally scaled with load balancer
- File storage can be moved to cloud storage (S3, etc.)
- Database can be added for user management and project persistence

## 🔧 Features

### Core Functionality
✅ Video Upload & Processing
✅ AI-Powered Analysis (Scene Detection, Emotion Recognition)
✅ Video Editing Controls (Filters, Trimming, Effects)
✅ Smart Recommendations Engine
✅ Multiple Export Formats (Video, PDF Reports, JSON Data)
✅ Real-time Processing Feedback
✅ Responsive Design

### AI Capabilities
- Scene Detection and Classification
- Emotion Analysis
- Music Recommendation
- Background Removal Detection
- Intelligent Editing Suggestions

### Export Options
- Processed Video Download
- Professional PDF Reports
- Detailed Analysis Reports
- Raw JSON Data Export
- Fallback Mechanisms for Offline Use

## 🛡️ Production Checklist

- [x] Production build created and optimized
- [x] Environment variables configured
- [x] Error handling and fallbacks implemented
- [x] Security headers and CORS configured
- [x] File upload validation in place
- [x] Responsive design tested
- [x] Export functionality verified
- [x] AI simulation mode ready
- [x] Docker configuration available
- [x] Documentation complete

## 📦 Project Structure

```
VideoCraft/
├── backend/           # FastAPI server
├── frontend/         # React application
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── nginx.frontend.conf
```

## 🔗 API Endpoints

- `POST /upload` - Video upload
- `POST /analyze` - AI analysis
- `GET /recommendations` - Get recommendations
- `POST /export/video` - Export processed video
- `POST /export/report` - Export PDF report
- `POST /export/analysis` - Export analysis data
- `POST /export/data` - Export raw JSON data

Ready for production deployment! 🎬
