import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging
import copy

logger = logging.getLogger(__name__)

@dataclass
class CutSuggestion:
    timestamp: float
    confidence: float
    reason: str
    suggestion_type: str  # 'scene_change', 'emotion_beat', 'speaker_change', 'dialogue_pause'
    metadata: Dict = None
    
    def copy(self):
        """Create a copy of this CutSuggestion."""
        return copy.deepcopy(self)
    
    def update(self, updates: Dict):
        """Update fields in this CutSuggestion with values from a dictionary."""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                # If the key doesn't exist as an attribute, add it to metadata
                if self.metadata is None:
                    self.metadata = {}
                self.metadata[key] = value
    
    def get(self, key: str, default=None):
        """Get a field value from this CutSuggestion, supporting both attributes and metadata."""
        if hasattr(self, key):
            return getattr(self, key)
        elif self.metadata is not None and key in self.metadata:
            return self.metadata[key]
        else:
            return default
    
    def __getitem__(self, key: str):
        """Make CutSuggestion subscriptable - support suggestion['key'] syntax."""
        if hasattr(self, key):
            return getattr(self, key)
        elif self.metadata is not None and key in self.metadata:
            return self.metadata[key]
        else:
            raise KeyError(f"'{key}' not found in CutSuggestion")
    
    def __setitem__(self, key: str, value):
        """Make CutSuggestion subscriptable - support suggestion['key'] = value syntax."""
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            # If the key doesn't exist as an attribute, add it to metadata
            if self.metadata is None:
                self.metadata = {}
            self.metadata[key] = value
    
    def __contains__(self, key: str):
        """Support 'key in suggestion' syntax."""
        return hasattr(self, key) or (self.metadata is not None and key in self.metadata)

class CutSuggester:
    """
    Generates intelligent cut suggestions by analyzing multimodal content.
    Combines video, audio, and script analysis to recommend optimal cut points.
    """
    
    def __init__(self, config: dict):
        """
        Initialize CutSuggester with configuration settings.
        
        Args:
            config: Configuration dictionary containing thresholds and weights
        """
        self.config = config
        self.suggestions_config = config.get('suggestions', {})
        
        # Suggestion weights for different types
        self.suggestion_weights = {
            'scene_change': 1.0,
            'emotion_beat': 0.8,
            'speaker_change': 0.7,
            'dialogue_pause': 0.6,
            'audio_silence': 0.5
        }
        
        # Minimum intervals between cuts
        self.min_cut_interval = self.suggestions_config.get('minimum_cut_interval', 2.0)
        self.max_suggestions = self.suggestions_config.get('maximum_suggestions', 100)
    
    def generate_suggestions(self, 
                           video_analysis: Dict,
                           script_analysis: Dict,
                           audio_analysis: Dict) -> List[CutSuggestion]:
        """
        Generate comprehensive cut suggestions from all analysis sources.
        
        Args:
            video_analysis: Results from video processing
            script_analysis: Results from script analysis
            audio_analysis: Results from audio processing
            
        Returns:
            List of cut suggestions sorted by timestamp
        """
        logger.info("Generating cut suggestions from multimodal analysis")
        
        suggestions = []
        
        # Scene change suggestions from video
        if 'scene_changes' in video_analysis:
            suggestions.extend(self._create_scene_change_suggestions(
                video_analysis['scene_changes']
            ))
        
        # Emotional beat suggestions from script
        if 'emotional_beats' in script_analysis:
            suggestions.extend(self._create_emotion_beat_suggestions(
                script_analysis['emotional_beats']
            ))
        
        # Speaker change suggestions from audio
        if 'speaker_changes' in audio_analysis:
            suggestions.extend(self._create_speaker_change_suggestions(
                audio_analysis['speaker_changes']
            ))
        
        # Dialogue-based suggestions
        if 'dialogue_data' in script_analysis:
            suggestions.extend(self._create_dialogue_suggestions(
                script_analysis['dialogue_data']
            ))
        
        # Audio silence suggestions
        if 'energy_timeline' in audio_analysis:
            suggestions.extend(self._create_silence_suggestions(
                audio_analysis['energy_timeline']
            ))
        
        # Process and rank suggestions
        processed_suggestions = self._process_suggestions(suggestions)
        
        logger.info(f"Generated {len(processed_suggestions)} cut suggestions")
        return processed_suggestions
    
    def _create_scene_change_suggestions(self, scene_changes: List) -> List[CutSuggestion]:
        """Create suggestions based on visual scene changes."""
        suggestions = []
        
        for scene_data in scene_changes:
            if isinstance(scene_data, dict):
                timestamp = scene_data.get('timestamp', 0)
                confidence = scene_data.get('confidence', 0.8)
                reason = scene_data.get('reason', 'Visual scene change detected')
            else:
                timestamp = float(scene_data)
                confidence = 0.8
                reason = 'Visual scene change detected'
            
            suggestion = CutSuggestion(
                timestamp=timestamp,
                confidence=confidence,
                reason=reason,
                suggestion_type='scene_change',
                metadata={'method': 'visual_analysis'}
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def _create_emotion_beat_suggestions(self, emotional_beats: List[Dict]) -> List[CutSuggestion]:
        """Create suggestions based on emotional changes in script."""
        suggestions = []
        
        for beat in emotional_beats:
            suggestion = CutSuggestion(
                timestamp=beat.get('timestamp', 0),
                confidence=0.7,
                reason=f"Emotional transition: {beat.get('emotion_from', 'unknown')} → {beat.get('emotion_to', 'unknown')}",
                suggestion_type='emotion_beat',
                metadata={
                    'emotion_from': beat.get('emotion_from'),
                    'emotion_to': beat.get('emotion_to'),
                    'change_magnitude': beat.get('change_magnitude', 0),
                    'speaker': beat.get('speaker')
                }
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def _create_speaker_change_suggestions(self, speaker_changes: List[float]) -> List[CutSuggestion]:
        """Create suggestions based on speaker changes in audio."""
        suggestions = []
        
        for timestamp in speaker_changes:
            if timestamp > 0:  # Skip the initial 0.0 timestamp
                suggestion = CutSuggestion(
                    timestamp=timestamp,
                    confidence=0.6,
                    reason="Potential speaker change detected in audio",
                    suggestion_type='speaker_change',
                    metadata={'method': 'audio_analysis'}
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _create_dialogue_suggestions(self, dialogue_data: List[Dict]) -> List[CutSuggestion]:
        """Create suggestions based on dialogue structure."""
        suggestions = []
        
        for i, dialogue in enumerate(dialogue_data):
            # Suggest cuts at dialogue boundaries with high emotional content
            if dialogue.get('emotion_confidence', 0) > 0.8:
                timestamp = dialogue.get('estimated_start_time', 0)
                
                suggestion = CutSuggestion(
                    timestamp=timestamp,
                    confidence=dialogue['emotion_confidence'] * 0.6,  # Scale down confidence
                    reason=f"High emotional content: {dialogue.get('emotion', 'unknown')}",
                    suggestion_type='dialogue_pause',
                    metadata={
                        'speaker': dialogue.get('speaker'),
                        'emotion': dialogue.get('emotion'),
                        'line_number': dialogue.get('line_number')
                    }
                )
                suggestions.append(suggestion)
            
            # Suggest cuts at long pauses between speakers
            if i > 0:
                prev_end = dialogue_data[i-1].get('estimated_end_time', 0)
                curr_start = dialogue.get('estimated_start_time', 0)
                pause_duration = curr_start - prev_end
                
                if pause_duration > 3.0:  # Long pause
                    suggestion = CutSuggestion(
                        timestamp=prev_end + pause_duration/2,
                        confidence=min(0.5, pause_duration / 10),
                        reason=f"Long pause ({pause_duration:.1f}s) between speakers",
                        suggestion_type='dialogue_pause',
                        metadata={'pause_duration': pause_duration}
                    )
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _create_silence_suggestions(self, energy_timeline: List[Dict]) -> List[CutSuggestion]:
        """Create suggestions based on audio silence/low energy periods."""
        suggestions = []
        
        for i, energy_data in enumerate(energy_timeline):
            db_level = energy_data.get('db_level', 0)
            
            # Very low audio levels might indicate good cut points
            if db_level < -40:  # Very quiet
                timestamp = energy_data.get('start_time', 0)
                
                suggestion = CutSuggestion(
                    timestamp=timestamp,
                    confidence=0.4,
                    reason="Low audio energy detected",
                    suggestion_type='audio_silence',
                    metadata={'db_level': db_level}
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _process_suggestions(self, suggestions: List[CutSuggestion]) -> List[CutSuggestion]:
        """Process, rank, and filter suggestions."""
        if not suggestions:
            return []
        
        # Sort by timestamp
        suggestions.sort(key=lambda x: x.timestamp)
        
        # Filter suggestions that are too close together
        filtered_suggestions = self._filter_close_suggestions(suggestions)
        
        # Apply suggestion type weights
        for suggestion in filtered_suggestions:
            weight = self.suggestion_weights.get(suggestion.suggestion_type, 1.0)
            suggestion.confidence *= weight
        
        # Sort by confidence (highest first) then by timestamp
        filtered_suggestions.sort(key=lambda x: (-x.confidence, x.timestamp))
        
        # Limit to maximum number of suggestions
        if len(filtered_suggestions) > self.max_suggestions:
            filtered_suggestions = filtered_suggestions[:self.max_suggestions]
        
        # Re-sort by timestamp for final output
        filtered_suggestions.sort(key=lambda x: x.timestamp)
        
        return filtered_suggestions
    
    def _filter_close_suggestions(self, suggestions: List[CutSuggestion]) -> List[CutSuggestion]:
        """Remove suggestions that are too close to each other."""
        if not suggestions:
            return []
        
        filtered = [suggestions[0]]
        
        for suggestion in suggestions[1:]:
            # Check distance from last kept suggestion
            time_diff = suggestion.timestamp - filtered[-1].timestamp
            
            if time_diff >= self.min_cut_interval:
                filtered.append(suggestion)
            elif suggestion.confidence > filtered[-1].confidence:
                # Replace with higher confidence suggestion
                filtered[-1] = suggestion
        
        return filtered
    
    def create_custom_suggestions(self, 
                                 timestamps: List[float], 
                                 suggestion_type: str = 'manual',
                                 confidence: float = 1.0) -> List[CutSuggestion]:
        """
        Create custom suggestions from manual timestamps.
        
        Args:
            timestamps: List of timestamps for cuts
            suggestion_type: Type of suggestion
            confidence: Confidence level for suggestions
            
        Returns:
            List of cut suggestions
        """
        suggestions = []
        
        for timestamp in timestamps:
            suggestion = CutSuggestion(
                timestamp=timestamp,
                confidence=confidence,
                reason="Manual cut suggestion",
                suggestion_type=suggestion_type,
                metadata={'source': 'manual'}
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def merge_suggestions(self, *suggestion_lists: List[CutSuggestion]) -> List[CutSuggestion]:
        """
        Merge multiple lists of suggestions.
        
        Args:
            *suggestion_lists: Variable number of suggestion lists
            
        Returns:
            Merged and processed list of suggestions
        """
        all_suggestions = []
        for suggestion_list in suggestion_lists:
            all_suggestions.extend(suggestion_list)
        
        return self._process_suggestions(all_suggestions)
