import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

class InteractiveTimelineEditor:
    """
    Advanced interactive timeline editor with drag-and-drop functionality,
    real-time preview, and professional editing controls.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.timeline_height = config.get('timeline_height', 400)
        self.zoom_levels = config.get('zoom_levels', [1, 5, 10, 30, 60, 300])
        
        # Initialize session state for timeline
        if 'timeline_state' not in st.session_state:
            st.session_state.timeline_state = {
                'zoom_level': 10,
                'selected_cuts': [],
                'custom_cuts': [],
                'timeline_position': 0.0,
                'preview_range': (0.0, 30.0),
                'edited_suggestions': {},
                'timeline_tracks': {
                    'video': True,
                    'audio': True,
                    'cuts': True,
                    'emotions': True,
                    'music': False
                }
            }
    
    def render_advanced_timeline(self, 
                                video_duration: float,
                                cut_suggestions: List[Dict],
                                audio_analysis: Dict,
                                emotion_timeline: List[Dict] = None,
                                music_data: Dict = None) -> Dict:
        """
        Render advanced interactive timeline with multiple tracks.
        
        Args:
            video_duration: Total video duration in seconds
            cut_suggestions: AI-generated cut suggestions
            audio_analysis: Audio analysis results
            emotion_timeline: Emotion analysis over time
            music_data: Music synchronization data
            
        Returns:
            Dictionary with user interactions and selections
        """
        
        st.subheader("🎬 Advanced Timeline Editor")
        
        # Timeline controls
        timeline_controls = self._render_timeline_controls(video_duration)
        
        # Track visibility controls
        track_controls = self._render_track_controls()
        
        # Main timeline
        timeline_fig = self._create_interactive_timeline(
            video_duration, cut_suggestions, audio_analysis, 
            emotion_timeline, music_data, timeline_controls, track_controls
        )
        
        # Render timeline with interaction handling
        selected_data = st.plotly_chart(
            timeline_fig, 
            use_container_width=True,
            key="main_timeline",
            on_select="rerun"
        )
        
        # Handle timeline interactions
        interactions = self._handle_timeline_interactions(selected_data)
        
        # Cut editing panel
        cut_editor = self._render_cut_editor(cut_suggestions)
        
        # Timeline statistics
        self._render_timeline_statistics(cut_suggestions, video_duration)
        
        return {
            'timeline_controls': timeline_controls,
            'track_controls': track_controls,
            'interactions': interactions,
            'cut_editor': cut_editor,
            'selected_cuts': st.session_state.timeline_state['selected_cuts']
        }
    
    def _render_timeline_controls(self, video_duration: float) -> Dict:
        """Render timeline navigation and zoom controls."""
        
        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        
        with col1:
            # Timeline position slider
            current_pos = st.slider(
                "Timeline Position",
                min_value=0.0,
                max_value=video_duration,
                value=st.session_state.timeline_state['timeline_position'],
                step=0.1,
                format="%.1fs",
                key="timeline_position"
            )
            st.session_state.timeline_state['timeline_position'] = current_pos
        
        with col2:
            # Zoom level
            zoom_level = st.selectbox(
                "Zoom (seconds)",
                options=self.zoom_levels,
                index=self.zoom_levels.index(st.session_state.timeline_state['zoom_level']),
                key="timeline_zoom"
            )
            st.session_state.timeline_state['zoom_level'] = zoom_level
        
        with col3:
            # Playback controls
            if st.button("⏮️", help="Go to start"):
                st.session_state.timeline_state['timeline_position'] = 0.0
                st.rerun()
            
            if st.button("⏭️", help="Go to end"):
                st.session_state.timeline_state['timeline_position'] = float(video_duration)
                st.rerun()
        
        with col4:
            # Preview range
            preview_range = st.slider(
                "Preview Range (seconds)",
                min_value=0.0,
                max_value=video_duration,
                value=st.session_state.timeline_state['preview_range'],
                step=1.0,
                key="preview_range"
            )
            st.session_state.timeline_state['preview_range'] = preview_range
        
        return {
            'position': current_pos,
            'zoom': zoom_level,
            'preview_range': preview_range
        }
    
    def _render_track_controls(self) -> Dict:
        """Render track visibility and organization controls."""
        
        st.subheader("📊 Timeline Tracks")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            video_track = st.checkbox(
                "📹 Video Track",
                value=st.session_state.timeline_state['timeline_tracks']['video'],
                key="track_video"
            )
            
            audio_track = st.checkbox(
                "🔊 Audio Track",
                value=st.session_state.timeline_state['timeline_tracks']['audio'],
                key="track_audio"
            )
        
        with col2:
            cuts_track = st.checkbox(
                "✂️ Cut Suggestions",
                value=st.session_state.timeline_state['timeline_tracks']['cuts'],
                key="track_cuts"
            )
            
            emotions_track = st.checkbox(
                "😊 Emotions",
                value=st.session_state.timeline_state['timeline_tracks']['emotions'],
                key="track_emotions"
            )
        
        with col3:
            music_track = st.checkbox(
                "🎵 Music Sync",
                value=st.session_state.timeline_state['timeline_tracks']['music'],
                key="track_music"
            )
            
            if st.button("📊 Add Custom Track"):
                st.info("Custom track functionality coming soon!")
        
        # Update session state
        st.session_state.timeline_state['timeline_tracks'].update({
            'video': video_track,
            'audio': audio_track,
            'cuts': cuts_track,
            'emotions': emotions_track,
            'music': music_track
        })
        
        return st.session_state.timeline_state['timeline_tracks']
    
    def _create_interactive_timeline(self, 
                                   video_duration: float,
                                   cut_suggestions: List[Dict],
                                   audio_analysis: Dict,
                                   emotion_timeline: List[Dict],
                                   music_data: Dict,
                                   timeline_controls: Dict,
                                   track_controls: Dict) -> go.Figure:
        """Create the main interactive timeline visualization."""
        
        # Calculate timeline range based on zoom and position
        zoom = timeline_controls['zoom']
        position = timeline_controls['position']
        
        timeline_start = max(0, position - zoom / 2)
        timeline_end = min(video_duration, position + zoom / 2)
        
        # Create subplot with multiple tracks
        track_count = sum(track_controls.values())
        fig = make_subplots(
            rows=track_count,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=self._get_active_track_titles(track_controls)
        )
        
        row = 1
        
        # Video track
        if track_controls['video']:
            self._add_video_track(fig, row, timeline_start, timeline_end, video_duration)
            row += 1
        
        # Audio track
        if track_controls['audio']:
            self._add_audio_track(fig, row, audio_analysis, timeline_start, timeline_end)
            row += 1
        
        # Cut suggestions track
        if track_controls['cuts']:
            self._add_cuts_track(fig, row, cut_suggestions, timeline_start, timeline_end)
            row += 1
        
        # Emotions track
        if track_controls['emotions'] and emotion_timeline:
            self._add_emotions_track(fig, row, emotion_timeline, timeline_start, timeline_end)
            row += 1
        
        # Music track
        if track_controls['music'] and music_data:
            self._add_music_track(fig, row, music_data, timeline_start, timeline_end)
            row += 1
        
        # Add current position indicator
        self._add_position_indicator(fig, position, track_count)
        
        # Add preview range indicator
        preview_start, preview_end = timeline_controls['preview_range']
        self._add_preview_range(fig, preview_start, preview_end, track_count)
        
        # Configure layout
        fig.update_layout(
            height=self.timeline_height,
            showlegend=True,
            title="Interactive Video Timeline",
            xaxis=dict(
                title="Time (seconds)",
                range=[timeline_start, timeline_end],
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            dragmode='select',
            selectdirection='h'
        )
        
        return fig
    
    def _get_active_track_titles(self, track_controls: Dict) -> List[str]:
        """Get titles for active tracks."""
        titles = []
        if track_controls['video']:
            titles.append("📹 Video")
        if track_controls['audio']:
            titles.append("🔊 Audio")
        if track_controls['cuts']:
            titles.append("✂️ Cuts")
        if track_controls['emotions']:
            titles.append("😊 Emotions")
        if track_controls['music']:
            titles.append("🎵 Music")
        return titles
    
    def _add_video_track(self, fig: go.Figure, row: int, start: float, end: float, duration: float):
        """Add video track to timeline."""
        # Simple video duration bar
        fig.add_trace(
            go.Scatter(
                x=[0, duration],
                y=[0.5, 0.5],
                mode='lines',
                line=dict(color='blue', width=20),
                name='Video Duration',
                hovertemplate='Video: %{x:.1f}s<extra></extra>'
            ),
            row=row, col=1
        )
    
    def _add_audio_track(self, fig: go.Figure, row: int, audio_analysis: Dict, start: float, end: float):
        """Add audio waveform/energy track."""
        energy_timeline = audio_analysis.get('energy_timeline', [])
        
        if energy_timeline:
            # Safe access using start_time and rms_energy keys used across the app
            times = [
                (point.get('start_time', 0.0) if hasattr(point, 'get') else 0.0)
                for point in energy_timeline
            ]
            energies = [
                (point.get('rms_energy', 0.0) if hasattr(point, 'get') else 0.0)
                for point in energy_timeline
            ]
            
            # Filter for visible range
            visible_indices = [i for i, t in enumerate(times) if start <= t <= end]
            if visible_indices:
                visible_times = [times[i] for i in visible_indices]
                visible_energies = [energies[i] for i in visible_indices]
                
                fig.add_trace(
                    go.Scatter(
                        x=visible_times,
                        y=visible_energies,
                        mode='lines',
                        fill='tonexty',
                        line=dict(color='green', width=1),
                        name='Audio Energy',
                        hovertemplate='Audio Energy: %{y:.2f}<br>Time: %{x:.1f}s<extra></extra>'
                    ),
                    row=row, col=1
                )
    
    def _add_cuts_track(self, fig: go.Figure, row: int, cut_suggestions: List[Dict], start: float, end: float):
        """Add cut suggestions track."""
        visible_cuts = [cut for cut in cut_suggestions if start <= cut.get('timestamp', 0) <= end]
        
        if visible_cuts:
            # Safe access to timestamp for CutSuggestion objects
            times = [cut.get('timestamp', 0.0) if hasattr(cut, 'get') else cut.get('timestamp', 0.0) for cut in visible_cuts]
            confidences = [cut.get('confidence', 0.5) for cut in visible_cuts]
            reasons = [cut.get('reason', 'AI suggestion') for cut in visible_cuts]
            
            # Color based on confidence
            colors = ['red' if c > 0.8 else 'orange' if c > 0.6 else 'yellow' for c in confidences]
            
            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=confidences,
                    mode='markers',
                    marker=dict(
                        color=colors,
                        size=[c * 20 + 5 for c in confidences],
                        symbol='line-ns',
                        line=dict(width=2, color='black')
                    ),
                    name='Cut Suggestions',
                    text=reasons,
                    hovertemplate='Cut Suggestion<br>Time: %{x:.1f}s<br>Confidence: %{y:.1%}<br>Reason: %{text}<extra></extra>',
                    customdata=list(range(len(visible_cuts)))  # For selection tracking
                ),
                row=row, col=1
            )
    
    def _add_emotions_track(self, fig: go.Figure, row: int, emotion_timeline: List[Dict], start: float, end: float):
        """Add emotions track."""
        visible_emotions = [emotion for emotion in emotion_timeline if start <= emotion.get('timestamp', 0) <= end]
        
        if visible_emotions:
            # Safe access to timestamp for any object type
            times = [emotion.get('timestamp', 0.0) if hasattr(emotion, 'get') else emotion.get('timestamp', 0.0) for emotion in visible_emotions]
            dominant_emotions = [emotion.get('dominant_emotion', 'neutral') for emotion in visible_emotions]
            confidences = [emotion.get('confidence', 0.5) for emotion in visible_emotions]
            
            # Map emotions to colors
            emotion_colors = {
                'happy': 'yellow',
                'sad': 'blue',
                'angry': 'red',
                'neutral': 'gray',
                'surprised': 'purple',
                'fearful': 'black'
            }
            
            colors = [emotion_colors.get(emotion, 'gray') for emotion in dominant_emotions]
            
            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=confidences,
                    mode='markers',
                    marker=dict(
                        color=colors,
                        size=10,
                        symbol='circle'
                    ),
                    name='Emotions',
                    text=dominant_emotions,
                    hovertemplate='Emotion: %{text}<br>Time: %{x:.1f}s<br>Confidence: %{y:.1%}<extra></extra>'
                ),
                row=row, col=1
            )
    
    def _add_music_track(self, fig: go.Figure, row: int, music_data: Dict, start: float, end: float):
        """Add music synchronization track."""
        beats = music_data.get('beats', [])
        visible_beats = [beat for beat in beats if start <= beat.get('time', 0) <= end]
        
        if visible_beats:
            times = [beat['time'] for beat in visible_beats]
            strengths = [beat.get('strength', 0.5) for beat in visible_beats]
            beat_types = [beat.get('type', 'beat') for beat in visible_beats]
            
            # Different symbols for different beat types
            symbols = ['diamond' if bt == 'downbeat' else 'circle' for bt in beat_types]
            colors = ['red' if bt == 'downbeat' else 'blue' for bt in beat_types]
            
            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=strengths,
                    mode='markers',
                    marker=dict(
                        color=colors,
                        size=8,
                        symbol=symbols
                    ),
                    name='Music Beats',
                    text=beat_types,
                    hovertemplate='Beat: %{text}<br>Time: %{x:.1f}s<br>Strength: %{y:.2f}<extra></extra>'
                ),
                row=row, col=1
            )
    
    def _add_position_indicator(self, fig: go.Figure, position: float, track_count: int):
        """Add current position indicator."""
        fig.add_vline(
            x=position,
            line=dict(color="red", width=3, dash="solid"),
            annotation_text=f"Current: {position:.1f}s",
            annotation_position="top"
        )
    
    def _add_preview_range(self, fig: go.Figure, start: float, end: float, track_count: int):
        """Add preview range indicator."""
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor="rgba(255, 255, 0, 0.2)",
            layer="below",
            line_width=0,
            annotation_text="Preview Range",
            annotation_position="top left"
        )
    
    def _handle_timeline_interactions(self, selected_data) -> Dict:
        """Handle user interactions with the timeline."""
        interactions = {
            'selected_points': [],
            'selected_cuts': [],
            'actions': []
        }
        
        if selected_data and hasattr(selected_data, 'selection'):
            selection = selected_data.selection
            
            if selection and 'points' in selection:
                for point in selection['points']:
                    if 'customdata' in point:
                        cut_index = point['customdata']
                        interactions['selected_cuts'].append(cut_index)
                        st.session_state.timeline_state['selected_cuts'].append(cut_index)
        
        return interactions
    
    def _render_cut_editor(self, cut_suggestions: List[Dict]) -> Dict:
        """Render cut editing controls."""
        
        st.subheader("✂️ Cut Editor")
        
        selected_cuts = st.session_state.timeline_state['selected_cuts']
        
        if not selected_cuts:
            st.info("Select cuts on the timeline to edit them")
            return {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Selected Cuts:** {len(selected_cuts)}")
            
            # Batch operations
            if st.button("✅ Approve Selected"):
                for cut_idx in selected_cuts:
                    if cut_idx < len(cut_suggestions):
                        cut_suggestions[cut_idx]['approved'] = True
                st.success(f"Approved {len(selected_cuts)} cuts")
                st.session_state.timeline_state['selected_cuts'] = []
                st.rerun()
            
            if st.button("❌ Reject Selected"):
                for cut_idx in selected_cuts:
                    if cut_idx < len(cut_suggestions):
                        cut_suggestions[cut_idx]['rejected'] = True
                st.success(f"Rejected {len(selected_cuts)} cuts")
                st.session_state.timeline_state['selected_cuts'] = []
                st.rerun()
        
        with col2:
            # Adjust confidence
            confidence_adjustment = st.slider(
                "Confidence Adjustment",
                min_value=-0.5,
                max_value=0.5,
                value=0.0,
                step=0.1,
                help="Adjust confidence for selected cuts"
            )
            
            if st.button("🔧 Apply Adjustment"):
                for cut_idx in selected_cuts:
                    if cut_idx < len(cut_suggestions):
                        old_confidence = cut_suggestions[cut_idx].get('confidence', 0.5)
                        new_confidence = max(0.0, min(1.0, old_confidence + confidence_adjustment))
                        cut_suggestions[cut_idx]['confidence'] = new_confidence
                st.success(f"Adjusted confidence for {len(selected_cuts)} cuts")
                st.rerun()
        
        # Individual cut editing
        if len(selected_cuts) == 1:
            cut_idx = selected_cuts[0]
            if cut_idx < len(cut_suggestions):
                cut = cut_suggestions[cut_idx]
                
                st.subheader(f"Edit Cut #{cut_idx + 1}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Ensure timestamp is always a float, handle potential type issues
                    timestamp_value = cut.get('timestamp', 0.0)
                    if isinstance(timestamp_value, (list, tuple)):
                        timestamp_value = float(timestamp_value[0]) if timestamp_value else 0.0
                    elif not isinstance(timestamp_value, (int, float)):
                        timestamp_value = 0.0
                    else:
                        timestamp_value = float(timestamp_value)
                    
                    new_timestamp = st.number_input(
                        "Timestamp (seconds)",
                        value=timestamp_value,
                        min_value=0.0,
                        step=0.1,
                        key=f"edit_timestamp_{cut_idx}"
                    )
                    
                    # Ensure confidence is always a float, handle potential type issues
                    confidence_value = cut.get('confidence', 0.5)
                    if isinstance(confidence_value, (list, tuple)):
                        confidence_value = float(confidence_value[0]) if confidence_value else 0.5
                    elif not isinstance(confidence_value, (int, float)):
                        confidence_value = 0.5
                    else:
                        confidence_value = float(confidence_value)
                    
                    new_confidence = st.slider(
                        "Confidence",
                        min_value=0.0,
                        max_value=1.0,
                        value=confidence_value,
                        step=0.01,
                        key=f"edit_confidence_{cut_idx}"
                    )
                
                with col2:
                    new_reason = st.text_input(
                        "Reason",
                        value=cut.get('reason', ''),
                        key=f"edit_reason_{cut_idx}"
                    )
                    
                    new_type = st.selectbox(
                        "Cut Type",
                        options=['cut', 'fade', 'dissolve'],
                        index=0,
                        key=f"edit_type_{cut_idx}"
                    )
                
                if st.button("💾 Save Changes", key=f"save_{cut_idx}"):
                    cut_suggestions[cut_idx].update({
                        'timestamp': new_timestamp,
                        'confidence': new_confidence,
                        'reason': new_reason,
                        'type': new_type,
                        'user_edited': True
                    })
                    st.success("Cut updated successfully!")
                    st.rerun()
        
        return {
            'selected_count': len(selected_cuts),
            'actions_available': ['approve', 'reject', 'adjust', 'edit']
        }
    
    def _render_timeline_statistics(self, cut_suggestions: List[Dict], video_duration: float):
        """Render timeline statistics and insights."""
        
        with st.expander("📊 Timeline Statistics", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_cuts = len(cut_suggestions)
                st.metric("Total Cuts", total_cuts)
            
            with col2:
                approved_cuts = len([c for c in cut_suggestions if c.get('approved', False)])
                st.metric("Approved", approved_cuts)
            
            with col3:
                avg_confidence = np.mean([c.get('confidence', 0) for c in cut_suggestions]) if cut_suggestions else 0
                st.metric("Avg Confidence", f"{avg_confidence:.1%}")
            
            with col4:
                cut_density = total_cuts / video_duration if video_duration > 0 else 0
                st.metric("Cuts/Minute", f"{cut_density * 60:.1f}")
            
            # Cut confidence distribution
            if cut_suggestions:
                confidences = [c.get('confidence', 0) for c in cut_suggestions]
                
                fig = px.histogram(
                    x=confidences,
                    nbins=20,
                    title="Cut Confidence Distribution",
                    labels={'x': 'Confidence', 'y': 'Count'}
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    def export_timeline_project(self, 
                              cut_suggestions: List[Dict],
                              timeline_state: Dict,
                              metadata: Dict) -> str:
        """Export timeline project for later import."""
        
        project_data = {
            'version': '1.0',
            'metadata': metadata,
            'timeline_state': timeline_state,
            'cut_suggestions': cut_suggestions,
            'custom_cuts': st.session_state.timeline_state.get('custom_cuts', []),
            'track_configuration': st.session_state.timeline_state.get('timeline_tracks', {}),
            'export_timestamp': pd.Timestamp.now().isoformat()
        }
        
        import json
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(project_data, f, indent=2)
            return f.name
