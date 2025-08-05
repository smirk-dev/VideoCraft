from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np
import logging

logger = logging.getLogger(__name__)

class TransitionType(Enum):
    CUT = "cut"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"  
    DISSOLVE = "dissolve"
    WIPE_LEFT = "wipe_left"
    WIPE_RIGHT = "wipe_right"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    SLIDE = "slide"

@dataclass
class TransitionSuggestion:
    start_time: float
    end_time: float
    transition_type: TransitionType
    confidence: float
    reason: str
    duration: float = 1.0
    metadata: Dict = None

class TransitionRecommender:
    """
    Recommends appropriate transitions based on content analysis and editing context.
    Uses film editing conventions and content analysis to suggest transition types.
    """
    
    def __init__(self, config: dict):
        """
        Initialize TransitionRecommender with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Transition rules based on content analysis
        self.transition_rules = {
            # Emotional transitions
            'emotional_escalation': TransitionType.CUT,
            'emotional_release': TransitionType.FADE_OUT,
            'emotional_buildup': TransitionType.DISSOLVE,
            'dramatic_reveal': TransitionType.CUT,
            
            # Scene type transitions  
            'action_to_dialogue': TransitionType.CUT,
            'dialogue_to_action': TransitionType.CUT,
            'indoor_to_outdoor': TransitionType.DISSOLVE,
            'day_to_night': TransitionType.DISSOLVE,
            'location_change': TransitionType.WIPE_LEFT,
            
            # Time transitions
            'time_jump': TransitionType.FADE_OUT,
            'flashback': TransitionType.DISSOLVE,
            'montage': TransitionType.CUT,
            
            # Mood transitions
            'tense_to_calm': TransitionType.DISSOLVE,
            'calm_to_tense': TransitionType.CUT,
            'happy_to_sad': TransitionType.FADE_OUT,
            'sad_to_happy': TransitionType.FADE_IN
        }
        
        # Default transition durations (seconds)
        self.default_durations = {
            TransitionType.CUT: 0.0,
            TransitionType.FADE_IN: 1.0,
            TransitionType.FADE_OUT: 1.0,
            TransitionType.DISSOLVE: 1.5,
            TransitionType.WIPE_LEFT: 0.8,
            TransitionType.WIPE_RIGHT: 0.8,
            TransitionType.ZOOM_IN: 1.2,
            TransitionType.ZOOM_OUT: 1.2,
            TransitionType.SLIDE: 0.6
        }
    
    def suggest_transitions(self, 
                          cut_suggestions: List,
                          emotion_analysis: List[Dict],
                          visual_analysis: Dict,
                          script_analysis: Optional[Dict] = None) -> List[TransitionSuggestion]:
        """
        Generate transition suggestions for cut points.
        
        Args:
            cut_suggestions: List of cut suggestions
            emotion_analysis: Timeline of emotion analysis
            visual_analysis: Visual content analysis
            script_analysis: Optional script analysis data
            
        Returns:
            List of transition suggestions
        """
        logger.info(f"Generating transition suggestions for {len(cut_suggestions)} cuts")
        
        transitions = []
        
        for i, cut in enumerate(cut_suggestions):
            # Analyze context around cut point
            context = self._analyze_cut_context(
                cut.timestamp,
                emotion_analysis,
                visual_analysis,
                script_analysis
            )
            
            # Determine transition type
            transition_type = self._determine_transition_type(context, cut)
            
            # Calculate transition duration and timing
            duration = self._calculate_transition_duration(transition_type, context)
            end_time = cut.timestamp + duration
            
            # Ensure transition doesn't overlap with next cut
            if i + 1 < len(cut_suggestions):
                next_cut_time = cut_suggestions[i + 1].timestamp
                if end_time > next_cut_time - 0.5:  # Leave 0.5s buffer
                    end_time = next_cut_time - 0.5
                    duration = max(0.0, end_time - cut.timestamp)
            
            # Create transition suggestion
            transition = TransitionSuggestion(
                start_time=cut.timestamp,
                end_time=end_time,
                transition_type=transition_type,
                duration=duration,
                confidence=self._calculate_transition_confidence(context),
                reason=self._generate_transition_reason(transition_type, context),
                metadata={
                    'context': context,
                    'cut_type': cut.suggestion_type,
                    'cut_confidence': cut.confidence
                }
            )
            
            transitions.append(transition)
        
        logger.info(f"Generated {len(transitions)} transition suggestions")
        return transitions
    
    def _analyze_cut_context(self, 
                           timestamp: float,
                           emotion_analysis: List[Dict],
                           visual_analysis: Dict,
                           script_analysis: Optional[Dict]) -> Dict:
        """Analyze the context around a cut point."""
        context = {
            'timestamp': timestamp,
            'emotion_before': None,
            'emotion_after': None,
            'emotional_change': 0.0,
            'visual_change_intensity': 0.5,
            'scene_type': 'dialogue',
            'speaker_change': False,
            'time_of_day': 'unknown',
            'location_change': False
        }
        
        # Find emotions before and after cut
        for emotion_data in emotion_analysis:
            start_time = emotion_data.get('start_time', 0)
            end_time = emotion_data.get('end_time', start_time + 5)
            
            if start_time <= timestamp <= end_time:
                context['emotion_before'] = emotion_data.get('emotion', 'neutral')
            elif start_time > timestamp and context['emotion_after'] is None:
                context['emotion_after'] = emotion_data.get('emotion', 'neutral')
                break
        
        # Calculate emotional change
        if context['emotion_before'] and context['emotion_after']:
            context['emotional_change'] = self._calculate_emotional_distance(
                context['emotion_before'], 
                context['emotion_after']
            )
        
        # Analyze visual context from scene detection
        scene_changes = visual_analysis.get('scene_changes', [])
        for scene in scene_changes:
            scene_time = scene.get('timestamp', scene) if isinstance(scene, dict) else scene
            if abs(scene_time - timestamp) < 1.0:  # Within 1 second
                context['visual_change_intensity'] = scene.get('confidence', 0.8) if isinstance(scene, dict) else 0.8
                break
        
        # Determine scene type and other contextual information
        if script_analysis and 'dialogue_data' in script_analysis:
            context.update(self._analyze_script_context(timestamp, script_analysis['dialogue_data']))
        
        return context
    
    def _determine_transition_type(self, context: Dict, cut) -> TransitionType:
        """Determine the most appropriate transition type based on context."""
        
        # Rule-based transition selection
        emotion_before = context.get('emotion_before', 'neutral')
        emotion_after = context.get('emotion_after', 'neutral')
        emotional_change = context.get('emotional_change', 0.0)
        visual_change = context.get('visual_change_intensity', 0.5)
        
        # Strong emotional transitions
        if emotional_change > 0.7:
            if emotion_before in ['sad', 'angry'] and emotion_after in ['happy', 'neutral']:
                return TransitionType.FADE_IN
            elif emotion_before in ['happy', 'neutral'] and emotion_after in ['sad', 'angry']:
                return TransitionType.FADE_OUT
            else:
                return TransitionType.DISSOLVE
        
        # Scene change based transitions
        if cut.suggestion_type == 'scene_change':
            if visual_change > 0.8:
                return TransitionType.CUT  # Sharp visual change = hard cut
            elif context.get('location_change', False):
                return TransitionType.WIPE_LEFT
            else:
                return TransitionType.DISSOLVE
        
        # Speaker change transitions
        if cut.suggestion_type == 'speaker_change' or context.get('speaker_change', False):
            return TransitionType.CUT
        
        # Dialogue-based transitions
        if cut.suggestion_type == 'dialogue_pause':
            if emotional_change > 0.4:
                return TransitionType.DISSOLVE
            else:
                return TransitionType.CUT
        
        # Default based on visual change intensity
        if visual_change > 0.6:
            return TransitionType.CUT
        else:
            return TransitionType.DISSOLVE
    
    def _calculate_transition_duration(self, transition_type: TransitionType, context: Dict) -> float:
        """Calculate appropriate duration for transition."""
        base_duration = self.default_durations.get(transition_type, 1.0)
        
        # Adjust based on context
        emotional_change = context.get('emotional_change', 0.0)
        
        # Longer transitions for significant emotional changes
        if emotional_change > 0.5:
            base_duration *= 1.5
        
        # Shorter transitions for dialogue scenes
        if context.get('scene_type') == 'dialogue':
            base_duration *= 0.8
        
        return max(0.0, min(base_duration, 3.0))  # Cap at 3 seconds
    
    def _calculate_transition_confidence(self, context: Dict) -> float:
        """Calculate confidence score for transition recommendation."""
        base_confidence = 0.7
        
        # Higher confidence for strong contextual cues
        if context.get('emotional_change', 0) > 0.5:
            base_confidence += 0.1
        
        if context.get('visual_change_intensity', 0) > 0.7:
            base_confidence += 0.1
        
        if context.get('speaker_change', False):
            base_confidence += 0.05
        
        return min(1.0, base_confidence)
    
    def _generate_transition_reason(self, transition_type: TransitionType, context: Dict) -> str:
        """Generate human-readable reason for transition choice."""
        emotion_before = context.get('emotion_before')
        emotion_after = context.get('emotion_after')
        emotional_change = context.get('emotional_change', 0)
        
        if transition_type == TransitionType.CUT:
            if context.get('speaker_change'):
                return "Sharp cut for speaker change"
            elif context.get('visual_change_intensity', 0) > 0.7:
                return "Hard cut for dramatic scene change"
            else:
                return "Standard cut for dialogue flow"
        
        elif transition_type == TransitionType.DISSOLVE:
            if emotional_change > 0.5:
                return f"Dissolve for emotional transition ({emotion_before} → {emotion_after})"
            elif context.get('location_change'):
                return "Dissolve for smooth location transition"
            else:
                return "Dissolve for gentle scene transition"
        
        elif transition_type == TransitionType.FADE_OUT:
            return f"Fade out for emotional release ({emotion_before} → {emotion_after})"
        
        elif transition_type == TransitionType.FADE_IN:
            return f"Fade in for emotional buildup ({emotion_before} → {emotion_after})"
        
        elif transition_type in [TransitionType.WIPE_LEFT, TransitionType.WIPE_RIGHT]:
            return "Wipe transition for location change"
        
        else:
            return f"Recommended {transition_type.value} transition"
    
    def _calculate_emotional_distance(self, emotion1: str, emotion2: str) -> float:
        """Calculate emotional distance between two emotions."""
        # Define emotion valence and arousal (simplified model)
        emotion_space = {
            'happy': (0.8, 0.6),     # positive, medium arousal
            'sad': (-0.8, -0.4),      # negative, low arousal  
            'angry': (-0.6, 0.8),     # negative, high arousal
            'fearful': (-0.7, 0.7),   # negative, high arousal
            'surprised': (0.3, 0.8),  # slightly positive, high arousal
            'disgusted': (-0.9, 0.2), # very negative, low arousal
            'neutral': (0.0, 0.0)     # neutral
        }
        
        pos1 = emotion_space.get(emotion1, (0, 0))
        pos2 = emotion_space.get(emotion2, (0, 0))
        
        # Euclidean distance in emotion space
        distance = np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        
        # Normalize to 0-1 range
        max_distance = np.sqrt(2 * 1.8**2)  # Maximum possible distance
        return min(1.0, distance / max_distance)
    
    def _analyze_script_context(self, timestamp: float, dialogue_data: List[Dict]) -> Dict:
        """Analyze script context around timestamp."""
        context = {}
        
        # Find dialogue around timestamp
        for dialogue in dialogue_data:
            start_time = dialogue.get('estimated_start_time', 0)
            end_time = dialogue.get('estimated_end_time', start_time + 2)
            
            if start_time <= timestamp <= end_time:
                context.update({
                    'scene_type': dialogue.get('scene_type', 'dialogue'),
                    'current_speaker': dialogue.get('speaker'),
                    'current_emotion': dialogue.get('emotion')
                })
                break
        
        # Check for speaker changes
        prev_speaker = None
        for dialogue in dialogue_data:
            start_time = dialogue.get('estimated_start_time', 0)
            
            if start_time > timestamp:
                if prev_speaker and prev_speaker != dialogue.get('speaker'):
                    context['speaker_change'] = True
                break
            
            prev_speaker = dialogue.get('speaker')
        
        return context
