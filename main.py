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

# Import our modules
from src.processors.video_analyzer import VideoAnalyzer
from src.processors.script_parser import ScriptParser
from src.processors.audio_analyzer import AudioAnalyzer
from src.processors.scene_detector import SceneDetector
from src.ai_models.emotion_detector import EmotionDetector
from src.suggestions.cut_suggester import CutSuggester
from src.suggestions.transition_recommender import TransitionRecommender
from src.ui.timeline_viewer import TimelineViewer
from src.ui.suggestion_panel import SuggestionPanel
from src.utils.file_handler import FileHandler
from src.utils.timeline_sync import TimelineSync

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
    """Initialize all processing components."""
    try:
        components = {
            'video_analyzer': VideoAnalyzer(config),
            'script_parser': ScriptParser(config),
            'audio_analyzer': AudioAnalyzer(config),
            'scene_detector': SceneDetector(config),
            'emotion_detector': EmotionDetector(config),
            'cut_suggester': CutSuggester(config),
            'transition_recommender': TransitionRecommender(config),
            'timeline_viewer': TimelineViewer(config),
            'suggestion_panel': SuggestionPanel(config),
            'file_handler': FileHandler(config),
            'timeline_sync': TimelineSync(config)
        }
        return components
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        st.error(f"Error initializing AI components: {e}")
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
            thumbnail_width = 300
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
    """Main Streamlit application."""
    st.set_page_config(
        page_title="AI Film Editor",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
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
    
    /* Improved metric cards */
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
    
    # Initialize components
    with st.spinner("Initializing AI components..."):
        components = initialize_components(config)
    
    if components is None:
        return
    
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
            if file_size_mb > 2048:
                st.error(f"⚠️ File too large: {file_size_mb:.1f}MB. Maximum allowed: 2048MB (2GB)")
            else:
                st.success(f"✅ Video loaded: {file_size_mb:.1f}MB")
                
                # Generate and display thumbnail
                with st.expander("📺 Video Preview", expanded=True):
                    try:
                        # Save uploaded file temporarily for thumbnail generation
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                            tmp_file.write(video_file.getvalue())
                            temp_path = tmp_file.name
                        
                        thumbnail = generate_video_thumbnail(temp_path)
                        if thumbnail:
                            st.image(thumbnail, caption="Video Thumbnail", use_column_width=True)
                        else:
                            st.info("Could not generate thumbnail")
                        
                        # Clean up temporary file
                        os.unlink(temp_path)
                    except Exception as e:
                        st.warning(f"Thumbnail generation failed: {e}")
        
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
                    
                    # Parse script
                    dialogue_data = script_parser.parse_script_file(script_path)
                    
                    current_step += 1
                    update_progress("Analyzing emotions in script...", current_step, total_steps)
                    with status_container:
                        status_text.text(f"Step {current_step}/{total_steps}: Analyzing emotions in script...")
                        progress_bar.progress(current_step / total_steps)
                    
                    # Emotion analysis
                    dialogue_with_emotions = script_parser.analyze_emotions(dialogue_data)
                    
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
                    emotional_beats = script_parser.detect_emotional_beats(aligned_dialogue)
                    
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
                
                # Complete progress
                progress_bar.progress(1.0)
                with status_container:
                    status_text.text(f"✅ AI analysis complete! Generated {len(cut_suggestions)} cut suggestions")
                
                # Display Results
                if cut_suggestions:
                    st.success(f"✅ Analysis complete! Generated {len(cut_suggestions)} cut suggestions and {len(transition_suggestions)} transition recommendations.")
                    
                    st.header("📊 Analysis Results")
                    
                    # Advanced Filtering Section
                    filter_settings = create_advanced_filters()
                    
                    # Apply filters to suggestions
                    filtered_suggestions = []
                    for suggestion in cut_suggestions:
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
                    
                    st.info(f"Showing {len(filtered_suggestions)} of {len(cut_suggestions)} suggestions after filtering")
                    
                    # Timeline Visualization
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
                    
                    # Interactive Suggestion Panel
                    suggestion_panel = components['suggestion_panel']
                    
                    # Render suggestion controls
                    filters = suggestion_panel.render_suggestion_controls()
                    
                    # Render suggestion list with filtered suggestions
                    selected_suggestions = suggestion_panel.render_suggestion_list(
                        filtered_suggestions, filters, transition_suggestions
                    )
                    
                    # Batch actions
                    if selected_suggestions:
                        batch_result = suggestion_panel.render_batch_actions(selected_suggestions)
                        
                        if batch_result.get('action') == 'export':
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
