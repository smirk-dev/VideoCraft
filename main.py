import streamlit as st
import yaml
import os
import tempfile
from pathlib import Path
import logging
import time
import threading
from PIL import Image
import cv2
import base64
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules with error handling
try:
    from src.processors.video_analyzer import VideoAnalyzer
except ImportError as e:
    logger.warning(f"VideoAnalyzer import failed: {e}")
    VideoAnalyzer = None

try:
    from src.processors.script_parser import ScriptParser
except ImportError as e:
    logger.warning(f"ScriptParser import failed: {e}")
    ScriptParser = None

try:
    from src.processors.audio_analyzer import AudioAnalyzer
except ImportError as e:
    logger.warning(f"AudioAnalyzer import failed: {e}")
    AudioAnalyzer = None

try:
    from src.processors.scene_detector import SceneDetector
except ImportError as e:
    logger.warning(f"SceneDetector import failed: {e}")
    SceneDetector = None

try:
    from src.ai_models.emotion_detector import EmotionDetector
except ImportError as e:
    logger.warning(f"EmotionDetector import failed: {e}")
    EmotionDetector = None

try:
    from src.ai_models.advanced_emotion_detector import AdvancedEmotionDetector
except ImportError as e:
    logger.warning(f"AdvancedEmotionDetector import failed: {e}")
    AdvancedEmotionDetector = None

try:
    from src.processors.video_editor import VideoEditor
except ImportError as e:
    logger.warning(f"VideoEditor import failed: {e}")
    VideoEditor = None

try:
    from src.processors.realtime_processor import RealTimeProcessor
except ImportError as e:
    logger.warning(f"RealTimeProcessor import failed: {e}")
    RealTimeProcessor = None

try:
    from src.exporters.professional_exporter import ProfessionalExporter
except ImportError as e:
    logger.warning(f"ProfessionalExporter import failed: {e}")
    ProfessionalExporter = None

try:
    from src.suggestions.cut_suggester import CutSuggester
except ImportError as e:
    logger.warning(f"CutSuggester import failed: {e}")
    CutSuggester = None

try:
    from src.suggestions.transition_recommender import TransitionRecommender
except ImportError as e:
    logger.warning(f"TransitionRecommender import failed: {e}")
    TransitionRecommender = None

try:
    from src.ui.timeline_viewer import TimelineViewer
except ImportError as e:
    logger.warning(f"TimelineViewer import failed: {e}")
    TimelineViewer = None

try:
    from src.ui.suggestion_panel import SuggestionPanel
except ImportError as e:
    logger.warning(f"SuggestionPanel import failed: {e}")
    SuggestionPanel = None

try:
    from src.utils.file_handler import FileHandler
except ImportError as e:
    logger.warning(f"FileHandler import failed: {e}")
    FileHandler = None

try:
    from src.utils.timeline_sync import TimelineSync
except ImportError as e:
    logger.warning(f"TimelineSync import failed: {e}")
    TimelineSync = None

# Import advanced AI components
try:
    from src.ai_models.intelligent_content_analyzer import IntelligentContentAnalyzer
except ImportError as e:
    logger.warning(f"IntelligentContentAnalyzer import failed: {e}")
    IntelligentContentAnalyzer = None

try:
    from src.ai_models.music_sync_engine import MusicSyncEngine
except ImportError as e:
    logger.warning(f"MusicSyncEngine import failed: {e}")
    MusicSyncEngine = None

try:
    from src.ai_models.user_learning_system import AIUserLearningSystem
except ImportError as e:
    logger.warning(f"AIUserLearningSystem import failed: {e}")
    AIUserLearningSystem = None

try:
    from src.ui.interactive_timeline_editor import InteractiveTimelineEditor
except ImportError as e:
    logger.warning(f"InteractiveTimelineEditor import failed: {e}")
    InteractiveTimelineEditor = None

try:
    from src.utils.cloud_integration import CloudIntegrationManager
except ImportError as e:
    logger.warning(f"CloudIntegrationManager import failed: {e}")
    CloudIntegrationManager = None

def load_config():
    """Load configuration from YAML file."""
    try:
        with open('config.yaml', 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.warning("config.yaml not found. Using default configuration.")
        # Return default configuration for cloud deployment
        return {
            'ai_models': {
                'clip_model': 'openai/clip-vit-base-patch32',
                'emotion_model': 'j-hartmann/emotion-english-distilroberta-base',
                'cache_dir': './cache'
            },
            'suggestions': {
                'scene_change_threshold': 0.4,
                'emotion_change_threshold': 0.3,
                'min_segment_length': 2.0
            },
            'video': {
                'max_file_size_mb': 500,
                'supported_formats': ['.mp4', '.avi', '.mov', '.mkv']
            },
            'processing': {
                'batch_size': 8,
                'num_workers': 2
            }
        }
    except yaml.YAMLError as e:
        logger.error(f"Error loading config.yaml: {e}")
        st.error("Error in configuration file format.")
        return None

def initialize_components(config):
    """Initialize all processing components with advanced AI features and offline fallbacks.

    In environments where heavy ML dependencies (torch, transformers, etc.) are not installed
    we allow a lightweight test mode by setting the environment variable LIGHT_TEST_MODE=1.
    This returns only the minimal components required for parsing tests.
    """
    # Lightweight path for tests
    if os.environ.get('LIGHT_TEST_MODE') == '1':
        try:
            from src.utils.offline_models import OfflineModelManager
            offline_manager = OfflineModelManager(config)
        except Exception:
            offline_manager = None
        # Provide a minimal script parser substitute if real one can't load
        try:
            from src.processors.script_parser import ScriptParser as ScriptParserClass  # may fail
            script_parser = ScriptParserClass(config)
        except Exception:
            # Minimal fallback with parse_script_file method
            class _BasicParser:
                def parse_script_file(self, path):
                    return []
            script_parser = _BasicParser()
        return {
            'script_parser': script_parser,
            'offline_manager': offline_manager
        }
    try:
        # Import offline model manager for fallback support
        from src.utils.offline_models import OfflineModelManager
        
        # Initialize offline manager first
        offline_manager = OfflineModelManager(config)
        
        components = {}
        
        # Initialize components with error handling
        try:
            from src.processors.video_analyzer import VideoAnalyzer as VideoAnalyzerClass
            components['video_analyzer'] = VideoAnalyzerClass(config)
            logger.info("✅ Video analyzer initialized")
        except Exception as e:
            logger.warning(f"⚠️ Video analyzer failed to initialize: {e}")
            fallback_analyzer = offline_manager.get_model('visual_analyzer')
            if fallback_analyzer is None:
                from src.utils.offline_models import BasicVisualAnalyzer
                fallback_analyzer = BasicVisualAnalyzer()
            components['video_analyzer'] = fallback_analyzer
            logger.info("✅ Video analyzer initialized with offline fallback")
        
        try:
            from src.processors.script_parser import ScriptParser as ScriptParserClass
            components['script_parser'] = ScriptParserClass(config)
            logger.info("✅ Script parser initialized")
        except Exception as e:
            logger.warning(f"⚠️ Script parser failed to initialize: {e}")
            fallback_parser = offline_manager.get_model('nlp_processor')
            if fallback_parser is None:
                # Force create a basic NLP processor if none exists
                from src.utils.offline_models import BasicNLPProcessor
                fallback_parser = BasicNLPProcessor()
            components['script_parser'] = fallback_parser
            logger.info("✅ Script parser initialized with offline fallback")
        
        try:
            from src.processors.audio_analyzer import AudioAnalyzer
            if AudioAnalyzer is not None:
                components['audio_analyzer'] = AudioAnalyzer(config)
                logger.info("✅ Audio analyzer initialized")
            else:
                raise ImportError("AudioAnalyzer class not available")
        except Exception as e:
            logger.warning(f"⚠️ Audio analyzer failed to initialize: {e}")
            components['audio_analyzer'] = offline_manager.get_model('visual_analyzer')  # Basic fallback
        
        try:
            from src.processors.scene_detector import SceneDetector
            if SceneDetector is not None:
                components['scene_detector'] = SceneDetector(config)
                logger.info("✅ Scene detector initialized")
            else:
                raise ImportError("SceneDetector class not available")
        except Exception as e:
            logger.warning(f"⚠️ Scene detector failed to initialize: {e}")
            components['scene_detector'] = offline_manager.get_model('scene_detector')
        
        try:
            from src.ai_models.emotion_detector import EmotionDetector
            if EmotionDetector is not None:
                components['emotion_detector'] = EmotionDetector(config)
                logger.info("✅ Emotion detector initialized")
            else:
                raise ImportError("EmotionDetector class not available")
        except Exception as e:
            logger.warning(f"⚠️ Emotion detector failed to initialize: {e}")
            components['emotion_detector'] = offline_manager.get_model('emotion_detector')
        
        # Initialize remaining components with fallbacks
        component_imports = [
            ('advanced_emotion_detector', 'src.ai_models.advanced_emotion_detector', 'AdvancedEmotionDetector'),
            ('video_editor', 'src.processors.video_editor', 'VideoEditor'),
            ('realtime_processor', 'src.processors.realtime_processor', 'RealTimeProcessor'),
            ('professional_exporter', 'src.exporters.professional_exporter', 'ProfessionalExporter'),
            ('cut_suggester', 'src.suggestions.cut_suggester', 'CutSuggester'),
            ('transition_recommender', 'src.suggestions.transition_recommender', 'TransitionRecommender'),
            ('timeline_viewer', 'src.ui.timeline_viewer', 'TimelineViewer'),
            ('suggestion_panel', 'src.ui.suggestion_panel', 'SuggestionPanel'),
            ('file_handler', 'src.utils.file_handler', 'FileHandler'),
            ('timeline_sync', 'src.utils.timeline_sync', 'TimelineSync'),
        ]
        
        for component_name, module_path, class_name in component_imports:
            try:
                module = __import__(module_path, fromlist=[class_name])
                component_class = getattr(module, class_name)
                if component_class is not None:
                    components[component_name] = component_class(config)
                    logger.info(f"✅ {component_name} initialized")
                else:
                    raise ImportError(f"{class_name} class not available")
            except Exception as e:
                logger.warning(f"⚠️ {component_name} failed to initialize: {e}")
                components[component_name] = offline_manager.get_model('visual_analyzer')  # Basic fallback
        
        # Initialize advanced AI components with extra error handling
        advanced_components = [
            ('content_analyzer', 'src.ai_models.intelligent_content_analyzer', 'IntelligentContentAnalyzer'),
            ('music_sync', 'src.ai_models.music_sync_engine', 'MusicSyncEngine'),
            ('learning_system', 'src.ai_models.user_learning_system', 'AIUserLearningSystem'),
            ('timeline_editor', 'src.ui.interactive_timeline_editor', 'InteractiveTimelineEditor'),
            ('cloud_manager', 'src.utils.cloud_integration', 'CloudIntegrationManager')
        ]
        
        for component_name, module_path, class_name in advanced_components:
            try:
                module = __import__(module_path, fromlist=[class_name])
                component_class = getattr(module, class_name)
                if component_class is not None:
                    components[component_name] = component_class(config)
                    logger.info(f"✅ {component_name} initialized")
                else:
                    raise ImportError(f"{class_name} class not available")
            except Exception as e:
                logger.warning(f"⚠️ {component_name} failed to initialize, using fallback: {e}")
                components[component_name] = offline_manager.get_model('visual_analyzer')  # Basic fallback
        
        # Add offline manager status info
        components['offline_manager'] = offline_manager
        
        # Show initialization summary
        online_count = sum(1 for name in components if not name.endswith('_fallback'))
        total_count = len(components) - 1  # Exclude offline_manager
        
        if online_count == total_count:
            logger.info(f"🚀 All {total_count} components initialized successfully!")
        else:
            fallback_count = total_count - online_count
            logger.info(f"⚠️ {online_count}/{total_count} components initialized. {fallback_count} using fallbacks.")
            st.warning(f"Some AI models are unavailable (offline mode). {online_count}/{total_count} components loaded successfully.")
        
        return components
        
    except Exception as e:
        logger.error(f"Critical error initializing components: {e}")
        st.error(f"Critical error initializing AI components: {e}")
        
        # Return minimal fallback system
        try:
            from src.utils.offline_models import OfflineModelManager
            offline_manager = OfflineModelManager(config)
            return {
                'video_analyzer': offline_manager.get_model('visual_analyzer'),
                'audio_analyzer': offline_manager.get_model('visual_analyzer'),
                'emotion_detector': offline_manager.get_model('emotion_detector'),
                'scene_detector': offline_manager.get_model('scene_detector'),
                'script_parser': offline_manager.get_model('nlp_processor'),
                'offline_manager': offline_manager
            }
        except Exception as fallback_error:
            logger.error(f"Even fallback initialization failed: {fallback_error}")
            return None

def generate_video_thumbnail(video_path, output_path=None, timestamp=1.0):
    """Generate a thumbnail from video file."""
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(fps * timestamp)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Resize for thumbnail
            height, width = frame_rgb.shape[:2]
            aspect_ratio = width / height
            thumbnail_width = 300  # Use default since config not available in this scope
            thumbnail_height = int(thumbnail_width / aspect_ratio)
            
            thumbnail = cv2.resize(frame_rgb, (thumbnail_width, thumbnail_height))
            return Image.fromarray(thumbnail)
    except Exception as e:
        logger.error(f"Error generating thumbnail: {e}")
    return None

def create_drag_drop_area():
    """Create a drag and drop file upload area."""
    st.markdown("""
    <div style="
        border: 3px dashed #667eea;
        border-radius: 15px;
        padding: 3rem;
        text-align: center;
        background: linear-gradient(145deg, #f8f9ff 0%, #ffffff 100%);
        margin: 1rem 0;
        transition: all 0.3s ease;
    " onmouseover="this.style.borderColor='#764ba2'; this.style.background='linear-gradient(145deg, #ffffff 0%, #f0f2ff 100%)'"
       onmouseout="this.style.borderColor='#667eea'; this.style.background='linear-gradient(145deg, #f8f9ff 0%, #ffffff 100%)'">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📁</div>
        <h3 style="color: #2c3e50; margin-bottom: 0.5rem;">Drag & Drop Your Files Here</h3>
        <p style="color: #7f8c8d; font-size: 1.1rem;">Or use the file uploaders below</p>
        <p style="color: #95a5a6; font-size: 0.9rem;">
            Supported: Video (up to 2GB), Audio (up to 500MB), Scripts (up to 500KB)
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_progress_tracker():
    """Create a progress tracking system."""
    if 'processing_progress' not in st.session_state:
        st.session_state.processing_progress = {
            'total_steps': 0,
            'current_step': 0,
            'step_name': '',
            'status': 'idle'
        }
    return st.session_state.processing_progress

def update_progress(step_name, current_step, total_steps):
    """Update processing progress."""
    progress_tracker = create_progress_tracker()
    progress_tracker['step_name'] = step_name
    progress_tracker['current_step'] = current_step
    progress_tracker['total_steps'] = total_steps
    progress_tracker['status'] = 'processing'

def display_progress_bar():
    """Display current progress bar."""
    progress_tracker = create_progress_tracker()
    
    if progress_tracker['status'] == 'processing' and progress_tracker['total_steps'] > 0:
        progress_percentage = progress_tracker['current_step'] / progress_tracker['total_steps']
        
        st.markdown("### 🔄 Processing Status")
        progress_bar = st.progress(progress_percentage)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text(f"Current Step: {progress_tracker['step_name']}")
        with col2:
            st.text(f"{progress_tracker['current_step']}/{progress_tracker['total_steps']}")
        
        return progress_bar
    return None

def create_advanced_filters():
    """Create advanced filtering options for suggestions."""
    st.markdown("### 🔍 Advanced Filters")
    
    with st.expander("Filter Options", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            confidence_threshold = st.slider(
                "Minimum Confidence",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Filter suggestions by confidence score"
            )
            
            suggestion_types = st.multiselect(
                "Suggestion Types",
                ["Cut Suggestions", "Transition Effects", "Scene Changes", "Emotion-based Cuts"],
                default=["Cut Suggestions", "Scene Changes"],
                help="Select which types of suggestions to show"
            )
        
        with col2:
            time_range = st.slider(
                "Time Range (seconds)",
                min_value=0,
                max_value=300,
                value=(0, 60),
                help="Filter suggestions by timestamp"
            )
            
            emotion_filter = st.multiselect(
                "Emotion Filter",
                ["Joy", "Sadness", "Anger", "Fear", "Surprise", "Neutral"],
                default=[],
                help="Filter by detected emotions"
            )
    
    return {
        'confidence_threshold': confidence_threshold,
        'suggestion_types': suggestion_types,
        'time_range': time_range,
        'emotion_filter': emotion_filter
    }

def main():
    """Main Streamlit application with enhanced error handling and offline support."""
    try:
        st.set_page_config(
            page_title="VideoCraft - AI Video Editor",
            page_icon="🎬",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    except Exception as e:
        logger.error(f"Page config error: {e}")
    
    # Custom CSS for better styling and accessibility
    st.markdown("""
    <style>
    /* Global styling improvements */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        color: white !important;
        margin-bottom: 0.5rem;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 1.2rem;
        margin: 0;
    }
    
    /* System status indicators */
    .status-online { color: #28a745; font-weight: bold; }
    .status-offline { color: #dc3545; font-weight: bold; }
    .status-fallback { color: #ffc107; font-weight: bold; }
    
    /* Enhanced metric cards */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #e1e5e9;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
    }
    
    .metric-card h4 {
        color: #2c3e50 !important;
        margin-bottom: 1rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
    }
    
    .metric-card p {
        color: #34495e !important;
        margin: 0.3rem 0;
        font-size: 0.95rem;
    }
    
    /* Feature cards styling */
    .feature-card {
        background: linear-gradient(145deg, #f8f9ff 0%, #ffffff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
    }
    
    .feature-card h4 {
        color: #2c3e50 !important;
        margin-bottom: 1rem;
    }
    
    .feature-card li {
        color: #34495e !important;
        margin: 0.5rem 0;
    }
    
    /* Status indicators */
    .status-enabled {
        color: #27ae60 !important;
        font-weight: bold;
    }
    
    .status-disabled {
        color: #e74c3c !important;
        font-weight: bold;
    }
    
    /* Button improvements */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar improvements */
    .css-1d391kg {
        background-color: #f8f9ff;
    }
    
    /* File uploader styling */
    .uploadedFile {
        background-color: #f0f2f6;
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Progress bar improvements */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Warning and error message styling */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Expander improvements */
    .streamlit-expanderHeader {
        background-color: #f8f9ff;
        border-radius: 8px;
        border: 1px solid #e1e5e9;
    }
    
    /* Metric improvements */
    [data-testid="metric-container"] {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
        border: 1px solid #e1e5e9;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    /* Dark text on light backgrounds for readability */
    .main .block-container {
        color: #2c3e50;
    }
    
    /* Ensure all text is readable */
    p, span, div {
        color: #2c3e50 !important;
    }
    
    /* Header improvements */
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50 !important;
    }
    
    /* Sidebar text */
    .css-1d391kg p, .css-1d391kg span {
        color: #2c3e50 !important;
    }
    
    /* Enhanced progress styling */
    .stProgress {
        height: 15px;
        border-radius: 7px;
        background-color: #f0f2f6;
        overflow: hidden;
        box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    /* Drag and drop area styling */
    .drag-drop-area {
        border: 3px dashed #667eea;
        border-radius: 15px;
        padding: 3rem;
        text-align: center;
        background: linear-gradient(145deg, #f8f9ff 0%, #ffffff 100%);
        margin: 1rem 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .drag-drop-area:hover {
        border-color: #764ba2;
        background: linear-gradient(145deg, #ffffff 0%, #f0f2ff 100%);
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.15);
    }
    
    /* Thumbnail styling */
    .video-thumbnail {
        border-radius: 10px;
        border: 2px solid #e1e5e9;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    
    .video-thumbnail:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    
    /* Filter controls styling */
    .filter-section {
        background: linear-gradient(145deg, #f8f9ff 0%, #ffffff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e1e5e9;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    /* Real-time status updates */
    .status-update {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-weight: 500;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    
    /* Processing indicator */
    .processing-indicator {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(102, 126, 234, 0.3);
        border-radius: 50%;
        border-top-color: #667eea;
        animation: spin 1s ease-in-out infinite;
        margin-right: 10px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🎬 AI Film Editor</h1>
        <p>Smart Cut & Transition Suggestions Powered by AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load configuration
    config = load_config()
    if config is None:
        return
    
    # Initialize components with error handling and offline mode support
    with st.spinner("Initializing AI components..."):
        components = initialize_components(config)
    
    if components is None:
        st.error("❌ Critical error: Unable to initialize any components")
        st.info("🔧 **Emergency Mode**: Try basic file management below")
        
        # Provide basic functionality even when everything fails
        st.subheader("📁 Basic File Management")
        video_file = st.file_uploader("Upload Video File", type=['mp4', 'avi', 'mov', 'mkv', 'webm'])
        if video_file:
            st.success(f"✅ File uploaded: {video_file.name} ({video_file.size / (1024*1024):.1f}MB)")
            st.info("Basic functionality only. Please check system requirements and restart.")
        return
    
    # Check if we're running in offline mode
    offline_mode = 'offline_manager' in components
    online_components = [name for name, comp in components.items() 
                        if name != 'offline_manager' and not hasattr(comp, '_is_fallback')]
    total_components = len(components) - (1 if offline_mode else 0)
    
    # Show system status
    if len(online_components) < total_components:
        st.warning("""
        🔄 **Offline Mode Active**: Some AI models are unavailable. VideoCraft is using local processing 
        for basic functionality. For full AI capabilities, ensure internet connection and restart the application.
        """)
        
        # System status metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("System Status", "🟡 Offline Mode", "Basic AI Active")
        with col2:
            st.metric("Components", f"{len(online_components)}/{total_components}", "Online/Total")
        with col3:
            st.metric("AI Capability", "Local Processing", "Limited Features")
    else:
        st.success("🚀 All AI components online and ready!")
        
        # Full system status
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("System Status", "🟢 Online", "Full AI Active")
        with col2:
            st.metric("Components", f"{total_components}/{total_components}", "All Online")
        with col3:
            st.metric("AI Capability", "Advanced AI", "All Features")
    
    # Sidebar for file uploads and settings
    with st.sidebar:
        st.header("📁 File Upload")
        
        # Drag and drop area
        create_drag_drop_area()
        
        # Video file upload with enhanced features
        video_file = st.file_uploader(
            "Upload Video File",
            type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
            help="Upload your raw video footage (max 2GB - increased limit!)",
            key="video_uploader"
        )
        
        # Display upload progress, file info, and thumbnail
        if video_file is not None:
            file_size_mb = video_file.size / (1024 * 1024)
            max_size_mb = config.get('file_limits', {}).get('max_video_size_mb', 4096)
            
            # Comprehensive file validation
            validation_errors = []
            
            # Check file size
            if file_size_mb > max_size_mb:
                validation_errors.append(f"File too large: {file_size_mb:.1f}MB. Maximum allowed: {max_size_mb}MB")
            
            # Check file extension
            allowed_extensions = config.get('video', {}).get('supported_formats', ['.mp4', '.avi', '.mov', '.mkv', '.webm'])
            file_ext = '.' + video_file.name.split('.')[-1].lower()
            if file_ext not in allowed_extensions:
                validation_errors.append(f"Unsupported format: {file_ext}. Allowed: {', '.join(allowed_extensions)}")
            
            # Check minimum file size (1MB minimum)
            if file_size_mb < 1:
                validation_errors.append(f"File too small: {file_size_mb:.1f}MB. Minimum size: 1MB")
            
            # Display validation results
            if validation_errors:
                for error in validation_errors:
                    st.error(f"⚠️ {error}")
                st.warning("Please upload a valid video file that meets all requirements.")
            else:
                st.success(f"✅ Video loaded: {file_size_mb:.1f}MB")
                
                # Display file metadata
                with st.expander("📋 File Information", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Filename:** {video_file.name}")
                        st.write(f"**Size:** {file_size_mb:.1f} MB")
                        st.write(f"**Format:** {file_ext.upper()}")
                    with col2:
                        st.write(f"**Status:** ✅ Valid")
                        st.write(f"**Validation:** Passed all checks")
                
                # Generate and display thumbnail
                with st.expander("📺 Video Preview", expanded=True):
                    try:
                        # Save uploaded file temporarily for thumbnail generation
                        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                            tmp_file.write(video_file.getvalue())
                            temp_path = tmp_file.name
                        
                        thumbnail = generate_video_thumbnail(temp_path)
                        if thumbnail:
                            st.image(thumbnail, caption="Video Thumbnail", use_column_width=True)
                        else:
                            st.info("Could not generate thumbnail - file may be corrupted or in an unsupported codec")
                        
                        # Clean up temporary file
                        os.unlink(temp_path)
                    except Exception as e:
                        st.warning(f"Thumbnail generation failed: {e}")
                        st.info("This may indicate a corrupted file or unsupported codec")
        
        # Script file upload
        script_file = st.file_uploader(
            "Upload Script File",
            type=['txt', 'srt', 'vtt', 'ass'],
            help="Upload the corresponding script or subtitles (max 500KB)",
            key="script_uploader"
        )
        
        # Audio file upload (new feature)
        audio_file = st.file_uploader(
            "Upload Audio File (Optional)",
            type=['mp3', 'wav', 'aac', 'flac'],
            help="Upload separate audio file for analysis (max 500MB)",
            key="audio_uploader"
        )
        
        st.divider()
        
        # Processing options
        st.header("⚙️ Analysis Options")
        
        analyze_video = st.checkbox("Analyze Video Content", value=True)
        analyze_audio = st.checkbox("Analyze Audio", value=True)
        analyze_script = st.checkbox("Analyze Script", value=bool(script_file))
        
        st.divider()
        
        # Sensitivity settings
        st.header("🎛️ Sensitivity Settings")
        
        emotion_threshold = st.slider(
            "Emotion Change Sensitivity", 
            0.1, 1.0, 0.3, 0.1,
            help="How sensitive to emotional changes in content"
        )
        
        scene_threshold = st.slider(
            "Scene Change Sensitivity", 
            0.1, 1.0, 0.4, 0.1,
            help="How sensitive to visual scene changes"
        )
        
        min_cut_interval = st.slider(
            "Minimum Cut Interval (seconds)", 
            0.5, 10.0, 2.0, 0.5,
            help="Minimum time between suggested cuts"
        )
    
    # Main processing area
    if video_file is not None:
        # Display file information
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📹 Video File</h4>
                <p><strong>Name:</strong> {video_file.name}</p>
                <p><strong>Size:</strong> {video_file.size / (1024*1024):.1f} MB</p>
                <p><strong>Type:</strong> {Path(video_file.name).suffix.upper()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if script_file:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📝 Script File</h4>
                    <p><strong>Name:</strong> {script_file.name}</p>
                    <p><strong>Size:</strong> {script_file.size / 1024:.1f} KB</p>
                    <p><strong>Type:</strong> {Path(script_file.name).suffix.upper()}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card">
                    <h4>📝 Script File</h4>
                    <p><strong>Status:</strong> <span class="status-disabled">No script uploaded</span></p>
                    <p><strong>Analysis:</strong> <span class="status-disabled">Script analysis disabled</span></p>
                    <p><em>Upload a script file to enable text analysis</em></p>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🎯 Analysis Configuration</h4>
                <p><strong>Video Analysis:</strong> <span class="{'status-enabled' if analyze_video else 'status-disabled'}">{'✅ Enabled' if analyze_video else '❌ Disabled'}</span></p>
                <p><strong>Audio Analysis:</strong> <span class="{'status-enabled' if analyze_audio else 'status-disabled'}">{'✅ Enabled' if analyze_audio else '❌ Disabled'}</span></p>
                <p><strong>Script Analysis:</strong> <span class="{'status-enabled' if analyze_script else 'status-disabled'}">{'✅ Enabled' if analyze_script else '❌ Disabled'}</span></p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Update config with user preferences
        config['suggestions']['emotion_change_threshold'] = emotion_threshold
        config['suggestions']['scene_change_threshold'] = scene_threshold
        config['suggestions']['minimum_cut_interval'] = min_cut_interval
        
        # Process button
        if st.button("🚀 Analyze Video & Generate Suggestions", type="primary", use_container_width=True):
            
            # Initialize variables first
            script_path = None
            audio_path = None
            
            # Initialize progress tracking
            total_steps = 2  # Base steps
            if analyze_video:
                total_steps += 3
            if analyze_audio:
                total_steps += 4
            if analyze_script and script_file:
                total_steps += 3
            
            current_step = 0
            
            # Create progress containers
            progress_container = st.container()
            status_container = st.container()
            
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            # Mark processing start for accurate timing
            st.session_state['processing_start_ts'] = time.time()

            # Save uploaded files
            current_step += 1
            update_progress("Preparing files...", current_step, total_steps)
            with status_container:
                status_text.text(f"Step {current_step}/{total_steps}: Preparing files...")
                progress_bar.progress(current_step / total_steps)
            
            file_handler = components['file_handler']
            
            video_path = file_handler.save_uploaded_file(video_file, 'video')
            if not video_path:
                st.error("Failed to save video file")
                return
            
            # Initialize file paths that were declared earlier
            if script_file and analyze_script:
                script_path = file_handler.save_uploaded_file(script_file, 'script')
                if not script_path:
                    st.warning("Failed to save script file - continuing without script analysis")
            
            if audio_file:
                audio_path = file_handler.save_uploaded_file(audio_file, 'audio')
            
            current_step += 1
            with status_container:
                status_text.text(f"Step {current_step}/{total_steps}: Files prepared successfully!")
                progress_bar.progress(current_step / total_steps)
            
            # Initialize analysis results
            video_analysis = {}
            script_analysis = {}
            audio_analysis = {}
            
            try:
                # Video Analysis
                if analyze_video:
                    current_step += 1
                    update_progress("Detecting scenes...", current_step, total_steps)
                    with status_container:
                        status_text.text(f"Step {current_step}/{total_steps}: Detecting scenes...")
                        progress_bar.progress(current_step / total_steps)
                    
                    video_analyzer = components['video_analyzer']
                    scene_detector = components['scene_detector']
                    
                    # Scene detection
                    scene_changes = scene_detector.detect_scenes(video_path, method='combined')
                    video_analysis['scene_changes'] = scene_changes
                    
                    current_step += 1
                    update_progress("Analyzing video timeline...", current_step, total_steps)
                    with status_container:
                        status_text.text(f"Step {current_step}/{total_steps}: Analyzing video timeline...")
                        progress_bar.progress(current_step / total_steps)
                    
                    # Video timeline analysis
                    timeline_analysis = video_analyzer.analyze_video_timeline(video_path)
                    video_analysis.update(timeline_analysis)
                    
                    current_step += 1
                    with status_container:
                        status_text.text(f"Step {current_step}/{total_steps}: Video analysis complete! Found {len(scene_changes)} scene changes")
                        progress_bar.progress(current_step / total_steps)
                
                # Audio Analysis  
                if analyze_audio:
                    current_step += 1
                    update_progress("Extracting audio...", current_step, total_steps)
                    with status_container:
                        status_text.text(f"Step {current_step}/{total_steps}: Extracting audio...")
                        progress_bar.progress(current_step / total_steps)
                    
                    audio_analyzer = components['audio_analyzer']
                    
                    # Extract audio from video or use uploaded audio
                    if not audio_path:
                        audio_path = audio_analyzer.extract_audio_from_video(video_path)
                    
                    current_step += 1
                    update_progress("Analyzing audio features...", current_step, total_steps)
                    with status_container:
                        status_text.text(f"Step {current_step}/{total_steps}: Analyzing audio features...")
                        progress_bar.progress(current_step / total_steps)
                    
                    # Audio feature extraction
                    audio_features = audio_analyzer.extract_audio_features(audio_path)
                    audio_analysis['features'] = audio_features
                    
                    current_step += 1
                    update_progress("Analyzing speech emotions...", current_step, total_steps)
                    with status_container:
                        status_text.text(f"Step {current_step}/{total_steps}: Analyzing speech emotions...")
                        progress_bar.progress(current_step / total_steps)
                    
                    # Speech emotion analysis
                    speech_emotions = audio_analyzer.analyze_speech_emotion(audio_path)
                    audio_analysis['speech_emotions'] = speech_emotions
                    
                    # Speaker change detection
                    speaker_changes = audio_analyzer.detect_speaker_changes(audio_path)
                    audio_analysis['speaker_changes'] = speaker_changes
                    
                    # Audio energy analysis
                    energy_timeline = audio_analyzer.analyze_audio_energy(audio_path)
                    audio_analysis['energy_timeline'] = energy_timeline
                    
                    current_step += 1
                    with status_container:
                        status_text.text(f"Step {current_step}/{total_steps}: Audio analysis complete! Found {len(speaker_changes)} potential speaker changes")
                        progress_bar.progress(current_step / total_steps)
                
                # Script Analysis
                if analyze_script and script_path:
                    current_step += 1
                    update_progress("Parsing script...", current_step, total_steps)
                    with status_container:
                        status_text.text(f"Step {current_step}/{total_steps}: Parsing script...")
                        progress_bar.progress(current_step / total_steps)
                    
                    script_parser = components['script_parser']
                    timeline_sync = components['timeline_sync']
                    
                    # Ensure we have a valid script parser
                    if script_parser is None:
                        st.error("❌ Script parser not available. Cannot analyze script.")
                        logger.error("Script parser is None, cannot parse script")
                        return
                    
                    # Parse script
                    try:
                        dialogue_data = script_parser.parse_script_file(script_path)
                    except Exception as e:
                        st.error(f"❌ Error parsing script: {e}")
                        logger.error(f"Script parsing failed: {e}")
                        return
                    
                    current_step += 1
                    update_progress("Analyzing emotions in script...", current_step, total_steps)
                    with status_container:
                        status_text.text(f"Step {current_step}/{total_steps}: Analyzing emotions in script...")
                        progress_bar.progress(current_step / total_steps)
                    
                    # Emotion analysis
                    try:
                        dialogue_with_emotions = script_parser.analyze_emotions(dialogue_data)
                    except Exception as e:
                        st.warning(f"⚠️ Emotion analysis failed, using basic analysis: {e}")
                        # Fallback to basic emotion assignment
                        dialogue_with_emotions = dialogue_data
                        for item in dialogue_with_emotions:
                            item.update({
                                'emotion': 'neutral',
                                'emotion_confidence': 0.5,
                                'all_emotions': {'neutral': 0.5}
                            })
                    
                    # Align script to video duration
                    video_duration = audio_analysis.get('features', {}).get('duration', 60)
                    aligned_dialogue = timeline_sync.align_script_to_video(
                        dialogue_with_emotions, video_duration
                    )
                    
                    current_step += 1
                    update_progress("Detecting emotional beats...", current_step, total_steps)
                    with status_container:
                        status_text.text(f"Step {current_step}/{total_steps}: Detecting emotional beats...")
                        progress_bar.progress(current_step / total_steps)
                    
                    # Detect emotional beats
                    try:
                        emotional_beats = script_parser.detect_emotional_beats(aligned_dialogue)
                    except Exception as e:
                        st.warning(f"⚠️ Emotional beat detection failed: {e}")
                        emotional_beats = []  # Empty list as fallback
                    
                    script_analysis['dialogue_data'] = aligned_dialogue
                    script_analysis['emotional_beats'] = emotional_beats
                    
                    with status_container:
                        status_text.text(f"Script analysis complete! Found {len(emotional_beats)} emotional beats")
                
                # Generate AI Suggestions
                progress_bar.progress(0.9)  # Near completion
                with status_container:
                    status_text.text("Generating AI suggestions...")
                
                cut_suggester = components['cut_suggester']
                transition_recommender = components['transition_recommender']
                emotion_detector = components['emotion_detector']
                
                # Generate cut suggestions
                cut_suggestions = cut_suggester.generate_suggestions(
                    video_analysis, script_analysis, audio_analysis
                )
                
                # Generate transition suggestions
                transition_suggestions = transition_recommender.suggest_transitions(
                    cut_suggestions,
                    audio_analysis.get('speech_emotions', []),
                    video_analysis,
                    script_analysis
                )
                
                # Advanced AI Processing
                st.info("🧠 Running advanced AI analysis...")
                
                # Content-aware analysis
                content_analyzer = components['content_analyzer']
                # Pass precomputed analyses to prevent re-loading media and to provide richer context
                content_analysis = content_analyzer.analyze_content(
                    video_path,
                    audio_or_text=audio_analysis,
                    visual_or_metadata=video_analysis
                )
                
                # Adapt suggestions based on content type
                try:
                    if hasattr(content_analyzer, 'adapt_suggestions_to_content'):
                        adapted_suggestions = content_analyzer.adapt_suggestions_to_content(
                            cut_suggestions, content_analysis
                        )
                    else:
                        logger.warning("Content analyzer missing adapt_suggestions_to_content method, using original suggestions")
                        adapted_suggestions = cut_suggestions
                except Exception as e:
                    logger.error(f"Failed to adapt suggestions: {e}")
                    adapted_suggestions = cut_suggestions
                
                # Music synchronization (if music detected)
                music_sync = components['music_sync']
                if content_analysis.get('has_music', False) and audio_path:
                    # Perform full music analysis and snap cuts to beats
                    music_data = music_sync.analyze_music(audio_path)
                    final_suggestions = music_sync.generate_beat_synchronized_cuts(
                        adapted_suggestions, music_data
                    )
                else:
                    final_suggestions = adapted_suggestions
                
                # User learning integration
                learning_system = components['learning_system']
                personalized_suggestions = learning_system.get_personalized_suggestions(
                    final_suggestions, {
                        'video_type': content_analysis.get('content_type'),
                        'duration': audio_analysis.get('features', {}).get('duration'),
                        'has_speech': bool(audio_analysis.get('speech_emotions')),
                        'has_music': content_analysis.get('has_music', False)
                    }
                )
                
                # Track user interaction for learning
                learning_system.track_user_action(
                    'video_processed',
                    {
                        'content_type': content_analysis.get('content_type'),
                        'suggestion_count': len(personalized_suggestions),
                        'processing_time': time.time() - st.session_state.get('processing_start_ts', time.time())
                    },
                    {
                        'video_duration': audio_analysis.get('features', {}).get('duration'),
                        'analysis_types': ['video' if analyze_video else None, 
                                         'audio' if analyze_audio else None,
                                         'script' if analyze_script else None]
                    }
                )
                
                # Complete progress
                progress_bar.progress(1.0)
                with status_container:
                    status_text.text(f"✅ AI analysis complete! Generated {len(personalized_suggestions)} personalized suggestions")
                
                # Display Results
                if personalized_suggestions:
                    st.success(f"✅ Analysis complete! Generated {len(personalized_suggestions)} personalized suggestions and {len(transition_suggestions)} transition recommendations.")
                    
                    st.header("📊 Analysis Results")
                    
                    # Content Analysis Results
                    if content_analysis:
                        st.subheader("🎯 Content Analysis")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Content Type", content_analysis.get('content_type', 'Unknown'))
                        
                        with col2:
                            confidence = content_analysis.get('confidence', 0)
                            st.metric("Classification Confidence", f"{confidence:.1%}")
                        
                        with col3:
                            has_music = content_analysis.get('has_music', False)
                            st.metric("Music Detected", "✅ Yes" if has_music else "❌ No")
                        
                        # Content-specific insights
                        insights = content_analysis.get('insights', [])
                        if insights:
                            st.write("**AI Insights:**")
                            for insight in insights:
                                st.write(f"• {insight}")
                    
                    # Interactive Timeline Editor
                    st.subheader("🎬 Interactive Timeline Editor")
                    timeline_editor = components['timeline_editor']
                    
                    # Prepare emotion timeline for timeline editor
                    emotion_timeline = []
                    if audio_analysis.get('speech_emotions'):
                        emotion_timeline = [
                            {
                                'timestamp': emotion['timestamp'],
                                'dominant_emotion': emotion['emotion'],
                                'confidence': emotion['confidence']
                            }
                            for emotion in audio_analysis['speech_emotions']
                        ]
                    
                    # Prepare music data if available
                    music_data = None
                    if content_analysis.get('has_music'):
                        music_data = music_sync.get_last_analysis_data()
                    
                    # Render advanced timeline
                    video_duration = audio_analysis.get('features', {}).get('duration', 60)
                    timeline_interactions = timeline_editor.render_advanced_timeline(
                        video_duration,
                        personalized_suggestions,
                        audio_analysis,
                        emotion_timeline,
                        music_data
                    )
                    
                    # Update suggestions based on timeline interactions
                    if timeline_interactions.get('selected_cuts'):
                        selected_suggestions = [
                            personalized_suggestions[i] 
                            for i in timeline_interactions['selected_cuts']
                            if i < len(personalized_suggestions)
                        ]
                        
                        # Track timeline interactions for learning
                        learning_system.track_user_action(
                            'timeline_selection',
                            {
                                'selected_count': len(selected_suggestions),
                                'total_count': len(personalized_suggestions)
                            }
                        )
                    else:
                        selected_suggestions = personalized_suggestions
                    
                    # AI Learning Dashboard
                    st.subheader("🧠 AI Learning Dashboard")
                    learning_dashboard = learning_system.render_learning_dashboard()
                    
                    # Cloud Integration Dashboard
                    st.subheader("☁️ Performance & Cloud Integration")
                    cloud_manager = components['cloud_manager']
                    cloud_dashboard = cloud_manager.render_cloud_dashboard()
                    
                    # Advanced Filtering Section
                    filter_settings = create_advanced_filters()
                    
                    # Apply filters to suggestions
                    filtered_suggestions = []
                    for suggestion in selected_suggestions:
                        # Apply confidence filter
                        if suggestion.confidence < filter_settings['confidence_threshold']:
                            continue
                        
                        # Apply time range filter
                        if not (filter_settings['time_range'][0] <= suggestion.timestamp <= filter_settings['time_range'][1]):
                            continue
                        
                        # Apply emotion filter if specified
                        if filter_settings['emotion_filter']:
                            suggestion_emotions = getattr(suggestion, 'emotions', [])
                            if not any(emotion in filter_settings['emotion_filter'] for emotion in suggestion_emotions):
                                continue
                        
                        filtered_suggestions.append(suggestion)
                    
                    st.info(f"Showing {len(filtered_suggestions)} of {len(selected_suggestions)} suggestions after filtering")
                    
                    # Timeline Visualization (Traditional)
                    timeline_viewer = components['timeline_viewer']
                    
                    # Create main timeline with filtered suggestions
                    timeline_fig = timeline_viewer.create_timeline_visualization(
                        audio_analysis.get('features', {}).get('duration', 60),
                        filtered_suggestions,
                        transition_suggestions,
                        audio_analysis.get('speech_emotions', [])
                    )
                    
                    st.plotly_chart(timeline_fig, use_container_width=True)
                    
                    # Suggestion summary chart
                    summary_fig = timeline_viewer.create_suggestion_summary_chart(filtered_suggestions)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.plotly_chart(summary_fig, use_container_width=True)
                    
                    with col2:
                        # Display statistics
                        st.subheader("📈 Analysis Statistics")
                        
                        total_duration = audio_analysis.get('features', {}).get('duration', 0)
                        if filtered_suggestions:
                            avg_confidence = sum(s.confidence for s in filtered_suggestions) / len(filtered_suggestions)
                            high_confidence_count = len([s for s in filtered_suggestions if s.confidence > 0.7])
                        else:
                            avg_confidence = 0
                            high_confidence_count = 0
                        
                        st.metric("Video Duration", f"{total_duration:.1f} seconds")
                        st.metric("Filtered Suggestions", len(filtered_suggestions))
                        st.metric("Average Confidence", f"{avg_confidence:.1%}")
                        st.metric("High Confidence Cuts", high_confidence_count)
                        
                        # AI enhancement metrics
                        if content_analysis:
                            st.metric("Content Type", content_analysis.get('content_type', 'Unknown'))
                        
                        personalization_count = len(personalized_suggestions) - len(cut_suggestions)
                        if personalization_count > 0:
                            st.metric("AI Enhancements", f"+{personalization_count}")
                    
                    # Interactive Suggestion Panel
                    suggestion_panel = components['suggestion_panel']
                    
                    # Render suggestion controls
                    filters = suggestion_panel.render_suggestion_controls()
                    
                    # Render suggestion list with filtered suggestions
                    final_selected_suggestions = suggestion_panel.render_suggestion_list(
                        filtered_suggestions, filters, transition_suggestions
                    )
                    
                    # Track final selections for learning
                    if final_selected_suggestions:
                        learning_system.track_user_action(
                            'final_selection',
                            {
                                'selected_count': len(final_selected_suggestions),
                                'from_filtered': len(filtered_suggestions)
                            }
                        )
                    
                    # Batch actions
                    if selected_suggestions:
                        batch_result = suggestion_panel.render_batch_actions(selected_suggestions)
                        
                        if batch_result.get('action') == 'export':
                            # Professional Export Section
                            st.header("🎬 Professional Export")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("Export Formats")
                                export_formats = st.multiselect(
                                    "Select Export Formats",
                                    ['edl', 'xml', 'csv', 'json', 'fcpxml', 'premiere', 'resolve', 'avid'],
                                    default=['edl', 'xml', 'json'],
                                    help="Choose formats for your video editing software"
                                )
                                
                                create_package = st.checkbox(
                                    "Create Project Package",
                                    value=True,
                                    help="Bundle all formats in a ZIP file"
                                )
                                
                                include_preview = st.checkbox(
                                    "Generate Video Preview",
                                    value=False,
                                    help="Create a preview video with suggested cuts"
                                )
                            
                            with col2:
                                st.subheader("Export Options")
                                project_name = st.text_input(
                                    "Project Name",
                                    value=f"videocraft_edit_{Path(video_file.name).stem}",
                                    help="Name for the exported project"
                                )
                                
                                # Video editing software targeting
                                target_software = st.selectbox(
                                    "Target Software",
                                    ["Generic", "Adobe Premiere Pro", "Final Cut Pro", "DaVinci Resolve", "Avid Media Composer"],
                                    help="Optimize export for specific software"
                                )
                                
                                confidence_filter = st.slider(
                                    "Minimum Confidence for Export",
                                    0.0, 1.0, 0.5, 0.1,
                                    help="Only export cuts above this confidence level"
                                )
                            
                            if st.button("🚀 Export Professional Project", type="primary"):
                                with st.spinner("Creating professional exports..."):
                                    try:
                                        # Filter suggestions by confidence
                                        export_cuts = [s for s in selected_suggestions if s.confidence >= confidence_filter]
                                        # Extract video properties
                                        try:
                                            cap = cv2.VideoCapture(video_path)
                                            video_fps = cap.get(cv2.CAP_PROP_FPS) or config.get('video', {}).get('fps_target', 30)
                                            video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1920
                                            video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 1080
                                            cap.release()
                                        except Exception as e:
                                            logger.warning(f"Could not extract video properties: {e}")
                                            video_fps = config.get('video', {}).get('fps_target', 30)
                                            video_width = 1920
                                            video_height = 1080
                                        
                                        # Prepare video metadata
                                        video_metadata = {
                                            'file_path': video_file.name,
                                            'duration': total_duration,
                                            'fps': video_fps,
                                            'width': video_width,
                                            'height': video_height,
                                            'processing_time': time.time() - current_step  # Approximate
                                        }
                                        
                                        professional_exporter = components['professional_exporter']
                                        
                                        if create_package:
                                            # Create complete project package
                                            package_path = professional_exporter.create_project_package(
                                                export_cuts,
                                                transition_suggestions,
                                                video_metadata,
                                                str(Path.cwd() / "exports"),
                                                export_formats
                                            )
                                            
                                            # Offer download
                                            with open(package_path, 'rb') as f:
                                                st.download_button(
                                                    "📦 Download Project Package",
                                                    data=f.read(),
                                                    file_name=Path(package_path).name,
                                                    mime="application/zip"
                                                )
                                        else:
                                            # Export individual formats
                                            for fmt in export_formats:
                                                export_path = f"exports/{project_name}.{fmt}"
                                                Path("exports").mkdir(exist_ok=True)
                                                
                                                result_path = professional_exporter.export_suggestions(
                                                    export_cuts,
                                                    transition_suggestions,
                                                    video_metadata,
                                                    fmt,
                                                    export_path
                                                )
                                                
                                                with open(result_path, 'rb') as f:
                                                    st.download_button(
                                                        f"📄 Download {fmt.upper()}",
                                                        data=f.read(),
                                                        file_name=Path(result_path).name,
                                                        mime="application/octet-stream",
                                                        key=f"download_{fmt}"
                                                    )
                                        
                                        # Generate video preview if requested
                                        if include_preview:
                                            video_editor = components['video_editor']
                                            preview_path = video_editor.create_preview(
                                                video_path, export_cuts, max_duration=30.0
                                            )
                                            
                                            if preview_path:
                                                st.success("✅ Preview video generated!")
                                                with open(preview_path, 'rb') as f:
                                                    st.download_button(
                                                        "🎥 Download Preview Video",
                                                        data=f.read(),
                                                        file_name="ai_edit_preview.mp4",
                                                        mime="video/mp4"
                                                    )
                                        
                                        st.success(f"✅ Successfully exported {len(export_cuts)} suggestions in {len(export_formats)} format(s)!")
                                        
                                        # Show export statistics
                                        st.info(f"""
                                        **Export Summary:**
                                        - Exported Cuts: {len(export_cuts)}
                                        - Average Confidence: {sum(s.confidence for s in export_cuts) / len(export_cuts):.1%}
                                        - Formats: {', '.join(export_formats)}
                                        - Target Software: {target_software}
                                        """)
                                        
                                    except Exception as e:
                                        st.error(f"Export failed: {e}")
                                        logger.error(f"Export error: {e}")
                            
                            # Export format descriptions
                            st.subheader("📋 Format Guide")
                            format_descriptions = {
                                'edl': "**EDL** - Industry standard Edit Decision List, compatible with most professional software",
                                'xml': "**XML** - Generic XML format for broad compatibility and custom workflows", 
                                'fcpxml': "**FCPXML** - Native Final Cut Pro format with full metadata support",
                                'premiere': "**Premiere XML** - Adobe Premiere Pro compatible project format",
                                'resolve': "**Resolve DRP** - DaVinci Resolve project metadata format",
                                'avid': "**Avid EDL** - Avid Media Composer optimized Edit Decision List",
                                'csv': "**CSV** - Spreadsheet format for analysis and custom processing",
                                'json': "**JSON** - Complete metadata with full AI analysis results"
                            }
                            
                            for fmt in export_formats:
                                if fmt in format_descriptions:
                                    st.markdown(f"- {format_descriptions[fmt]}")
                            
                            # Export functionality
                            export_format = st.selectbox("Export Format", ['json', 'csv', 'txt'])
                            
                            if st.button("Download Export"):
                                export_path = file_handler.export_suggestions(
                                    selected_suggestions, export_format
                                )
                                if export_path:
                                    with open(export_path, 'rb') as f:
                                        st.download_button(
                                            f"Download {export_format.upper()} File",
                                            data=f.read(),
                                            file_name=Path(export_path).name,
                                            mime=f"application/{export_format}"
                                        )
                    
                    # Render analytics
                    suggestion_panel.render_suggestion_analytics(cut_suggestions)
                    
                else:
                    st.warning("No cut suggestions were generated. Try adjusting the sensitivity settings.")
                
            except Exception as e:
                logger.error(f"Error during processing: {e}")
                st.error(f"An error occurred during processing: {e}")
            
            finally:
                # Cleanup temporary files
                try:
                    file_handler.cleanup_file(video_path)
                    if script_path:
                        file_handler.cleanup_file(script_path)
                    if 'audio_path' in locals():
                        file_handler.cleanup_file(audio_path)
                except:
                    pass
    
    else:
        # Welcome screen when no video is uploaded
        st.markdown("""
        ## 🎯 How AI Film Editor Works
        
        Our AI-powered film editing assistant analyzes your video content and scripts to suggest intelligent cut points and transitions that enhance your storytelling.
        
        ### 📋 Getting Started:
        
        1. **📹 Upload Video**: Upload your raw footage (MP4, AVI, MOV, MKV, WebM) - **Now supports up to 2GB files!**
        2. **📝 Upload Script**: Optionally upload your script or subtitles (TXT, SRT, VTT, ASS)
        3. **⚙️ Configure Settings**: Adjust sensitivity settings in the sidebar
        4. **🚀 Process**: Click "Analyze Video" to generate AI suggestions
        5. **✨ Review & Apply**: Review suggestions and export your cut list
        
        ### 🤖 AI Analysis Features:
        
        - **🎬 Scene Detection**: Automatically identify visual scene changes using advanced computer vision
        - **😊 Emotion Analysis**: Detect emotional beats in dialogue and speech using state-of-the-art NLP
        - **🗣️ Speaker Changes**: Identify when speakers change in audio with voice recognition
        - **🎵 Audio Cues**: Analyze audio energy, silence, and music for optimal cut opportunities
        - **🔄 Smart Transitions**: Recommend appropriate transition types based on content context
        - **🎯 Context-Aware**: Combine multiple AI signals for intelligent editing suggestions
        
        ### 🎨 Supported Formats & Limits:
        
        **Video**: MP4, AVI, MOV, MKV, WebM (up to **2GB** - 4x increased!)  
        **Scripts**: TXT, SRT, VTT, ASS (up to 500KB - 5x increased!)  
        **Audio**: WAV, MP3, M4A, FLAC (up to 500MB - 5x increased!)  
        **Export**: JSON, CSV, TXT with rich metadata
        
        ---
        
        ### 🆕 What's New:
        - 🚀 **Massive file size increases**: Now supports 2GB video files (up from 200MB)
        - 🎨 **Complete UI redesign**: Better colors, improved readability, modern design
        - 🔧 **Enhanced accessibility**: No more white text on white backgrounds
        - ⚡ **Better performance**: Optimized processing for larger files
        - 📊 **Improved analytics**: More detailed suggestion statistics
        
        *Ready to revolutionize your editing workflow? Upload a video file to begin!*
        """)
        
        # Feature showcase with improved styling
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h4>🎬 Advanced Scene Analysis</h4>
                <ul>
                    <li>🔍 Smart visual scene detection</li>
                    <li>📸 Shot type identification</li>
                    <li>🎭 Mood and emotion analysis</li>
                    <li>🖼️ Composition evaluation</li>
                    <li>🎨 Color palette analysis</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h4>🗣️ Intelligent Audio Processing</h4>
                <ul>
                    <li>🎤 Speech emotion recognition</li>
                    <li>👥 Speaker change detection</li>
                    <li>📊 Audio energy analysis</li>
                    <li>🔇 Silence detection</li>
                    <li>🎵 Music vs speech classification</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h4>📝 Script Intelligence</h4>
                <ul>
                    <li>💭 Dialogue emotion analysis</li>
                    <li>👤 Character analysis</li>
                    <li>💓 Emotional beat detection</li>
                    <li>⏱️ Timeline synchronization</li>
                    <li>🎯 Content-aware suggestions</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
