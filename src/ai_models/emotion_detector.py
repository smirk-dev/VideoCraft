import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from src.utils.offline_models import OfflineModelManager

logger = logging.getLogger(__name__)

class EmotionDetector:
    """
    Multi-modal emotion detection combining text, speech, and visual cues.
    Integrates multiple emotion analysis models for comprehensive emotional understanding.
    Uses offline fallbacks when models are unavailable.
    """
    
    def __init__(self, config: dict):
        """
        Initialize EmotionDetector with multiple emotion analysis models.
        
        Args:
            config: Configuration dictionary containing model settings
        """
        self.config = config
        
        # Initialize offline model manager
        self.offline_manager = OfflineModelManager(config)
        
        # Try to load text emotion model
        try:
            from transformers import pipeline
            self.text_emotion = pipeline(
                "text-classification",
                model=config['models']['emotion_text'],
                return_all_scores=True
            )
            logger.info("Text emotion model loaded successfully")
            self.use_text_model = True
        except Exception as e:
            logger.warning(f"Could not load text emotion model: {e}")
            self.text_emotion = None
            self.use_text_model = False
        
        # Try to load speech emotion model
        try:
            from transformers import pipeline
            self.speech_emotion = pipeline(
                "audio-classification", 
                model=config['models']['emotion_speech'],
                return_all_scores=True
            )
            logger.info("Speech emotion model loaded successfully")
            self.use_speech_model = True
        except Exception as e:
            logger.warning(f"Could not load speech emotion model: {e}")
            self.speech_emotion = None
            self.use_speech_model = False
        
        # Get offline emotion detector
        if not self.use_text_model or not self.use_speech_model:
            self.offline_emotion_detector = self.offline_manager.get_model('emotion')
        
        # Emotion mapping for consistency across models
        self.emotion_mapping = {
            'joy': 'happy',
            'happiness': 'happy', 
            'sadness': 'sad',
            'anger': 'angry',
            'fear': 'fearful',
            'surprise': 'surprised',
            'disgust': 'disgusted',
            'neutral': 'neutral'
        }
        
        # Emotion weights for fusion
        self.modality_weights = {
            'text': 0.4,
            'speech': 0.4,
            'visual': 0.2
        }
    
    def detect_text_emotion(self, text: str) -> Dict[str, float]:
        """
        Detect emotion from text content using online models or offline fallback.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping emotions to confidence scores
        """
        if not text.strip():
            return {'neutral': 1.0}
        
        try:
            if self.use_text_model and self.text_emotion:
                # Use online model
                results = self.text_emotion(text)
                
                if isinstance(results[0], list):
                    results = results[0]
                
                # Normalize emotion labels and scores
                emotions = {}
                for result in results:
                    emotion = result['label'].lower()
                    emotion = self.emotion_mapping.get(emotion, emotion)
                    emotions[emotion] = result['score']
                
                return emotions
            else:
                # Use offline fallback
                return self.offline_emotion_detector.analyze_text(text)
                
        except Exception as e:
            logger.error(f"Error in text emotion detection: {e}")
            # Fallback to offline analysis
            try:
                return self.offline_emotion_detector.analyze_text(text)
            except:
                return {'neutral': 1.0}
    
    def detect_speech_emotion(self, audio_path: str) -> Dict[str, float]:
        """
        Detect emotion from speech audio using online models or offline fallback.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary mapping emotions to confidence scores
        """
        try:
            if self.use_speech_model and self.speech_emotion:
                # Use online model
                results = self.speech_emotion(audio_path)
                
                if isinstance(results[0], list):
                    results = results[0]
                
                # Normalize emotion labels and scores
                emotions = {}
                for result in results:
                    emotion = result['label'].lower()
                    emotion = self.emotion_mapping.get(emotion, emotion)
                    emotions[emotion] = result['score']
                
                return emotions
            else:
                # Use offline fallback - analyze basic audio features
                return self._analyze_audio_offline(audio_path)
                
        except Exception as e:
            logger.error(f"Error in speech emotion detection: {e}")
            return {'neutral': 1.0}
    
    def _analyze_audio_offline(self, audio_path: str) -> Dict[str, float]:
        """Analyze audio for emotion using basic features."""
        try:
            # This would require librosa or similar, but for basic fallback:
            # We'll return based on simple heuristics
            import os
            file_size = os.path.getsize(audio_path)
            
            # Very basic heuristic based on file size and duration
            if file_size > 1000000:  # Large file might indicate energetic content
                return {'happy': 0.6, 'neutral': 0.4}
            else:
                return {'neutral': 0.8, 'sad': 0.2}
                
        except Exception as e:
            logger.warning(f"Offline audio analysis failed: {e}")
            return {'neutral': 1.0}
            
            # Normalize emotion labels and scores
            emotions = {}
            for result in results:
                emotion = result['label'].lower()
                emotion = self.emotion_mapping.get(emotion, emotion)
                emotions[emotion] = result['score']
            
            return emotions
            
        except Exception as e:
            logger.error(f"Error in speech emotion detection: {e}")
            return {'neutral': 1.0}
    
    def fuse_emotions(self, 
                     text_emotions: Optional[Dict[str, float]] = None,
                     speech_emotions: Optional[Dict[str, float]] = None,
                     visual_emotions: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Fuse emotions from multiple modalities using weighted combination.
        
        Args:
            text_emotions: Text-based emotion scores
            speech_emotions: Speech-based emotion scores  
            visual_emotions: Visual-based emotion scores
            
        Returns:
            Fused emotion scores
        """
        # Collect available emotions
        all_emotions = set()
        modalities = {}
        
        if text_emotions:
            all_emotions.update(text_emotions.keys())
            modalities['text'] = text_emotions
        
        if speech_emotions:
            all_emotions.update(speech_emotions.keys())
            modalities['speech'] = speech_emotions
            
        if visual_emotions:
            all_emotions.update(visual_emotions.keys())
            modalities['visual'] = visual_emotions
        
        if not modalities:
            return {'neutral': 1.0}
        
        # Fuse emotions using weighted combination
        fused_emotions = {}
        total_weight = sum(self.modality_weights[mod] for mod in modalities.keys())
        
        for emotion in all_emotions:
            weighted_score = 0.0
            
            for modality, emotions in modalities.items():
                score = emotions.get(emotion, 0.0)
                weight = self.modality_weights[modality]
                weighted_score += score * weight
            
            fused_emotions[emotion] = weighted_score / total_weight
        
        # Normalize scores to sum to 1
        total_score = sum(fused_emotions.values())
        if total_score > 0:
            fused_emotions = {k: v/total_score for k, v in fused_emotions.items()}
        
        return fused_emotions
    
    def analyze_emotional_trajectory(self, emotion_timeline: List[Dict]) -> Dict:
        """
        Analyze emotional trajectory over time to identify patterns and peaks.
        
        Args:
            emotion_timeline: List of emotion analysis results with timestamps
            
        Returns:
            Emotional trajectory analysis
        """
        if not emotion_timeline:
            return {}
        
        # Extract emotion sequences
        timestamps = [item.get('timestamp', 0) for item in emotion_timeline]
        dominant_emotions = [item.get('emotion', 'neutral') for item in emotion_timeline]
        
        # Analyze emotional patterns
        analysis = {
            'duration': max(timestamps) - min(timestamps) if len(timestamps) > 1 else 0,
            'emotion_changes': self._count_emotion_changes(dominant_emotions),
            'dominant_emotion': self._find_dominant_emotion(emotion_timeline),
            'emotional_intensity': self._calculate_emotional_intensity(emotion_timeline),
            'emotional_peaks': self._find_emotional_peaks(emotion_timeline),
            'emotional_stability': self._calculate_emotional_stability(emotion_timeline)
        }
        
        return analysis
    
    def detect_emotional_transitions(self, 
                                   emotion_timeline: List[Dict],
                                   threshold: float = 0.3) -> List[Dict]:
        """
        Detect significant emotional transitions in timeline.
        
        Args:
            emotion_timeline: Timeline of emotion analysis
            threshold: Minimum change threshold for transition detection
            
        Returns:
            List of emotional transition points
        """
        transitions = []
        
        for i in range(1, len(emotion_timeline)):
            prev_emotions = emotion_timeline[i-1].get('all_emotions', {})
            curr_emotions = emotion_timeline[i].get('all_emotions', {})
            
            # Calculate emotional distance
            distance = self._calculate_emotional_distance(prev_emotions, curr_emotions)
            
            if distance > threshold:
                transition = {
                    'timestamp': emotion_timeline[i].get('timestamp', 0),
                    'from_emotion': emotion_timeline[i-1].get('emotion', 'neutral'),
                    'to_emotion': emotion_timeline[i].get('emotion', 'neutral'),
                    'intensity': distance,
                    'type': self._classify_transition_type(
                        emotion_timeline[i-1].get('emotion', 'neutral'),
                        emotion_timeline[i].get('emotion', 'neutral')
                    )
                }
                transitions.append(transition)
        
        return transitions
    
    def _count_emotion_changes(self, emotions: List[str]) -> int:
        """Count number of emotion changes in sequence."""
        if len(emotions) < 2:
            return 0
        
        changes = 0
        for i in range(1, len(emotions)):
            if emotions[i] != emotions[i-1]:
                changes += 1
        
        return changes
    
    def _find_dominant_emotion(self, emotion_timeline: List[Dict]) -> str:
        """Find the most frequent emotion in timeline."""
        emotion_counts = {}
        
        for item in emotion_timeline:
            emotion = item.get('emotion', 'neutral')
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        return max(emotion_counts, key=emotion_counts.get) if emotion_counts else 'neutral'
    
    def _calculate_emotional_intensity(self, emotion_timeline: List[Dict]) -> float:
        """Calculate average emotional intensity."""
        intensities = []
        
        for item in emotion_timeline:
            confidence = item.get('emotion_confidence', 0.5)
            emotion = item.get('emotion', 'neutral')
            
            # Weight intensity by emotion type (neutral is low intensity)
            emotion_weights = {
                'happy': 1.0, 'sad': 1.0, 'angry': 1.2, 
                'fearful': 1.1, 'surprised': 0.9, 'neutral': 0.3
            }
            
            weight = emotion_weights.get(emotion, 0.5)
            intensities.append(confidence * weight)
        
        return np.mean(intensities) if intensities else 0.0
    
    def _find_emotional_peaks(self, emotion_timeline: List[Dict]) -> List[Dict]:
        """Find emotional peaks (high intensity moments)."""
        peaks = []
        
        for i, item in enumerate(emotion_timeline):
            confidence = item.get('emotion_confidence', 0.5)
            
            # Check if this is a local maximum
            is_peak = True
            window = 2  # Check 2 items on each side
            
            for j in range(max(0, i-window), min(len(emotion_timeline), i+window+1)):
                if j != i:
                    other_confidence = emotion_timeline[j].get('emotion_confidence', 0.5)
                    if other_confidence >= confidence:
                        is_peak = False
                        break
            
            if is_peak and confidence > 0.7:  # Only consider high-confidence peaks
                peaks.append({
                    'timestamp': item.get('timestamp', 0),
                    'emotion': item.get('emotion', 'neutral'),
                    'intensity': confidence
                })
        
        return peaks
    
    def _calculate_emotional_stability(self, emotion_timeline: List[Dict]) -> float:
        """Calculate emotional stability (inverse of variance)."""
        confidences = [item.get('emotion_confidence', 0.5) for item in emotion_timeline]
        
        if len(confidences) < 2:
            return 1.0
        
        variance = np.var(confidences)
        stability = 1.0 / (1.0 + variance)  # Inverse relationship
        
        return stability
    
    def _calculate_emotional_distance(self, emotions1: Dict[str, float], emotions2: Dict[str, float]) -> float:
        """Calculate distance between two emotion distributions."""
        all_emotions = set(emotions1.keys()) | set(emotions2.keys())
        
        if not all_emotions:
            return 0.0
        
        distance = 0.0
        for emotion in all_emotions:
            val1 = emotions1.get(emotion, 0.0)
            val2 = emotions2.get(emotion, 0.0)
            distance += abs(val1 - val2)
        
        return distance / len(all_emotions)
    
    def _classify_transition_type(self, from_emotion: str, to_emotion: str) -> str:
        """Classify the type of emotional transition."""
        # Define emotion valence (positive/negative)
        positive_emotions = {'happy', 'surprised', 'neutral'}
        negative_emotions = {'sad', 'angry', 'fearful', 'disgusted'}
        
        from_valence = 'positive' if from_emotion in positive_emotions else 'negative'
        to_valence = 'positive' if to_emotion in positive_emotions else 'negative'
        
        if from_valence == to_valence:
            return 'same_valence'
        elif from_valence == 'positive' and to_valence == 'negative':
            return 'positive_to_negative'
        else:
            return 'negative_to_positive'
