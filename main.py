import streamlit as st
import yaml
import os
import tempfile
from pathlib import Path
import logging

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
        logger.error("config.yaml not found. Please ensure the configuration file exists.")
        st.error("Configuration file not found. Please check your setup.")
        return None
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
        
        # Video file upload
        video_file = st.file_uploader(
            "Upload Video File",
            type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
            help="Upload your raw video footage (max 2GB - increased limit!)",
            key="video_uploader"
        )
        
        # Display upload progress and file info
        if video_file is not None:
            file_size_mb = video_file.size / (1024 * 1024)
            if file_size_mb > 2048:
                st.error(f"⚠️ File too large: {file_size_mb:.1f}MB. Maximum allowed: 2048MB (2GB)")
            else:
                st.success(f"✅ Video loaded: {file_size_mb:.1f}MB")
        
        # Script file upload
        script_file = st.file_uploader(
            "Upload Script File",
            type=['txt', 'srt', 'vtt', 'ass'],
            help="Upload the corresponding script or subtitles (max 500KB)",
            key="script_uploader"
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
            
            # Save uploaded files
            with st.status("Preparing files...") as status:
                file_handler = components['file_handler']
                
                video_path = file_handler.save_uploaded_file(video_file, 'video')
                if not video_path:
                    st.error("Failed to save video file")
                    return
                
                script_path = None
                if script_file and analyze_script:
                    script_path = file_handler.save_uploaded_file(script_file, 'script')
                    if not script_path:
                        st.warning("Failed to save script file - continuing without script analysis")
                
                status.update(label="Files prepared successfully!", state="complete")
            
            # Initialize analysis results
            video_analysis = {}
            script_analysis = {}
            audio_analysis = {}
            
            try:
                # Video Analysis
                if analyze_video:
                    with st.status("Analyzing video content...") as status:
                        video_analyzer = components['video_analyzer']
                        scene_detector = components['scene_detector']
                        
                        # Scene detection
                        scene_changes = scene_detector.detect_scenes(video_path, method='combined')
                        video_analysis['scene_changes'] = scene_changes
                        
                        # Video timeline analysis
                        timeline_analysis = video_analyzer.analyze_video_timeline(video_path)
                        video_analysis.update(timeline_analysis)
                        
                        status.update(
                            label=f"Video analysis complete! Found {len(scene_changes)} scene changes",
                            state="complete"
                        )
                
                # Audio Analysis  
                if analyze_audio:
                    with st.status("Analyzing audio content...") as status:
                        audio_analyzer = components['audio_analyzer']
                        
                        # Extract audio from video
                        audio_path = audio_analyzer.extract_audio_from_video(video_path)
                        
                        # Audio feature extraction
                        audio_features = audio_analyzer.extract_audio_features(audio_path)
                        audio_analysis['features'] = audio_features
                        
                        # Speech emotion analysis
                        speech_emotions = audio_analyzer.analyze_speech_emotion(audio_path)
                        audio_analysis['speech_emotions'] = speech_emotions
                        
                        # Speaker change detection
                        speaker_changes = audio_analyzer.detect_speaker_changes(audio_path)
                        audio_analysis['speaker_changes'] = speaker_changes
                        
                        # Audio energy analysis
                        energy_timeline = audio_analyzer.analyze_audio_energy(audio_path)
                        audio_analysis['energy_timeline'] = energy_timeline
                        
                        status.update(
                            label=f"Audio analysis complete! Found {len(speaker_changes)} potential speaker changes",
                            state="complete"
                        )
                
                # Script Analysis
                if analyze_script and script_path:
                    with st.status("Analyzing script content...") as status:
                        script_parser = components['script_parser']
                        timeline_sync = components['timeline_sync']
                        
                        # Parse script
                        dialogue_data = script_parser.parse_script_file(script_path)
                        
                        # Emotion analysis
                        dialogue_with_emotions = script_parser.analyze_emotions(dialogue_data)
                        
                        # Align script to video duration
                        video_duration = audio_analysis.get('features', {}).get('duration', 60)
                        aligned_dialogue = timeline_sync.align_script_to_video(
                            dialogue_with_emotions, video_duration
                        )
                        
                        # Detect emotional beats
                        emotional_beats = script_parser.detect_emotional_beats(aligned_dialogue)
                        
                        script_analysis['dialogue_data'] = aligned_dialogue
                        script_analysis['emotional_beats'] = emotional_beats
                        
                        status.update(
                            label=f"Script analysis complete! Found {len(emotional_beats)} emotional beats",
                            state="complete"
                        )
                
                # Generate AI Suggestions
                with st.status("Generating AI suggestions...") as status:
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
                    
                    status.update(
                        label=f"AI analysis complete! Generated {len(cut_suggestions)} cut suggestions",
                        state="complete"
                    )
                
                # Display Results
                if cut_suggestions:
                    st.success(f"✅ Analysis complete! Generated {len(cut_suggestions)} cut suggestions and {len(transition_suggestions)} transition recommendations.")
                    
                    st.header("📊 Analysis Results")
                    
                    # Timeline Visualization
                    timeline_viewer = components['timeline_viewer']
                    
                    # Create main timeline
                    timeline_fig = timeline_viewer.create_timeline_visualization(
                        audio_analysis.get('features', {}).get('duration', 60),
                        cut_suggestions,
                        transition_suggestions,
                        audio_analysis.get('speech_emotions', [])
                    )
                    
                    st.plotly_chart(timeline_fig, use_container_width=True)
                    
                    # Suggestion summary chart
                    summary_fig = timeline_viewer.create_suggestion_summary_chart(cut_suggestions)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.plotly_chart(summary_fig, use_container_width=True)
                    
                    with col2:
                        # Display statistics
                        st.subheader("📈 Analysis Statistics")
                        
                        total_duration = audio_analysis.get('features', {}).get('duration', 0)
                        avg_confidence = sum(s.confidence for s in cut_suggestions) / len(cut_suggestions)
                        
                        st.metric("Video Duration", f"{total_duration:.1f} seconds")
                        st.metric("Total Suggestions", len(cut_suggestions))
                        st.metric("Average Confidence", f"{avg_confidence:.1%}")
                        st.metric("High Confidence Cuts", len([s for s in cut_suggestions if s.confidence > 0.7]))
                    
                    # Interactive Suggestion Panel
                    suggestion_panel = components['suggestion_panel']
                    
                    # Render suggestion controls
                    filters = suggestion_panel.render_suggestion_controls()
                    
                    # Render suggestion list
                    selected_suggestions = suggestion_panel.render_suggestion_list(
                        cut_suggestions, filters, transition_suggestions
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
