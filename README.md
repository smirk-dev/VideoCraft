# VideoCraft - AI-Powered Video Editing Assistant

A comprehensive video editing platform powered by Python and HuggingFace AI models.

## Features

### 🤖 AI-Powered Analysis
- **Video Analysis**: Automatic scene detection, object recognition, and content analysis
- **Emotion Detection**: Real-time emotion analysis using facial recognition and audio sentiment
- **Script Analysis**: NLP-powered script improvement suggestions and structure analysis
- **Audio Analysis**: Speech-to-text, noise detection, and audio quality assessment

### 🎵 Smart Recommendations
- **Music Recommendation**: Context-aware music suggestions based on video content and mood
- **Cut Suggestions**: AI-powered editing suggestions for optimal pacing and flow
- **Color Grading**: Automatic color correction and enhancement recommendations

### ✨ Advanced Editing Tools
- **Background Removal**: AI-powered background removal and replacement
- **In-Browser Editing**: Timeline-based video editing with real-time preview
- **Smart Cropping**: Intelligent video cropping and aspect ratio optimization
- **Text & Subtitle Generation**: Automatic subtitle generation and text overlay suggestions

## Architecture

```
VideoCraft/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   └── core/           # Core utilities
│   ├── requirements.txt
│   └── main.py
├── ai_models/              # HuggingFace AI models and processors
│   ├── video_analysis/     # Video content analysis
│   ├── emotion_detection/  # Emotion and sentiment analysis
│   ├── audio_processing/   # Audio analysis and transcription
│   ├── background_removal/ # Background removal models
│   └── music_recommendation/ # Music suggestion algorithms
├── frontend/               # React frontend (minimal, focused on UI)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
├── uploads/                # Temporary file storage
├── processed/              # Processed video output
└── requirements.txt        # Main Python dependencies
```

## Technology Stack

### Backend (Python)
- **FastAPI**: High-performance web framework
- **HuggingFace Transformers**: Pre-trained AI models
- **OpenCV**: Video processing and computer vision
- **MoviePy**: Video editing and manipulation
- **Librosa**: Audio analysis and processing
- **MediaPipe**: Real-time perception pipeline
- **PyTorch**: Deep learning framework

### Frontend (React)
- **React 18**: Modern UI framework
- **Material-UI**: Component library
- **Axios**: HTTP client for API communication
- **React Router**: Navigation and routing

### AI Models (HuggingFace)
- **facebook/detr-resnet-50**: Object detection
- **microsoft/DialoGPT-medium**: Conversational AI
- **openai/whisper-base**: Speech recognition
- **cardiffnlp/twitter-roberta-base-emotion**: Emotion analysis
- **facebook/musicgen-small**: Music generation

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- FFmpeg (for video processing)

### Setup

1. **Clone and navigate to project**
```bash
git clone <repository-url>
cd VideoCraft1
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install frontend dependencies**
```bash
npm install
```

4. **Start the development servers**
```bash
# Backend (Python FastAPI)
cd backend
uvicorn main:app --reload --port 8000

# Frontend (React)
npm start
```

## Usage

1. **Upload Video**: Drag and drop videos or use the upload interface
2. **AI Analysis**: Automatic analysis provides insights and suggestions
3. **Edit**: Use the timeline editor with AI-powered recommendations
4. **Export**: Generate and download your enhanced video

## API Endpoints

- `POST /api/upload` - Upload video files
- `POST /api/analyze/video` - Analyze video content
- `POST /api/analyze/emotion` - Detect emotions in video
- `POST /api/analyze/audio` - Process audio content
- `POST /api/recommend/music` - Get music recommendations
- `POST /api/edit/background-remove` - Remove video backgrounds
- `GET /api/projects` - List user projects

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
npm test
```

### Adding New AI Models
1. Add model configuration in `ai_models/`
2. Create service class in `backend/app/services/`
3. Add API endpoint in `backend/app/api/`
4. Update frontend interface

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details.