# 🎬 VideoCraft AI - Professional Video Editing Assistant

> **🚀 STABLE & RELIABLE**: This project features a **simplified backend** for reliable functionality, **working video analysis**, and **complete frontend integration**. The simple backend is now the default for better stability.

A video editing platform with intelligent analysis capabilities. Built with Python FastAPI backend and React frontend, designed for stability and ease of use.

## ✨ Current Features (Stable Implementation)

### 🎥 **Video Processing**
- **File Upload**: Support for multiple video formats (MP4, AVI, MOV, MKV, etc.)
- **Video Analysis**: Automated content analysis with structured results
- **Real-time Processing**: Live progress updates and status tracking
- **Export Functionality**: Download processed videos and analysis reports

### 🤖 **AI Analysis (Simplified)**
- **Scene Detection**: Smart scene classification and content analysis
- **Object Recognition**: Automated object and element detection
- **Emotion Analysis**: Facial expression and mood detection
- **Audio Processing**: Speech recognition and audio analysis

### � **Data Management**
- **File Storage**: Organized upload and processing directories
- **Analysis Reports**: Structured JSON analysis data
- **Project Management**: Save and manage editing projects
- **Progress Tracking**: Real-time status updates

### 🔗 **Full Integration**
- **REST API**: Complete backend-frontend communication
- **File Uploads**: Drag & drop file upload interface
- **Real-time Updates**: Live progress and status updates
- **Error Handling**: Comprehensive error management
- **Background Removal**: AI-powered background removal and replacement
- **Color Grading**: Automatic color correction and cinematic enhancement
- **Smart Cropping**: Intelligent aspect ratio optimization
- **Visual Effects**: AI-assisted visual enhancement and filtering

### ⚡ Professional Editing Suite
- **Timeline Editor**: Professional timeline-based editing interface
- **Real-time Preview**: Instant video preview with applied changes
- **Cut Suggestions**: AI-powered editing recommendations for optimal pacing
- **Batch Processing**: Handle multiple videos with automated workflows
- **Project Management**: Organize and manage editing projects efficiently

### 📊 Analytics & Insights
- **Performance Metrics**: Detailed video performance analysis
- **Engagement Prediction**: AI-powered audience engagement forecasting
- **Content Optimization**: Suggestions for improving video performance
- **Export Analytics**: Comprehensive reports on video metrics

## 🏗️ Project Architecture

> **📁 Organized Structure**: The project is now organized with clear separation of concerns for better maintainability and accessibility.

```
VideoCraft/
├── 🐍 backend/                      # FastAPI Python Backend
│   ├── app/
│   │   ├── api/                     # REST API Endpoints
│   │   │   ├── upload.py            # File upload handling (2GB support)
│   │   │   ├── video_analysis.py    # Video AI analysis
│   │   │   ├── emotion_detection.py # Emotion & sentiment analysis
│   │   │   ├── audio_analysis.py    # Audio processing & transcription
│   │   │   ├── music_recommendation.py # Smart music suggestions
│   │   │   ├── background_removal.py # AI background processing
│   │   │   └── video_editing.py     # Video editing operations
│   │   ├── core/
│   │   │   ├── config.py            # Application configuration
│   │   │   └── logging_config.py    # Logging setup
│   │   └── models/                  # Data models and schemas
│   ├── uploads/                     # Uploaded files storage (gitignored)
│   ├── processed/                   # Processed video outputs (gitignored)
│   ├── temp/                        # Temporary processing files (gitignored)
│   ├── requirements.txt             # Python dependencies
│   ├── simple_main_backup.py        # Production backend server
│   └── .env.production             # Production environment config
├── ⚛️ frontend/                     # React Frontend Application
│   ├── src/
│   │   ├── components/
│   │   │   └── Navbar.js           # Navigation component
│   │   ├── pages/
│   │   │   ├── HomePage.js         # Landing page with features
│   │   │   ├── UploadPage.js       # File upload interface (2GB support)
│   │   │   ├── EditorPage.js       # Timeline-based video editor
│   │   │   ├── AnalysisPage.js     # AI analysis dashboard
│   │   │   └── ProjectsPage.js     # Project management
│   │   ├── services/
│   │   │   └── exportService.js    # Complete export functionality
│   │   ├── App.js                 # Main React application
│   │   └── index.js               # React DOM entry point
│   ├── build/                     # Production build (334KB gzipped)
│   ├── public/                    # Static assets
│   ├── package.json              # Node.js dependencies
│   └── .env.production           # Production environment config
├── � docs/                       # All Documentation
│   ├── DEPLOYMENT.md              # Deployment instructions
│   ├── DEVELOPMENT.md             # Development setup guide
│   ├── PRODUCTION_CHECKLIST.md    # Pre-deployment checklist
│   ├── READY_TO_DEPLOY.md         # Final deployment summary
│   ├── FUNCTIONALITY_STATUS.md    # Feature status tracking
│   └── PROJECT_STATUS.md          # Overall project status
├── � scripts/                    # Development Scripts
│   ├── start-custom-ports.bat     # Windows: Start with custom ports
│   ├── start-custom-ports.ps1     # PowerShell: Start with custom ports
│   ├── start-simple-backend.bat   # Windows: Start backend only
│   ├── start-videocraft.ps1       # PowerShell: Start full application
│   └── setup_real_implementation.py # AI setup script
├── 🐳 deployment/                 # Production Deployment
│   ├── docker-compose.yml         # Development Docker setup
│   ├── docker-compose.production.yml # Production Docker setup
│   ├── Dockerfile.backend         # Backend Docker image
│   └── Dockerfile.frontend        # Frontend Docker image
├── ⚙️ config/                     # Configuration Files
│   ├── nginx.frontend.conf        # Nginx config for frontend
│   ├── nginx.production.conf      # Production Nginx config
│   ├── .env.example              # Environment variables template
│   └── requirements.txt          # Global Python requirements
├── 📄 PROJECT_STRUCTURE.md        # Detailed structure documentation
├── 🔧 .env                       # Local environment variables
├── 🔒 .gitignore                 # Git exclusion rules
├── 📋 LICENSE                    # MIT License
└── 📖 README.md                  # This file
```

## 🛠️ Technology Stack

### Backend Technologies
| Technology | Purpose | Version |
|------------|---------|---------|
| **FastAPI** | High-performance web framework | Latest |
| **Python** | Core backend language | 3.8+ |
| **HuggingFace Transformers** | Pre-trained AI models | 4.36+ |
| **PyTorch** | Deep learning framework | 2.1+ |
| **OpenCV** | Computer vision and video processing | 4.8+ |
| **MoviePy** | Video editing and manipulation | 1.0+ |
| **Librosa** | Audio analysis and processing | 0.10+ |
| **Whisper** | Speech recognition and transcription | Latest |
| **MediaPipe** | Real-time perception pipeline | 0.10+ |
| **Uvicorn** | ASGI server for FastAPI | Latest |

### Frontend Technologies
| Technology | Purpose | Version |
|------------|---------|---------|
| **React** | Modern UI framework | 18.2+ |
| **Material-UI (MUI)** | Component library and design system | 5.14+ |
| **React Router** | Client-side routing | 6.8+ |
| **Axios** | HTTP client for API communication | 1.6+ |
| **React Dropzone** | File upload with drag & drop | 14.2+ |

### AI Models & Services
| Model | Provider | Use Case |
|-------|----------|----------|
| **DETR ResNet-50** | Facebook | Object detection and recognition |
| **Whisper Base** | OpenAI | Speech-to-text transcription |
| **RoBERTa Emotion** | Cardiff NLP | Emotion classification |
| **U2Net** | Various | Background removal |
| **MediaPipe Face** | Google | Facial landmark detection |
| **Various Audio Models** | HuggingFace | Audio analysis and enhancement |

### Development & Deployment
| Tool | Purpose |
|------|---------|
| **Docker** | Containerization and deployment |
| **Git** | Version control |
| **PowerShell/Batch** | Startup automation scripts |
| **Nginx** | Production web server (optional) |

## 🚀 Quick Start Guide

### Prerequisites
Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/)
- **FFmpeg** (Optional) - For advanced video processing

### � Quick Setup (Real Implementation)

#### Automated Setup (Recommended)

1. **Clone the Repository**
```bash
git clone https://github.com/your-username/VideoCraft.git
cd VideoCraft
```

2. **Run Real Implementation Setup**

**Windows:**
```powershell
python scripts/setup_real_implementation.py
```

**Or use PowerShell script:**
```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_real_implementation.ps1
```

3. **Start the Application**

**Backend (Terminal 1):**
```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # macOS/Linux
python main.py
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm start
```

#### What the Setup Includes

✅ **Real Video Processing**: FFmpeg integration for actual video editing  
✅ **AI Models**: HuggingFace transformers for genuine analysis  
✅ **Database**: SQLAlchemy with SQLite for project persistence  
✅ **Full API**: Complete REST API with all endpoints functional  
✅ **Dependencies**: All required Python and Node.js packages  

### 📥 Manual Installation

#### Prerequisites

- **Python 3.8+** - [Download Python](https://www.python.org/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/)
- **FFmpeg** - [Download FFmpeg](https://ffmpeg.org/) (Required for video processing)

### �📥 Installation

#### Method 1: Automated Setup (Recommended)

1. **Clone the Repository**
```bash
git clone https://github.com/your-username/VideoCraft.git
cd VideoCraft
```

2. **Run the Automated Startup Script**

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File scripts/start-custom-ports.ps1
```

**Windows (Command Prompt):**
```batch
scripts/start-custom-ports.bat
```

The script will:
- Set up Python virtual environment
- Install all dependencies
- Configure ports to avoid conflicts
- Launch both backend and frontend servers

#### Method 2: Manual Setup

1. **Clone and Navigate**
```bash
git clone https://github.com/your-username/VideoCraft.git
cd VideoCraft
```

2. **Setup Python Environment**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

3. **Install Backend Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Install Frontend Dependencies**
```bash
cd ../frontend
npm install
```

5. **Start the Servers**

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### 🌐 Access the Application

- **Frontend Interface**: http://localhost:3001
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/api/docs
- **Alternative API Docs**: http://localhost:8001/api/redoc

### 🎯 Port Configuration

The application uses custom ports to avoid conflicts:
- **Backend**: Port 8001 (instead of default 8000)
- **Frontend**: Port 3001 (instead of default 3000)
- **Alternative ports**: 8002/3002, 8080/3080 available via startup scripts

## 📖 Usage Guide

### 1. 📤 Upload Videos
- **Drag & Drop**: Simply drag video files onto the upload area
- **File Selection**: Click to browse and select files
- **Supported Formats**: MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V, 3GP
- **File Size**: Up to 2GB per file
- **Batch Upload**: Upload multiple files simultaneously

### 2. 🤖 AI Analysis
Once uploaded, your videos are automatically analyzed:

- **Scene Detection**: Identifies scene changes and transitions
- **Emotion Analysis**: Detects emotions in faces and voice
- **Audio Transcription**: Converts speech to text
- **Content Recognition**: Identifies objects, people, and activities
- **Quality Assessment**: Analyzes video and audio quality

### 3. ✂️ Video Editing
Use the professional timeline editor:

- **Timeline Interface**: Drag and drop clips on the timeline
- **Real-time Preview**: See changes instantly
- **AI Suggestions**: Get intelligent editing recommendations
- **Cut Tools**: Precise cutting and trimming
- **Transitions**: Add smooth transitions between clips
- **Effects**: Apply filters and visual effects

### 4. 🎨 Enhancement Tools
Apply AI-powered enhancements:

- **Background Removal**: Remove or replace backgrounds
- **Color Correction**: Automatic color grading
- **Audio Enhancement**: Noise reduction and audio improvement
- **Smart Cropping**: Optimize for different aspect ratios

### 5. 📊 Analytics & Insights
View comprehensive analysis:

- **Emotion Timeline**: Track emotional changes
- **Scene Breakdown**: Detailed scene analysis
- **Audio Metrics**: Volume levels and speech quality
- **Engagement Predictions**: AI-powered performance forecasts

### 6. 💾 Export & Share
Download your enhanced videos:

- **Multiple Formats**: Export in various video formats
- **Quality Options**: Choose from different quality settings
- **Quick Share**: Generate shareable links
- **Project Saving**: Save projects for future editing

## 🔧 Configuration Options

### Environment Variables
Create a `.env` file in the root directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8001
DEBUG=false

# File Upload Settings
MAX_UPLOAD_SIZE=2147483648  # 2GB in bytes

# AI Model Settings
USE_GPU=false
HF_CACHE_DIR=./models_cache

# Database (Optional)
DATABASE_URL=sqlite:///./videocraft.db
```

### Frontend Configuration
Edit `frontend/.env.local`:

```env
REACT_APP_API_URL=http://localhost:8001
PORT=3001
BROWSER=none
```

## 🔌 API Reference

### Upload Endpoints
| Method | Endpoint | Description | Max Size |
|--------|----------|-------------|----------|
| `POST` | `/api/upload/video` | Upload video files | 2GB |
| `POST` | `/api/upload/audio` | Upload audio files | 2GB |
| `POST` | `/api/upload/multiple` | Batch upload files | 10 files |
| `GET` | `/api/upload/list` | List uploaded files | - |
| `DELETE` | `/api/upload/delete/{filename}` | Delete uploaded file | - |

### Analysis Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analyze/video` | Comprehensive video analysis |
| `POST` | `/api/analyze/scenes` | Scene detection and classification |
| `POST` | `/api/analyze/objects` | Object detection and tracking |
| `POST` | `/api/analyze/quality` | Video quality assessment |

### Emotion & Audio Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/emotion/detect` | Facial emotion detection |
| `POST` | `/api/emotion/timeline` | Emotion analysis over time |
| `POST` | `/api/audio/transcribe` | Speech-to-text conversion |
| `POST` | `/api/audio/analyze` | Audio quality and metrics |
| `POST` | `/api/audio/enhance` | Audio enhancement and cleanup |

### Enhancement Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/background/remove` | AI background removal |
| `POST` | `/api/background/replace` | Background replacement |
| `POST` | `/api/edit/color-correct` | Automatic color correction |
| `POST` | `/api/edit/enhance` | Video quality enhancement |

### Music & Recommendations
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/music/recommend` | Get music recommendations |
| `POST` | `/api/music/analyze` | Analyze music compatibility |
| `GET` | `/api/music/genres` | List available music genres |

### Project Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/projects` | List user projects |
| `POST` | `/api/projects` | Create new project |
| `PUT` | `/api/projects/{id}` | Update project |
| `DELETE` | `/api/projects/{id}` | Delete project |

### System Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/info` | API information |
| `GET` | `/` | Web interface |
| `GET` | `/api/docs` | Swagger documentation |

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Build and Run**
```bash
cd deployment/
docker-compose up --build
```

2. **Production Deployment**
```bash
cd deployment/
docker-compose -f docker-compose.production.yml up -d
```

### Manual Docker Build

**Backend:**
```bash
docker build -f Dockerfile.backend -t videocraft-backend .
docker run -p 8001:8001 videocraft-backend
```

**Frontend:**
```bash
docker build -f Dockerfile.frontend -t videocraft-frontend .
docker run -p 3001:3001 videocraft-frontend
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
pip install pytest pytest-asyncio
pytest tests/ -v
```

### Frontend Testing
```bash
cd frontend
npm test
```

### API Testing
Use the interactive API documentation:
- **Swagger UI**: http://localhost:8001/api/docs
- **ReDoc**: http://localhost:8001/api/redoc

### Manual Testing Checklist
- [ ] File upload (small and large files up to 2GB)
- [ ] Video analysis processing
- [ ] Emotion detection accuracy
- [ ] Audio transcription quality
- [ ] Background removal functionality
- [ ] Timeline editor responsiveness
- [ ] Export functionality

## 🔧 Development

### Project Structure Guidelines
- **Backend**: Follow FastAPI best practices
- **Frontend**: Use React functional components with hooks
- **AI Models**: Implement lazy loading for better performance
- **API**: RESTful design with clear error handling

### Adding New Features

1. **Backend Endpoint**
```python
# backend/app/api/new_feature.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/new-endpoint")
async def new_endpoint():
    return {"message": "New feature"}
```

2. **Frontend Integration**
```javascript
// frontend/src/services/api.js
export const newFeatureAPI = async (data) => {
  return await axios.post('/api/new-endpoint', data);
};
```

### Code Style
- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Use ESLint and Prettier
- **Commits**: Follow conventional commit format

### Performance Optimization
- Use async/await for I/O operations
- Implement caching for AI model results
- Optimize file handling for large uploads
- Use React.memo for expensive components

## 🚨 Troubleshooting

### Common Issues

**🔍 Server Won't Start**
```bash
# Check if ports are available
netstat -ano | findstr :8001
netstat -ano | findstr :3001

# Use alternative ports
python main.py --port 8002
npm start -- --port 3002
```

**🔍 Upload Fails for Large Files**
- Ensure 2GB limit is configured in both frontend and backend
- Check available disk space
- Verify network stability for large uploads

**🔍 AI Models Not Loading**
```bash
# Clear HuggingFace cache
rm -rf ~/.cache/huggingface/

# Reinstall transformers
pip uninstall transformers
pip install transformers
```

**🔍 Frontend Build Errors**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**🔍 Permission Errors (Windows)**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Getting Help
- **Issues**: Create a GitHub issue with detailed description
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check `/api/docs` for API reference

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit with conventional commit format
7. Push to your fork: `git push origin feature/amazing-feature`
8. Create a Pull Request

### Contribution Guidelines
- **Code Quality**: Maintain high code quality standards
- **Testing**: Add tests for new features
- **Documentation**: Update documentation for changes
- **Performance**: Consider performance impact
- **Compatibility**: Ensure cross-platform compatibility

### Areas for Contribution
- 🆕 New AI models integration
- 🎨 UI/UX improvements
- 📱 Mobile responsiveness
- 🔧 Performance optimizations
- 📚 Documentation improvements
- 🧪 Test coverage expansion

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- HuggingFace Transformers: Apache 2.0
- FastAPI: MIT
- React: MIT
- Material-UI: MIT

## 🙏 Acknowledgments

- **HuggingFace** for providing excellent pre-trained models
- **OpenAI** for Whisper speech recognition
- **Google** for MediaPipe framework
- **Facebook** for PyTorch and computer vision models
- **React** and **FastAPI** communities for excellent frameworks

## 📊 Project Stats

- **Languages**: Python, JavaScript, TypeScript
- **Backend**: FastAPI with 15+ AI models
- **Frontend**: React with Material-UI
- **File Support**: 2GB uploads, 10+ video formats
- **AI Features**: 6 major AI capabilities
- **API Endpoints**: 25+ RESTful endpoints

---

**Made with ❤️ by the VideoCraft AI Team**

For more information, visit our [documentation](./DEVELOPMENT.md) or check out the [live demo](http://localhost:3001).
