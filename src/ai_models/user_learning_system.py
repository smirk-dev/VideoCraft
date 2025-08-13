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
    
    def update(self, action: UserAction):
        """Update cut timing preferences based on user action."""
        # Implementation for learning cut timing preferences
        pass
    
    def adjust_suggestion(self, suggestion: Dict, user_profile: Dict, context: Dict) -> Dict:
        """Adjust cut timing based on learned preferences."""
        # Implementation for adjusting cut timing
        return {}


class TransitionStyleLearner:
    """Learns user preferences for transition styles."""
    
    def update(self, action: UserAction):
        """Update transition style preferences."""
        pass
    
    def adjust_suggestion(self, suggestion: Dict, user_profile: Dict, context: Dict) -> Dict:
        """Adjust transition style based on preferences."""
        return {}


class ContentPreferenceLearner:
    """Learns user content preferences."""
    
    def update(self, action: UserAction):
        """Update content preferences."""
        pass
    
    def adjust_suggestion(self, suggestion: Dict, user_profile: Dict, context: Dict) -> Dict:
        """Adjust based on content preferences."""
        return {}


class EditingPaceLearner:
    """Learns user editing pace preferences."""
    
    def update(self, action: UserAction):
        """Update editing pace preferences."""
        pass
    
    def adjust_suggestion(self, suggestion: Dict, user_profile: Dict, context: Dict) -> Dict:
        """Adjust based on editing pace."""
        return {}


class QualityStandardsLearner:
    """Learns user quality standards."""
    
    def update(self, action: UserAction):
        """Update quality standards."""
        pass
    
    def adjust_suggestion(self, suggestion: Dict, user_profile: Dict, context: Dict) -> Dict:
        """Adjust based on quality standards."""
        return {}
