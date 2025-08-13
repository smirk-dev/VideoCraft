import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import sqlite3
import pickle
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class UserAction:
    """Represents a user action for learning purposes."""
    action_type: str  # 'cut_edit', 'approval', 'rejection', 'timeline_navigation', etc.
    timestamp: datetime
    video_id: str
    action_data: Dict[str, Any]
    context: Dict[str, Any]
    outcome: Optional[str] = None

@dataclass
class UserPreference:
    """Represents learned user preferences."""
    preference_type: str
    value: Any
    confidence: float
    last_updated: datetime
    evidence_count: int

class AIUserLearningSystem:
    """
    Advanced AI system that learns from user behavior to personalize
    video editing suggestions and improve over time.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.db_path = config.get('user_db_path', 'user_learning.db')
        self.learning_rate = config.get('learning_rate', 0.1)
        self.min_evidence_threshold = config.get('min_evidence_threshold', 5)
        
        # Initialize database
        self._init_database()
        
        # Learning models
        self.preference_models = {
            'cut_timing': CutTimingLearner(),
            'transition_style': TransitionStyleLearner(),
            'content_preferences': ContentPreferenceLearner(),
            'editing_pace': EditingPaceLearner(),
            'quality_standards': QualityStandardsLearner()
        }
        
        # Session tracking
        if 'learning_session' not in st.session_state:
            st.session_state.learning_session = {
                'session_id': self._generate_session_id(),
                'start_time': datetime.now(),
                'actions': [],
                'current_video': None,
                'user_profile': self._load_user_profile()
            }
    
    def _init_database(self):
        """Initialize SQLite database for user learning data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                action_type TEXT,
                timestamp TEXT,
                video_id TEXT,
                action_data TEXT,
                context TEXT,
                outcome TEXT
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_type TEXT,
                value TEXT,
                confidence REAL,
                last_updated TEXT,
                evidence_count INTEGER,
                UNIQUE(preference_type)
            )
        ''')
        
        # Video processing history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT,
                video_hash TEXT,
                processing_date TEXT,
                final_cuts TEXT,
                user_satisfaction REAL,
                processing_time REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:12]
    
    def track_user_action(self, 
                         action_type: str,
                         action_data: Dict[str, Any],
                         context: Dict[str, Any] = None,
                         video_id: str = None) -> UserAction:
        """
        Track a user action for learning purposes.
        
        Args:
            action_type: Type of action (e.g., 'cut_approval', 'timeline_edit')
            action_data: Specific data about the action
            context: Additional context (video metadata, UI state, etc.)
            video_id: Current video identifier
            
        Returns:
            UserAction object
        """
        
        action = UserAction(
            action_type=action_type,
            timestamp=datetime.now(),
            video_id=video_id or st.session_state.learning_session.get('current_video'),
            action_data=action_data,
            context=context or {}
        )
        
        # Add to session
        st.session_state.learning_session['actions'].append(action)
        
        # Store in database
        self._store_action(action)
        
        # Process for immediate learning
        self._process_action_for_learning(action)
        
        logger.info(f"Tracked user action: {action_type}")
        return action
    
    def _store_action(self, action: UserAction):
        """Store action in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_actions 
            (session_id, action_type, timestamp, video_id, action_data, context, outcome)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            st.session_state.learning_session['session_id'],
            action.action_type,
            action.timestamp.isoformat(),
            action.video_id,
            json.dumps(action.action_data),
            json.dumps(action.context),
            action.outcome
        ))
        
        conn.commit()
        conn.close()
    
    def _process_action_for_learning(self, action: UserAction):
        """Process action for immediate learning updates."""
        
        # Route to appropriate learning model
        if action.action_type in ['cut_approval', 'cut_rejection', 'cut_edit']:
            self.preference_models['cut_timing'].update(action)
        
        elif action.action_type in ['transition_selection', 'transition_edit']:
            self.preference_models['transition_style'].update(action)
        
        elif action.action_type in ['content_rating', 'style_preference']:
            self.preference_models['content_preferences'].update(action)
        
        elif action.action_type in ['timeline_navigation', 'editing_speed']:
            self.preference_models['editing_pace'].update(action)
        
        elif action.action_type in ['quality_rating', 'export_settings']:
            self.preference_models['quality_standards'].update(action)
    
    def get_personalized_suggestions(self, 
                                   base_suggestions: List[Dict],
                                   video_context: Dict) -> List[Dict]:
        """
        Personalize suggestions based on learned user preferences.
        
        Args:
            base_suggestions: Original AI suggestions
            video_context: Context about current video
            
        Returns:
            Personalized suggestions
        """
        
        user_profile = st.session_state.learning_session['user_profile']
        personalized = []
        
        for suggestion in base_suggestions:
            # Apply learned preferences
            personalized_suggestion = suggestion.copy()
            
            # Adjust based on cut timing preferences
            timing_adjustment = self.preference_models['cut_timing'].adjust_suggestion(
                suggestion, user_profile, video_context
            )
            personalized_suggestion.update(timing_adjustment)
            
            # Adjust based on transition preferences
            transition_adjustment = self.preference_models['transition_style'].adjust_suggestion(
                suggestion, user_profile, video_context
            )
            personalized_suggestion.update(transition_adjustment)
            
            # Adjust confidence based on historical accuracy
            confidence_adjustment = self._calculate_confidence_adjustment(
                suggestion, user_profile
            )
            personalized_suggestion['confidence'] *= confidence_adjustment
            
            # Add personalization metadata
            personalized_suggestion['personalization'] = {
                'original_confidence': suggestion.get('confidence', 0.5),
                'adjustments_applied': ['timing', 'transition', 'confidence'],
                'user_profile_version': user_profile.get('version', 1)
            }
            
            personalized.append(personalized_suggestion)
        
        # Sort by personalized confidence
        personalized.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return personalized
    
    def _calculate_confidence_adjustment(self, 
                                       suggestion: Dict,
                                       user_profile: Dict) -> float:
        """Calculate confidence adjustment based on user history."""
        
        suggestion_type = suggestion.get('type', 'unknown')
        historical_accuracy = user_profile.get('accuracy_by_type', {}).get(suggestion_type, 0.5)
        
        # Boost confidence for types user typically agrees with
        if historical_accuracy > 0.7:
            return 1.2
        elif historical_accuracy < 0.3:
            return 0.8
        else:
            return 1.0
    
    def _load_user_profile(self) -> Dict:
        """Load user profile from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_preferences')
        preferences = cursor.fetchall()
        
        profile = {
            'version': 1,
            'preferences': {},
            'accuracy_by_type': {},
            'last_updated': datetime.now().isoformat()
        }
        
        for pref in preferences:
            _, pref_type, value, confidence, last_updated, evidence_count = pref
            profile['preferences'][pref_type] = {
                'value': json.loads(value),
                'confidence': confidence,
                'last_updated': last_updated,
                'evidence_count': evidence_count
            }
        
        # Calculate accuracy by type from historical data
        cursor.execute('''
            SELECT action_type, action_data, outcome 
            FROM user_actions 
            WHERE outcome IS NOT NULL
        ''')
        actions = cursor.fetchall()
        
        accuracy_counts = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for action_type, action_data, outcome in actions:
            if outcome in ['approved', 'accepted']:
                accuracy_counts[action_type]['correct'] += 1
            accuracy_counts[action_type]['total'] += 1
        
        for action_type, counts in accuracy_counts.items():
            if counts['total'] > 0:
                profile['accuracy_by_type'][action_type] = counts['correct'] / counts['total']
        
        conn.close()
        return profile
    
    def render_learning_dashboard(self) -> Dict:
        """Render user learning dashboard."""
        
        st.subheader("🧠 AI Learning Dashboard")
        
        with st.expander("📊 Learning Insights", expanded=False):
            self._render_learning_statistics()
        
        with st.expander("⚙️ Personalization Settings", expanded=False):
            personalization_settings = self._render_personalization_settings()
        
        with st.expander("📈 Learning Progress", expanded=False):
            self._render_learning_progress()
        
        # Quick feedback section
        feedback_data = self._render_quick_feedback()
        
        return {
            'personalization_settings': personalization_settings,
            'feedback_data': feedback_data
        }
    
    def _render_learning_statistics(self):
        """Render learning statistics."""
        
        # Get recent statistics
        conn = sqlite3.connect(self.db_path)
        
        # Action counts by type
        df_actions = pd.read_sql_query('''
            SELECT action_type, COUNT(*) as count 
            FROM user_actions 
            WHERE timestamp > date('now', '-30 days')
            GROUP BY action_type
        ''', conn)
        
        if not df_actions.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Recent Actions (Last 30 Days)**")
                for _, row in df_actions.iterrows():
                    st.write(f"• {row['action_type'].replace('_', ' ').title()}: {row['count']}")
            
            with col2:
                # Action distribution pie chart
                import plotly.express as px
                fig = px.pie(df_actions, values='count', names='action_type', 
                            title="Action Distribution")
                st.plotly_chart(fig, use_container_width=True)
        
        # Accuracy trends
        df_accuracy = pd.read_sql_query('''
            SELECT 
                DATE(timestamp) as date,
                action_type,
                CASE WHEN outcome IN ('approved', 'accepted') THEN 1 ELSE 0 END as correct
            FROM user_actions 
            WHERE outcome IS NOT NULL 
            AND timestamp > date('now', '-30 days')
        ''', conn)
        
        if not df_accuracy.empty:
            daily_accuracy = df_accuracy.groupby('date')['correct'].mean().reset_index()
            
            fig = px.line(daily_accuracy, x='date', y='correct', 
                         title="Daily Accuracy Trend",
                         labels={'correct': 'Accuracy', 'date': 'Date'})
            st.plotly_chart(fig, use_container_width=True)
        
        conn.close()
    
    def _render_personalization_settings(self) -> Dict:
        """Render personalization settings controls."""
        
        st.write("**Personalization Controls**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            learning_enabled = st.checkbox(
                "Enable AI Learning",
                value=True,
                help="Allow the AI to learn from your editing choices"
            )
            
            aggressive_learning = st.checkbox(
                "Aggressive Learning",
                value=False,
                help="Learn more quickly from fewer examples (may be less stable)"
            )
            
            suggestion_adaptation = st.slider(
                "Suggestion Adaptation Level",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                help="How much to adapt suggestions based on your preferences"
            )
        
        with col2:
            preserve_preferences = st.checkbox(
                "Preserve Preferences",
                value=True,
                help="Keep learned preferences across sessions"
            )
            
            if st.button("🔄 Reset Learning Data"):
                if st.confirm("Are you sure? This will delete all learned preferences."):
                    self._reset_learning_data()
                    st.success("Learning data reset successfully!")
                    st.rerun()
            
            if st.button("📤 Export Profile"):
                profile_data = self._export_user_profile()
                st.download_button(
                    "Download Profile",
                    data=profile_data,
                    file_name=f"videoCraft_profile_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        
        return {
            'learning_enabled': learning_enabled,
            'aggressive_learning': aggressive_learning,
            'suggestion_adaptation': suggestion_adaptation,
            'preserve_preferences': preserve_preferences
        }
    
    def _render_learning_progress(self):
        """Render learning progress visualization."""
        
        user_profile = st.session_state.learning_session['user_profile']
        preferences = user_profile.get('preferences', {})
        
        if preferences:
            st.write("**Learned Preferences**")
            
            for pref_type, pref_data in preferences.items():
                confidence = pref_data.get('confidence', 0)
                evidence_count = pref_data.get('evidence_count', 0)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{pref_type.replace('_', ' ').title()}**")
                
                with col2:
                    st.progress(confidence, text=f"Confidence: {confidence:.1%}")
                
                with col3:
                    st.write(f"Evidence: {evidence_count}")
                
                # Show specific preference values
                value = pref_data.get('value', {})
                if isinstance(value, dict) and value:
                    for k, v in value.items():
                        st.write(f"  • {k}: {v}")
        else:
            st.info("No preferences learned yet. Keep using VideoCraft to build your profile!")
    
    def _render_quick_feedback(self) -> Dict:
        """Render quick feedback section."""
        
        st.subheader("💬 Quick Feedback")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**How satisfied are you with today's suggestions?**")
            satisfaction = st.slider(
                "Satisfaction Level",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Very Poor, 5 = Excellent"
            )
            
            if st.button("📝 Submit Feedback"):
                self.track_user_action(
                    'satisfaction_rating',
                    {'rating': satisfaction, 'session_id': st.session_state.learning_session['session_id']},
                    {'feedback_type': 'session_satisfaction'}
                )
                st.success("Thank you for your feedback!")
        
        with col2:
            st.write("**Specific Feedback**")
            feedback_text = st.text_area(
                "Comments",
                placeholder="Tell us what worked well or could be improved...",
                height=100
            )
            
            if st.button("💾 Save Comment") and feedback_text:
                self.track_user_action(
                    'text_feedback',
                    {'comment': feedback_text},
                    {'feedback_type': 'free_text'}
                )
                st.success("Feedback saved!")
        
        return {
            'satisfaction': satisfaction,
            'feedback_text': feedback_text
        }
    
    def _reset_learning_data(self):
        """Reset all learning data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM user_actions')
        cursor.execute('DELETE FROM user_preferences')
        cursor.execute('DELETE FROM video_history')
        
        conn.commit()
        conn.close()
        
        # Reset session state
        st.session_state.learning_session['user_profile'] = {
            'version': 1,
            'preferences': {},
            'accuracy_by_type': {},
            'last_updated': datetime.now().isoformat()
        }
    
    def _export_user_profile(self) -> str:
        """Export user profile as JSON."""
        user_profile = st.session_state.learning_session['user_profile']
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'profile_version': user_profile.get('version', 1),
            'preferences': user_profile.get('preferences', {}),
            'accuracy_stats': user_profile.get('accuracy_by_type', {}),
            'session_count': len(st.session_state.learning_session.get('actions', [])),
            'application': 'VideoCraft',
            'format_version': '1.0'
        }
        
        return json.dumps(export_data, indent=2)


class CutTimingLearner:
    """Learns user preferences for cut timing."""
    
    def __init__(self):
        self.timing_preferences = {
            'preferred_cut_duration': 3.0,  # seconds
            'min_cut_duration': 1.0,
            'max_cut_duration': 10.0,
            'confidence': 0.1
        }
    
    def update(self, action: UserAction):
        """Update cut timing preferences based on user action."""
        try:
            if action.action_type in ['cut_approval', 'cut_edit']:
                action_data = action.action_data
                
                # Extract timing information
                if 'cut_duration' in action_data:
                    duration = action_data['cut_duration']
                    
                    # Update preferred duration with weighted average
                    current_pref = self.timing_preferences['preferred_cut_duration']
                    weight = 0.1  # Learning rate
                    
                    if action.action_type == 'cut_approval':
                        # User approved this duration - move towards it
                        self.timing_preferences['preferred_cut_duration'] = (
                            current_pref * (1 - weight) + duration * weight
                        )
                    elif action.action_type == 'cut_edit':
                        # User edited - learn from the final duration
                        final_duration = action_data.get('final_duration', duration)
                        self.timing_preferences['preferred_cut_duration'] = (
                            current_pref * (1 - weight) + final_duration * weight
                        )
                    
                    # Update confidence
                    self.timing_preferences['confidence'] = min(
                        self.timing_preferences['confidence'] + 0.1, 1.0
                    )
                    
                    logger.info(f"Updated cut timing preference: {self.timing_preferences['preferred_cut_duration']:.2f}s")
                    
        except Exception as e:
            logger.error(f"Error updating cut timing preferences: {e}")
    
    def adjust_suggestion(self, suggestion: Dict, user_profile: Dict, context: Dict) -> Dict:
        """Adjust cut timing based on learned preferences."""
        try:
            adjustments = {}
            
            if self.timing_preferences['confidence'] > 0.3:
                current_duration = suggestion.get('duration', 3.0)
                preferred_duration = self.timing_preferences['preferred_cut_duration']
                
                # Adjust duration towards user preference
                adjustment_factor = 0.3 * self.timing_preferences['confidence']
                new_duration = (
                    current_duration * (1 - adjustment_factor) + 
                    preferred_duration * adjustment_factor
                )
                
                adjustments['duration'] = new_duration
                adjustments['timing_confidence'] = self.timing_preferences['confidence']
                
            return adjustments
            
        except Exception as e:
            logger.error(f"Error adjusting cut timing: {e}")
            return {}


class TransitionStyleLearner:
    """Learns user preferences for transition styles."""
    
    def __init__(self):
        self.style_preferences = {
            'preferred_styles': {'cut': 0.7, 'fade': 0.2, 'dissolve': 0.1},
            'style_confidence': 0.1
        }
    
    def update(self, action: UserAction):
        """Update transition style preferences."""
        try:
            if action.action_type in ['transition_selection', 'transition_edit']:
                action_data = action.action_data
                
                if 'transition_type' in action_data:
                    transition_type = action_data['transition_type']
                    
                    # Increase preference for selected/approved transitions
                    current_prefs = self.style_preferences['preferred_styles']
                    
                    if action.action_type == 'transition_selection':
                        # Boost selected transition
                        for style in current_prefs:
                            if style == transition_type:
                                current_prefs[style] = min(current_prefs[style] + 0.05, 1.0)
                            else:
                                current_prefs[style] = max(current_prefs[style] - 0.01, 0.0)
                    
                    # Normalize preferences
                    total = sum(current_prefs.values())
                    if total > 0:
                        for style in current_prefs:
                            current_prefs[style] /= total
                    
                    # Update confidence
                    self.style_preferences['style_confidence'] = min(
                        self.style_preferences['style_confidence'] + 0.1, 1.0
                    )
                    
                    logger.info(f"Updated transition preferences: {current_prefs}")
                    
        except Exception as e:
            logger.error(f"Error updating transition preferences: {e}")
    
    def adjust_suggestion(self, suggestion: Dict, user_profile: Dict, context: Dict) -> Dict:
        """Adjust transition style based on preferences."""
        try:
            adjustments = {}
            
            if self.style_preferences['style_confidence'] > 0.3:
                current_style = suggestion.get('transition_type', 'cut')
                preferred_styles = self.style_preferences['preferred_styles']
                
                # Find best matching style
                best_style = max(preferred_styles.items(), key=lambda x: x[1])
                
                if best_style[1] > 0.5:  # Strong preference
                    adjustments['transition_type'] = best_style[0]
                    adjustments['style_confidence'] = self.style_preferences['style_confidence']
                
            return adjustments
            
        except Exception as e:
            logger.error(f"Error adjusting transition style: {e}")
            return {}


class ContentPreferenceLearner:
    """Learns user content preferences."""
    
    def __init__(self):
        self.content_preferences = {
            'preferred_content_types': defaultdict(float),
            'scene_preferences': defaultdict(float),
            'confidence': 0.1
        }
    
    def update(self, action: UserAction):
        """Update content preferences."""
        try:
            if action.action_type in ['content_rating', 'scene_approval']:
                action_data = action.action_data
                context = action.context
                
                # Learn from content ratings
                if 'content_type' in context:
                    content_type = context['content_type']
                    rating = action_data.get('rating', 3)
                    
                    # Update preference based on rating (1-5 scale)
                    normalized_rating = (rating - 3) / 2  # Convert to -1 to 1
                    self.content_preferences['preferred_content_types'][content_type] += normalized_rating * 0.1
                
                # Learn from scene approvals
                if 'scene_type' in context:
                    scene_type = context['scene_type']
                    if action.action_type == 'scene_approval':
                        self.content_preferences['scene_preferences'][scene_type] += 0.1
                
                # Update confidence
                self.content_preferences['confidence'] = min(
                    self.content_preferences['confidence'] + 0.05, 1.0
                )
                
        except Exception as e:
            logger.error(f"Error updating content preferences: {e}")
    
    def adjust_suggestion(self, suggestion: Dict, user_profile: Dict, context: Dict) -> Dict:
        """Adjust based on content preferences."""
        try:
            adjustments = {}
            
            if self.content_preferences['confidence'] > 0.2:
                scene_type = context.get('scene_type')
                if scene_type and scene_type in self.content_preferences['scene_preferences']:
                    preference_score = self.content_preferences['scene_preferences'][scene_type]
                    
                    if preference_score > 0.3:
                        # Boost confidence for preferred content
                        adjustments['content_boost'] = 1.2
                    elif preference_score < -0.3:
                        # Reduce confidence for disliked content
                        adjustments['content_boost'] = 0.8
                    else:
                        adjustments['content_boost'] = 1.0
            
            return adjustments
            
        except Exception as e:
            logger.error(f"Error adjusting content preferences: {e}")
            return {}


class EditingPaceLearner:
    """Learns user editing pace preferences."""
    
    def __init__(self):
        self.pace_preferences = {
            'preferred_pace': 'medium',  # slow, medium, fast
            'cuts_per_minute': 10.0,
            'confidence': 0.1
        }
    
    def update(self, action: UserAction):
        """Update editing pace preferences."""
        try:
            if action.action_type in ['timeline_navigation', 'editing_speed']:
                action_data = action.action_data
                
                # Learn from editing speed
                if 'cuts_per_minute' in action_data:
                    cpm = action_data['cuts_per_minute']
                    current_cpm = self.pace_preferences['cuts_per_minute']
                    
                    # Weighted average
                    self.pace_preferences['cuts_per_minute'] = (
                        current_cpm * 0.9 + cpm * 0.1
                    )
                    
                    # Classify pace
                    if self.pace_preferences['cuts_per_minute'] < 5:
                        self.pace_preferences['preferred_pace'] = 'slow'
                    elif self.pace_preferences['cuts_per_minute'] > 15:
                        self.pace_preferences['preferred_pace'] = 'fast'
                    else:
                        self.pace_preferences['preferred_pace'] = 'medium'
                
                # Update confidence
                self.pace_preferences['confidence'] = min(
                    self.pace_preferences['confidence'] + 0.1, 1.0
                )
                
        except Exception as e:
            logger.error(f"Error updating pace preferences: {e}")
    
    def adjust_suggestion(self, suggestion: Dict, user_profile: Dict, context: Dict) -> Dict:
        """Adjust based on editing pace."""
        try:
            adjustments = {}
            
            if self.pace_preferences['confidence'] > 0.3:
                preferred_pace = self.pace_preferences['preferred_pace']
                
                # Adjust number of cuts based on pace preference
                current_cuts = suggestion.get('estimated_cuts', 10)
                
                if preferred_pace == 'fast':
                    adjustments['estimated_cuts'] = int(current_cuts * 1.3)
                elif preferred_pace == 'slow':
                    adjustments['estimated_cuts'] = int(current_cuts * 0.7)
                
                adjustments['pace_preference'] = preferred_pace
            
            return adjustments
            
        except Exception as e:
            logger.error(f"Error adjusting editing pace: {e}")
            return {}


class QualityStandardsLearner:
    """Learns user quality standards."""
    
    def __init__(self):
        self.quality_preferences = {
            'min_confidence_threshold': 0.5,
            'quality_vs_speed': 0.5,  # 0 = speed, 1 = quality
            'confidence': 0.1
        }
    
    def update(self, action: UserAction):
        """Update quality standards."""
        try:
            if action.action_type in ['quality_rating', 'export_settings']:
                action_data = action.action_data
                
                # Learn from quality ratings
                if 'quality_rating' in action_data:
                    rating = action_data['quality_rating']
                    confidence = action_data.get('suggestion_confidence', 0.5)
                    
                    # If user rated low quality highly, lower threshold
                    # If user rated high quality lowly, raise threshold
                    if rating >= 4 and confidence < self.quality_preferences['min_confidence_threshold']:
                        self.quality_preferences['min_confidence_threshold'] -= 0.05
                    elif rating <= 2 and confidence > self.quality_preferences['min_confidence_threshold']:
                        self.quality_preferences['min_confidence_threshold'] += 0.05
                
                # Learn from export settings
                if 'export_quality' in action_data:
                    export_quality = action_data['export_quality']
                    if export_quality in ['high', 'ultra']:
                        self.quality_preferences['quality_vs_speed'] += 0.1
                    elif export_quality in ['fast', 'draft']:
                        self.quality_preferences['quality_vs_speed'] -= 0.1
                
                # Clamp values
                self.quality_preferences['min_confidence_threshold'] = max(0.1, min(0.9, 
                    self.quality_preferences['min_confidence_threshold']))
                self.quality_preferences['quality_vs_speed'] = max(0.0, min(1.0,
                    self.quality_preferences['quality_vs_speed']))
                
                # Update confidence
                self.quality_preferences['confidence'] = min(
                    self.quality_preferences['confidence'] + 0.1, 1.0
                )
                
        except Exception as e:
            logger.error(f"Error updating quality standards: {e}")
    
    def adjust_suggestion(self, suggestion: Dict, user_profile: Dict, context: Dict) -> Dict:
        """Adjust based on quality standards."""
        try:
            adjustments = {}
            
            if self.quality_preferences['confidence'] > 0.3:
                min_threshold = self.quality_preferences['min_confidence_threshold']
                current_confidence = suggestion.get('confidence', 0.5)
                
                # Filter out suggestions below user's quality threshold
                if current_confidence < min_threshold:
                    adjustments['quality_filtered'] = True
                    adjustments['reason'] = 'Below user quality threshold'
                
                # Adjust processing quality based on preference
                quality_pref = self.quality_preferences['quality_vs_speed']
                if quality_pref > 0.7:
                    adjustments['processing_quality'] = 'high'
                elif quality_pref < 0.3:
                    adjustments['processing_quality'] = 'fast'
                else:
                    adjustments['processing_quality'] = 'balanced'
                
            return adjustments
            
        except Exception as e:
            logger.error(f"Error adjusting quality standards: {e}")
            return {}
