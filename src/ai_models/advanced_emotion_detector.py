import numpy as np
from typing import Dict, List, Optional, Tuple
from transformers import pipeline
import logging
import cv2
from sklearn.preprocessing import StandardScaler
from scipy.signal import find_peaks
import torch

logger = logging.getLogger(__name__)

class AdvancedEmotionDetector:
    """
    Advanced multi-modal emotion detection with temporal analysis and context awareness.
    Integrates text, speech, visual, and contextual cues for sophisticated emotion understanding.
    """
    
    def __init__(self, config: dict):
        """Initialize advanced emotion detector with multiple AI models."""
        self.config = config
        
        # Initialize models
        self._load_emotion_models()
        
        # Emotion correlation matrix for cross-modal reinforcement
        self.emotion_correlations = {
            'happy': {'joy': 0.9, 'excitement': 0.7, 'positive': 0.8, 'smile': 0.9},
            'sad': {'sadness': 0.9, 'melancholy': 0.8, 'grief': 0.7, 'crying': 0.9},
            'angry': {'anger': 0.9, 'frustration': 0.8, 'rage': 0.7, 'shouting': 0.8},
            'fear': {'anxiety': 0.8, 'worry': 0.7, 'panic': 0.9, 'scared': 0.9},
            'surprise': {'amazement': 0.8, 'shock': 0.7, 'wonder': 0.6, 'gasp': 0.8},
            'neutral': {'calm': 0.7, 'peaceful': 0.6, 'relaxed': 0.5, 'normal': 0.9}
        }
        
        # Context-aware weighting
        self.context_weights = {
            'dialogue_scene': {'text': 0.5, 'speech': 0.4, 'visual': 0.1},
            'action_scene': {'text': 0.2, 'speech': 0.3, 'visual': 0.5},
            'emotional_scene': {'text': 0.3, 'speech': 0.4, 'visual': 0.3},
            'music_scene': {'text': 0.1, 'speech': 0.2, 'visual': 0.7}
        }
        
    def _load_emotion_models(self):
        """Load all emotion detection models."""
        try:
            # Text emotion model (RoBERTa-based)
            self.text_emotion = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
            logger.info("Text emotion model loaded")
        except Exception as e:
            logger.warning(f"Could not load text emotion model: {e}")
            self.text_emotion = None
            
        try:
            # Speech emotion model (Wav2Vec2-based)
            self.speech_emotion = pipeline(
                "audio-classification",
                model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition", 
                return_all_scores=True
            )
            logger.info("Speech emotion model loaded")
        except Exception as e:
            logger.warning(f"Could not load speech emotion model: {e}")
            self.speech_emotion = None
            
        try:
            # Facial emotion model (Vision Transformer)
            self.facial_emotion = pipeline(
                "image-classification",
                model="trpakov/vit-face-expression",
                return_all_scores=True
            )
            logger.info("Facial emotion model loaded")
        except Exception as e:
            logger.warning(f"Could not load facial emotion model: {e}")
            self.facial_emotion = None
    
    def analyze_multi_modal_emotions(self, 
                                   text: Optional[str] = None,
                                   audio_path: Optional[str] = None,
                                   image: Optional[np.ndarray] = None,
                                   context: Optional[Dict] = None) -> Dict:
        """
        Comprehensive multi-modal emotion analysis with context awareness.
        
        Args:
            text: Text content to analyze
            audio_path: Path to audio file
            image: Video frame as numpy array
            context: Scene context (type, lighting, etc.)
            
        Returns:
            Comprehensive emotion analysis with confidence scores
        """
        results = {
            'text_emotions': {},
            'speech_emotions': {},
            'visual_emotions': {},
            'fused_emotions': {},
            'dominant_emotion': 'neutral',
            'confidence': 0.0,
            'temporal_pattern': 'stable',
            'intensity': 'medium'
        }
        
        # Text emotion analysis
        if text and self.text_emotion:
            results['text_emotions'] = self._analyze_text_emotion(text)
        
        # Speech emotion analysis  
        if audio_path and self.speech_emotion:
            results['speech_emotions'] = self._analyze_speech_emotion(audio_path)
            
        # Visual emotion analysis
        if image is not None and self.facial_emotion:
            results['visual_emotions'] = self._analyze_visual_emotion(image)
        
        # Advanced fusion with context awareness
        results['fused_emotions'] = self._advanced_emotion_fusion(
            results['text_emotions'],
            results['speech_emotions'], 
            results['visual_emotions'],
            context
        )
        
        # Determine dominant emotion and metrics
        if results['fused_emotions']:
            dominant = max(results['fused_emotions'].items(), 
                         key=lambda x: x[1] if x[0] != 'confidence' else 0)
            results['dominant_emotion'] = dominant[0]
            results['confidence'] = results['fused_emotions'].get('confidence', 0.5)
            results['intensity'] = self._calculate_intensity(results['fused_emotions'])
        
        return results
    
    def _analyze_text_emotion(self, text: str) -> Dict[str, float]:
        """Advanced text emotion analysis with preprocessing."""
        try:
            # Preprocess text
            text = self._preprocess_text(text)
            
            if len(text.strip()) < 3:
                return {'neutral': 1.0}
            
            # Get predictions
            predictions = self.text_emotion(text)
            
            # Convert to standardized format
            emotions = {}
            for pred in predictions:
                emotion = pred['label'].lower()
                score = pred['score']
                emotions[emotion] = score
            
            return emotions
            
        except Exception as e:
            logger.error(f"Error in text emotion analysis: {e}")
            return {'neutral': 1.0}
    
    def _analyze_speech_emotion(self, audio_path: str) -> Dict[str, float]:
        """Advanced speech emotion analysis with preprocessing."""
        try:
            # Speech emotion analysis
            predictions = self.speech_emotion(audio_path)
            
            emotions = {}
            for pred in predictions:
                emotion = pred['label'].lower()
                score = pred['score']
                emotions[emotion] = score
            
            return emotions
            
        except Exception as e:
            logger.error(f"Error in speech emotion analysis: {e}")
            return {'neutral': 1.0}
    
    def _analyze_visual_emotion(self, image: np.ndarray) -> Dict[str, float]:
        """Advanced visual emotion analysis with face detection."""
        try:
            # Convert numpy array to PIL Image
            from PIL import Image
            if image.dtype == np.float64:
                image = (image * 255).astype(np.uint8)
            
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Detect faces first
            faces = self._detect_faces(image)
            
            if not faces:
                # No faces detected, analyze overall image mood
                return self._analyze_scene_mood(pil_image)
            
            # Analyze emotions for each face
            face_emotions = []
            for face in faces:
                face_img = self._extract_face_region(pil_image, face)
                predictions = self.facial_emotion(face_img)
                
                emotions = {}
                for pred in predictions:
                    emotion = pred['label'].lower()
                    score = pred['score']
                    emotions[emotion] = score
                
                face_emotions.append(emotions)
            
            # Combine emotions from all faces
            combined_emotions = self._combine_face_emotions(face_emotions)
            return combined_emotions
            
        except Exception as e:
            logger.error(f"Error in visual emotion analysis: {e}")
            return {'neutral': 1.0}
    
    def _detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces in image using OpenCV."""
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            return [(x, y, w, h) for (x, y, w, h) in faces]
        except:
            return []
    
    def _extract_face_region(self, image, face_coords):
        """Extract face region from image."""
        x, y, w, h = face_coords
        return image.crop((x, y, x+w, y+h))
    
    def _combine_face_emotions(self, face_emotions: List[Dict[str, float]]) -> Dict[str, float]:
        """Combine emotions from multiple faces."""
        if not face_emotions:
            return {'neutral': 1.0}
        
        combined = {}
        for emotions in face_emotions:
            for emotion, score in emotions.items():
                combined[emotion] = combined.get(emotion, 0) + score
        
        # Average the scores
        face_count = len(face_emotions)
        return {emotion: score/face_count for emotion, score in combined.items()}
    
    def _analyze_scene_mood(self, image) -> Dict[str, float]:
        """Analyze overall scene mood when no faces are detected."""
        # Simplified scene mood analysis
        # In production, this could use more sophisticated visual analysis
        return {
            'neutral': 0.6,
            'calm': 0.3,
            'mysterious': 0.1
        }
    
    def _advanced_emotion_fusion(self, 
                               text_emotions: Dict[str, float],
                               speech_emotions: Dict[str, float],
                               visual_emotions: Dict[str, float],
                               context: Optional[Dict] = None) -> Dict[str, float]:
        """Advanced emotion fusion with context awareness and correlation boosting."""
        
        # Determine context-aware weights
        weights = self._get_context_weights(context)
        
        # Collect all emotions
        all_emotions = set()
        modalities = {'text': text_emotions, 'speech': speech_emotions, 'visual': visual_emotions}
        
        for emotions in modalities.values():
            if emotions:
                all_emotions.update(emotions.keys())
        
        if not all_emotions:
            return {'neutral': 1.0, 'confidence': 0.0}
        
        # Fusion with correlation boosting
        fused_emotions = {}
        for emotion in all_emotions:
            total_weight = 0
            weighted_score = 0
            
            for modality, emotions in modalities.items():
                if emotions and emotion in emotions:
                    base_score = emotions[emotion]
                    
                    # Apply correlation boost from other modalities
                    correlation_boost = self._calculate_correlation_boost(
                        emotion, modalities, modality
                    )
                    
                    final_score = min(1.0, base_score + correlation_boost)
                    weighted_score += final_score * weights[modality]
                    total_weight += weights[modality]
            
            if total_weight > 0:
                fused_emotions[emotion] = weighted_score / total_weight
        
        # Normalize
        total_score = sum(fused_emotions.values())
        if total_score > 0:
            fused_emotions = {k: v/total_score for k, v in fused_emotions.items()}
        
        # Calculate confidence
        confidence = self._calculate_fusion_confidence(text_emotions, speech_emotions, visual_emotions)
        fused_emotions['confidence'] = confidence
        
        return fused_emotions
    
    def _get_context_weights(self, context: Optional[Dict]) -> Dict[str, float]:
        """Get context-aware modality weights."""
        default_weights = {'text': 0.4, 'speech': 0.4, 'visual': 0.2}
        
        if not context:
            return default_weights
        
        scene_type = context.get('scene_type', '').lower()
        
        for context_key, weights in self.context_weights.items():
            if context_key.replace('_scene', '') in scene_type:
                return weights
        
        return default_weights
    
    def _calculate_correlation_boost(self, target_emotion: str, modalities: Dict, exclude_modality: str) -> float:
        """Calculate correlation boost from other modalities."""
        boost = 0.0
        correlations = self.emotion_correlations.get(target_emotion, {})
        
        for modality, emotions in modalities.items():
            if modality != exclude_modality and emotions:
                for emotion, score in emotions.items():
                    if emotion in correlations:
                        boost += score * correlations[emotion] * 0.1
        
        return min(0.2, boost)  # Cap boost at 0.2
    
    def _calculate_fusion_confidence(self, text_emotions, speech_emotions, visual_emotions) -> float:
        """Calculate confidence based on cross-modal agreement."""
        available_modalities = [x for x in [text_emotions, speech_emotions, visual_emotions] if x]
        
        if len(available_modalities) < 2:
            return 0.5
        
        # Calculate agreement between modalities
        agreements = []
        for i in range(len(available_modalities)):
            for j in range(i+1, len(available_modalities)):
                agreement = self._calculate_agreement(available_modalities[i], available_modalities[j])
                agreements.append(agreement)
        
        avg_agreement = sum(agreements) / len(agreements) if agreements else 0.5
        return min(1.0, avg_agreement + 0.3)
    
    def _calculate_agreement(self, emotions1: Dict, emotions2: Dict) -> float:
        """Calculate agreement between two emotion distributions."""
        common_emotions = set(emotions1.keys()) & set(emotions2.keys())
        
        if not common_emotions:
            return 0.0
        
        agreement = 0.0
        for emotion in common_emotions:
            # Calculate similarity between scores
            diff = abs(emotions1[emotion] - emotions2[emotion])
            agreement += 1.0 - diff
        
        return agreement / len(common_emotions)
    
    def _calculate_intensity(self, emotions: Dict[str, float]) -> str:
        """Calculate emotional intensity."""
        max_score = max(v for k, v in emotions.items() if k != 'confidence')
        
        if max_score > 0.8:
            return 'very_high'
        elif max_score > 0.6:
            return 'high'
        elif max_score > 0.4:
            return 'medium'
        elif max_score > 0.2:
            return 'low'
        else:
            return 'very_low'
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better emotion analysis."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Handle special characters that might affect analysis
        text = text.replace('...', '.')
        text = text.replace('!!!', '!')
        text = text.replace('???', '?')
        
        return text
    
    def analyze_temporal_emotions(self, emotion_timeline: List[Dict]) -> Dict:
        """Analyze emotional patterns over time."""
        if not emotion_timeline:
            return {'pattern': 'stable', 'peaks': [], 'transitions': []}
        
        # Extract dominant emotions over time
        emotions_over_time = []
        timestamps = []
        
        for entry in emotion_timeline:
            emotions_over_time.append(entry.get('dominant_emotion', 'neutral'))
            timestamps.append(entry.get('timestamp', 0))
        
        # Detect emotional peaks and transitions
        peaks = self._detect_emotional_peaks(emotion_timeline)
        transitions = self._detect_emotional_transitions(emotion_timeline)
        pattern = self._classify_emotional_pattern(emotions_over_time)
        
        return {
            'pattern': pattern,
            'peaks': peaks,
            'transitions': transitions,
            'stability': self._calculate_emotional_stability(emotions_over_time),
            'intensity_trend': self._analyze_intensity_trend(emotion_timeline)
        }
    
    def _detect_emotional_peaks(self, timeline: List[Dict]) -> List[Dict]:
        """Detect emotional intensity peaks."""
        if len(timeline) < 3:
            return []
        
        intensities = []
        for entry in timeline:
            emotions = entry.get('fused_emotions', {})
            max_intensity = max(v for k, v in emotions.items() if k != 'confidence') if emotions else 0
            intensities.append(max_intensity)
        
        # Find peaks using scipy
        peaks, _ = find_peaks(intensities, height=0.6, distance=3)
        
        peak_data = []
        for peak_idx in peaks:
            peak_data.append({
                'timestamp': timeline[peak_idx].get('timestamp', 0),
                'emotion': timeline[peak_idx].get('dominant_emotion', 'neutral'),
                'intensity': intensities[peak_idx]
            })
        
        return peak_data
    
    def _detect_emotional_transitions(self, timeline: List[Dict]) -> List[Dict]:
        """Detect significant emotional transitions."""
        if len(timeline) < 2:
            return []
        
        transitions = []
        for i in range(1, len(timeline)):
            prev_emotion = timeline[i-1].get('dominant_emotion', 'neutral')
            curr_emotion = timeline[i].get('dominant_emotion', 'neutral')
            
            if prev_emotion != curr_emotion:
                transition_intensity = self._calculate_transition_intensity(
                    timeline[i-1].get('fused_emotions', {}),
                    timeline[i].get('fused_emotions', {})
                )
                
                if transition_intensity > 0.3:  # Significant transition
                    transitions.append({
                        'timestamp': timeline[i].get('timestamp', 0),
                        'from_emotion': prev_emotion,
                        'to_emotion': curr_emotion,
                        'intensity': transition_intensity
                    })
        
        return transitions
    
    def _calculate_transition_intensity(self, emotions1: Dict, emotions2: Dict) -> float:
        """Calculate intensity of emotional transition."""
        if not emotions1 or not emotions2:
            return 0.0
        
        # Calculate distance between emotion distributions
        common_emotions = set(emotions1.keys()) & set(emotions2.keys())
        distance = 0.0
        
        for emotion in common_emotions:
            if emotion != 'confidence':
                distance += abs(emotions1[emotion] - emotions2[emotion])
        
        return min(1.0, distance / len(common_emotions)) if common_emotions else 0.0
    
    def _classify_emotional_pattern(self, emotions: List[str]) -> str:
        """Classify overall emotional pattern."""
        if not emotions:
            return 'stable'
        
        unique_emotions = len(set(emotions))
        total_emotions = len(emotions)
        
        if unique_emotions == 1:
            return 'stable'
        elif unique_emotions / total_emotions > 0.7:
            return 'volatile'
        elif unique_emotions / total_emotions > 0.4:
            return 'dynamic'
        else:
            return 'evolving'
    
    def _calculate_emotional_stability(self, emotions: List[str]) -> float:
        """Calculate emotional stability score."""
        if not emotions:
            return 1.0
        
        changes = sum(1 for i in range(1, len(emotions)) if emotions[i] != emotions[i-1])
        return max(0.0, 1.0 - (changes / len(emotions)))
    
    def _analyze_intensity_trend(self, timeline: List[Dict]) -> str:
        """Analyze trend in emotional intensity."""
        if len(timeline) < 3:
            return 'stable'
        
        intensities = []
        for entry in timeline:
            emotions = entry.get('fused_emotions', {})
            max_intensity = max(v for k, v in emotions.items() if k != 'confidence') if emotions else 0
            intensities.append(max_intensity)
        
        # Calculate trend
        x = np.arange(len(intensities))
        slope = np.polyfit(x, intensities, 1)[0]
        
        if slope > 0.05:
            return 'increasing'
        elif slope < -0.05:
            return 'decreasing'
        else:
            return 'stable'
