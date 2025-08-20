# VideoCraft AI Video Editor - Development Guide

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Clone or navigate to the project
cd VideoCraft1

# Run the setup script
python setup.py --setup

# Start the backend
python setup.py --backend

# In another terminal, start the frontend
python setup.py --frontend
```

### Option 2: Manual Setup

#### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Navigate to backend directory
cd backend

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

## 🐳 Docker Deployment

### Development with Docker Compose
```bash
# Start all services
docker-compose up --build

# Start only backend and database
docker-compose up backend db redis

# Start in background
docker-compose up -d
```

### Production Deployment
```bash
# Start with production profile
docker-compose --profile production up -d
```

## 📁 Project Structure

```
VideoCraft1/
├── backend/                 # FastAPI Backend
│   ├── main.py             # Application entry point
│   ├── app/
│   │   ├── core/           # Core configuration
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   └── requirements.txt    # Python dependencies
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Utilities
│   └── package.json        # Node.js dependencies
├── uploads/                # Uploaded files
├── processed/              # Processed videos
├── temp/                   # Temporary files
├── logs/                   # Application logs
├── models_cache/           # AI models cache
└── static/                 # Static assets
```

## 🤖 AI Features

### Video Analysis
- **Object Detection**: DETR model for detecting objects in video frames
- **Scene Classification**: Image classification for scene understanding
- **Quality Assessment**: Video quality metrics and analysis
- **Scene Change Detection**: Automatic detection of scene transitions

### Emotion Detection
- **Facial Emotions**: Real-time facial emotion recognition
- **Audio Sentiment**: Speech emotion analysis
- **Text Sentiment**: Script and subtitle emotion analysis
- **Multi-modal Fusion**: Combined emotion insights

### Audio Processing
- **Speech Recognition**: Whisper for accurate transcription
- **Audio Enhancement**: Noise reduction and quality improvement
- **Feature Extraction**: Audio characteristics analysis
- **Silence Detection**: Automatic silence removal

### Background Removal
- **AI Segmentation**: rembg and MediaPipe for background removal
- **Background Replacement**: Custom background options
- **Real-time Processing**: Fast processing for video frames

### Music Recommendation
- **Mood Analysis**: AI-driven mood detection from content
- **Music Matching**: Intelligent music recommendation
- **Tempo Synchronization**: Beat matching with video rhythm

## 🛠️ Development Workflow

### Backend Development
1. **API Development**: Create new endpoints in `backend/app/api/`
2. **Model Integration**: Add AI models in respective service files
3. **Testing**: Use FastAPI's automatic documentation at `/api/docs`
4. **Logging**: Comprehensive logging configured in `logging_config.py`

### Frontend Development
1. **Component Creation**: Build reusable components in `frontend/src/components/`
2. **Page Development**: Create pages in `frontend/src/pages/`
3. **API Integration**: Use services in `frontend/src/services/`
4. **Styling**: Material-UI components and custom CSS

### AI Model Integration
1. **HuggingFace Models**: Download and cache models automatically
2. **Custom Models**: Add custom models in appropriate service files
3. **GPU Support**: Configure GPU usage in environment variables
4. **Model Optimization**: Use quantization and optimization techniques

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000

# File Upload
MAX_UPLOAD_SIZE=524288000  # 500MB

# AI Models
USE_GPU=False
HF_CACHE_DIR=./models_cache

# API Keys (Optional)
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_API_KEY=your_hf_key

# Database
DATABASE_URL=sqlite:///./videocraft.db

# Security
SECRET_KEY=your-secret-key
```

### AI Model Configuration
Models are automatically downloaded and cached. Configure in `config.py`:

```python
# Video Analysis Models
VIDEO_ANALYSIS_MODEL = "facebook/detr-resnet-50"
SCENE_CLASSIFICATION_MODEL = "google/vit-base-patch16-224"

# Emotion Models
FACIAL_EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"
AUDIO_EMOTION_MODEL = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"

# Audio Models
SPEECH_RECOGNITION_MODEL = "openai/whisper-base"
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

### API Testing
- Use the interactive documentation at `http://localhost:8000/api/docs`
- Test endpoints with curl or Postman
- Check logs in the `logs/` directory

## 🚀 Deployment

### Local Production
```bash
# Build and run with Docker
docker-compose --profile production up -d
```

### Cloud Deployment
1. **AWS/GCP/Azure**: Use container services
2. **Heroku**: Deploy with buildpacks
3. **DigitalOcean**: Use App Platform or Droplets
4. **Kubernetes**: Use provided Kubernetes manifests

### Performance Optimization
- **GPU Support**: Enable GPU for AI models
- **Caching**: Use Redis for model and result caching
- **CDN**: Serve static assets via CDN
- **Load Balancing**: Use multiple backend instances

## 📊 Monitoring

### Application Monitoring
- **Logs**: Structured logging with rotation
- **Health Checks**: Built-in health check endpoints
- **Metrics**: Performance and usage metrics

### AI Model Performance
- **Model Loading Time**: Monitor model initialization
- **Inference Speed**: Track processing times
- **Resource Usage**: Monitor CPU/GPU/Memory usage

## 🔒 Security

### API Security
- **CORS**: Configured for frontend domain
- **Rate Limiting**: Prevent API abuse
- **File Validation**: Strict file type checking
- **Size Limits**: Configurable upload limits

### Data Privacy
- **Temporary Storage**: Files cleaned up after processing
- **No Data Retention**: Files deleted after processing
- **Secure Upload**: Validated file uploads
- **Access Control**: Future user authentication

## 🐛 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip install -r requirements.txt

# Check port availability
netstat -an | grep 8000
```

#### Frontend Won't Start
```bash
# Check Node.js version
node --version  # Should be 14+

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

#### AI Models Not Loading
```bash
# Check HuggingFace cache directory
ls -la models_cache/

# Clear model cache
rm -rf models_cache/
# Models will re-download on next startup

# Check internet connection for model downloads
ping huggingface.co
```

#### FFmpeg Issues
```bash
# Install FFmpeg
# Windows: Download from https://ffmpeg.org/
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg

# Check FFmpeg installation
ffmpeg -version
```

### Debug Mode
Enable debug mode for detailed error information:

```env
DEBUG=True
LOG_LEVEL=DEBUG
```

### Performance Issues
- **Memory Usage**: Monitor RAM usage during video processing
- **GPU Memory**: Check GPU memory for AI models
- **Disk Space**: Ensure sufficient space for uploads and processing
- **Network**: Check bandwidth for model downloads

## 📚 API Documentation

### Upload Endpoints
- `POST /api/upload/video` - Upload video files
- `POST /api/upload/audio` - Upload audio files

### Analysis Endpoints
- `POST /api/analyze/video` - Comprehensive video analysis
- `POST /api/emotion/video` - Emotion detection in video
- `POST /api/emotion/audio` - Audio emotion analysis
- `POST /api/audio/analyze` - Audio processing and transcription

### Processing Endpoints
- `POST /api/background/remove` - Background removal
- `POST /api/music/recommend` - Music recommendation
- `POST /api/edit/trim` - Video trimming
- `POST /api/edit/merge` - Video merging

### Utility Endpoints
- `GET /api/health` - Health check
- `GET /api/supported-formats` - Supported file formats

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **HuggingFace**: For pre-trained AI models
- **FastAPI**: For the high-performance backend framework
- **React**: For the modern frontend framework
- **OpenCV**: For computer vision capabilities
- **MoviePy**: For video processing
- **Whisper**: For speech recognition

## 📞 Support

For support and questions:
- Check the [Issues](https://github.com/your-repo/VideoCraft1/issues) page
- Read the documentation
- Join our community discussions

---

**Happy Coding! 🎬✨**
