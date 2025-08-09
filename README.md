# 🎬 AI Film Editor - Smart Cut & Transition Suggestions

An intelligent video editing assistant that analyzes video content and scripts to suggest optimal cut points and transitions using state-of-the-art AI models.

## ✨ Features

- **Scene Change Detection**: Automatically identify visual scene boundaries
- **Emotion Analysis**: Detect emotional beats in both script and speech
- **Speaker Recognition**: Identify speaker changes in dialogue
- **Smart Transitions**: Recommend appropriate transition types based on content
- **Interactive Timeline**: Visualize suggestions on an interactive timeline
- **No Training Required**: Uses pre-trained Hugging Face models

## 🚀 Quick Start

### Option 1: Virtual Environment (Recommended)

```powershell
# Create and activate virtual environment
.\setup_venv.ps1

# Or manually:
python -m venv videocraft_env
.\videocraft_env\Scripts\Activate.ps1
python setup.py
```

### Option 2: Direct Installation

```bash
# Install dependencies with automatic conflict resolution
python setup.py

# Or manually:
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run main.py
```

## ⚠️ Important Notes

### PyTorch Version Requirements

- **Security Update**: This project requires PyTorch ≥2.6.0 due to CVE-2025-32434
- Some older packages may have version conflicts with newer PyTorch
- A virtual environment is strongly recommended to avoid system-wide conflicts

### Dependency Conflicts

If you encounter version conflicts:

1. Use the provided virtual environment setup script
2. Check `requirements.txt` for compatible versions
3. Some packages (mediapipe, tensorflow, numba) may conflict with numpy ≥2.0 but are not used in VideoCraft

### Upload and Process

- Upload your video file (.mp4, .avi, .mov, .mkv)
- Upload corresponding script file (.txt, .srt)
- Click "Process Video" and review AI suggestions

## 🤖 AI Models Used

- **cardiffnlp/twitter-roberta-base-emotion**: Text emotion analysis
- **ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition**: Speech emotion
- **openai/clip-vit-base-patch32**: Visual content understanding
- **trpakov/vit-face-expression**: Facial emotion recognition

## 📁 Project Structure
```
ai-film-editor/
├── README.md
├── requirements.txt
├── .env.example
├── config.yaml
├── main.py
├── src/
│   ├── __init__.py
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── video_analyzer.py
│   │   ├── script_parser.py
│   │   ├── audio_analyzer.py
│   │   └── scene_detector.py
│   ├── ai_models/
│   │   ├── __init__.py
│   │   ├── emotion_detector.py
│   │   ├── sentiment_analyzer.py
│   │   └── visual_analyzer.py
│   ├── suggestions/
│   │   ├── __init__.py
│   │   ├── cut_suggester.py
│   │   └── transition_recommender.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── timeline_viewer.py
│   │   └── suggestion_panel.py
│   └── utils/
│       ├── __init__.py
│       ├── file_handler.py
│       └── timeline_sync.py
├── data/
│   ├── input/
│   ├── output/
│   └── cache/
└── tests/
    └── __init__.py
```

## ⚙️ Configuration

Modify `config.yaml` to adjust:
- Model preferences
- Processing thresholds
- Suggestion sensitivity
- Output formats

## 🔧 Advanced Usage

### Custom Thresholds
Adjust sensitivity in the sidebar:
- **Emotion Change Sensitivity**: How dramatic emotional changes need to be
- **Scene Change Sensitivity**: How different scenes need to be visually

### Suggestion Types
Filter suggestions by:
- Scene changes
- Emotional beats
- Speaker changes

## 📊 Output

The application provides:
- Interactive timeline with suggestions
- Confidence scores for each suggestion
- Reasoning for cut and transition recommendations
- Export options for editing software integration

## 🛠️ Development

To add new features:
1. Add new processors in `src/processors/`
2. Implement AI models in `src/ai_models/`
3. Create suggestion engines in `src/suggestions/`
4. Update UI components in `src/ui/`

## 📝 License

MIT License - Feel free to use and modify for your projects.
