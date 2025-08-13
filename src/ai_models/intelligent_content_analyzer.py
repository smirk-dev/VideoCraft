import torch
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
from transformers import pipeline, AutoModel, AutoTokenizer
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ContentType(Enum):
    INTERVIEW = "interview"
    VLOG = "vlog"
    TUTORIAL = "tutorial"
    MUSIC_VIDEO = "music_video"
    DOCUMENTARY = "documentary"
    PRESENTATION = "presentation"
    GAMING = "gaming"
    NEWS = "news"
    SPORTS = "sports"
    COMMERCIAL = "commercial"

@dataclass
class ContentContext:
    type: ContentType
    confidence: float
    key_elements: List[str]
    suggested_style: str
    pacing: str  # fast, medium, slow
    target_audience: str

class IntelligentContentAnalyzer:
    """
    Advanced content understanding that adapts editing suggestions based on
    video type, audience, and content purpose.
    """
    
    def __init__(self, config: dict):
        self.config = config
        
        # Load advanced models
        self._load_models()
        
        # Content-specific editing rules
        self.editing_rules = {
            ContentType.INTERVIEW: {
                'cut_frequency': 'medium',
                'preferred_transitions': ['cut', 'fade'],
                'focus_on': ['speaker_changes', 'emotional_beats'],
                'avoid': ['fast_cuts', 'dramatic_transitions']
            },
            ContentType.VLOG: {
                'cut_frequency': 'high',
                'preferred_transitions': ['cut', 'jump_cut'],
                'focus_on': ['energy_changes', 'topic_shifts'],
                'keep_engagement': True
            },
            ContentType.TUTORIAL: {
                'cut_frequency': 'low',
                'preferred_transitions': ['cut', 'fade'],
                'focus_on': ['step_completion', 'demonstration_points'],
                'maintain_clarity': True
            },
            ContentType.MUSIC_VIDEO: {
                'cut_frequency': 'very_high',
                'preferred_transitions': ['cut', 'beat_sync'],
                'focus_on': ['beat_detection', 'visual_rhythm'],
                'sync_to_music': True
            }
        }
    
    def _load_models(self):
        """Load content analysis models."""
        try:
            # Video content classifier
            self.content_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            
            # Object detection for content understanding
            self.object_detector = pipeline(
                "object-detection",
                model="facebook/detr-resnet-50"
            )
            
            # Text analysis for content type
            self.text_analyzer = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium"
            )
            
            logger.info("Content analysis models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load content models: {e}")
            self.content_classifier = None
            self.object_detector = None
            self.text_analyzer = None
    
    def analyze_content_type(self, 
                           video_path: str,
                           script_text: Optional[str] = None,
                           metadata: Optional[Dict] = None) -> ContentContext:
        """
        Analyze video content to determine type and context.
        
        Args:
            video_path: Path to video file
            script_text: Optional script/subtitle text
            metadata: Optional video metadata
            
        Returns:
            ContentContext with detected type and suggestions
        """
        
        # Multi-modal content analysis
        visual_indicators = self._analyze_visual_content(video_path)
        audio_indicators = self._analyze_audio_patterns(video_path)
        text_indicators = self._analyze_text_content(script_text) if script_text else {}
        
        # Classify content type
        content_type = self._classify_content_type(
            visual_indicators, audio_indicators, text_indicators, metadata
        )
        
        # Generate context
        context = ContentContext(
            type=content_type['type'],
            confidence=content_type['confidence'],
            key_elements=content_type['elements'],
            suggested_style=self._suggest_editing_style(content_type['type']),
            pacing=self._determine_pacing(visual_indicators, audio_indicators),
            target_audience=self._infer_target_audience(content_type['type'], text_indicators)
        )
        
        return context
    
    def _analyze_visual_content(self, video_path: str) -> Dict:
        """Analyze visual patterns to understand content type."""
        indicators = {
            'face_frequency': 0,
            'object_diversity': 0,
            'scene_complexity': 0,
            'motion_level': 0,
            'visual_style': 'professional'
        }
        
        try:
            cap = cv2.VideoCapture(video_path)
            frame_count = 0
            faces_detected = 0
            unique_objects = set()
            
            # Sample frames for analysis
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, total_frames // 20)  # Sample 20 frames
            
            for i in range(0, total_frames, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Face detection
                faces = self._detect_faces_cv(frame)
                faces_detected += len(faces)
                
                # Object detection
                if self.object_detector and frame_count % 5 == 0:  # Every 5th frame
                    objects = self._detect_objects(frame)
                    for obj in objects:
                        unique_objects.add(obj['label'])
                
                # Motion analysis
                if frame_count > 1:
                    motion = self._calculate_motion(frame, prev_frame)
                    indicators['motion_level'] += motion
                
                prev_frame = frame.copy()
            
            cap.release()
            
            # Calculate indicators
            if frame_count > 0:
                indicators['face_frequency'] = faces_detected / frame_count
                indicators['object_diversity'] = len(unique_objects)
                indicators['motion_level'] /= frame_count
                
        except Exception as e:
            logger.error(f"Visual analysis failed: {e}")
        
        return indicators
    
    def _analyze_audio_patterns(self, video_path: str) -> Dict:
        """Analyze audio patterns for content classification."""
        indicators = {
            'speech_ratio': 0,
            'music_presence': False,
            'audio_quality': 'medium',
            'speaker_count': 1,
            'background_noise': 'low'
        }
        
        try:
            import librosa
            
            # Extract audio
            y, sr = librosa.load(video_path, duration=60)  # Analyze first minute
            
            # Speech detection
            speech_segments = self._detect_speech_segments(y, sr)
            indicators['speech_ratio'] = sum(seg[1] - seg[0] for seg in speech_segments) / len(y) * sr
            
            # Music detection
            indicators['music_presence'] = self._detect_music(y, sr)
            
            # Audio quality assessment
            indicators['audio_quality'] = self._assess_audio_quality(y, sr)
            
            # Speaker count estimation
            indicators['speaker_count'] = self._estimate_speaker_count(y, sr)
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
        
        return indicators
    
    def _analyze_text_content(self, text: str) -> Dict:
        """Analyze text content for classification clues."""
        indicators = {
            'formality': 'medium',
            'technical_level': 'medium',
            'emotional_tone': 'neutral',
            'instruction_words': 0,
            'question_ratio': 0
        }
        
        if not text or not self.text_analyzer:
            return indicators
        
        try:
            # Analyze formality and style
            sentences = text.split('.')
            question_count = text.count('?')
            instruction_words = ['step', 'first', 'next', 'then', 'finally', 'how to', 'tutorial']
            
            indicators['question_ratio'] = question_count / len(sentences) if sentences else 0
            indicators['instruction_words'] = sum(1 for word in instruction_words if word.lower() in text.lower())
            
            # Classify emotional tone
            if len(text) > 50:
                tone_result = self.content_classifier(
                    text[:500],  # First 500 chars
                    candidate_labels=['positive', 'negative', 'neutral', 'educational', 'entertaining']
                )
                indicators['emotional_tone'] = tone_result['labels'][0]
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
        
        return indicators
    
    def _classify_content_type(self, visual: Dict, audio: Dict, text: Dict, metadata: Optional[Dict]) -> Dict:
        """Classify content type based on all indicators."""
        
        scores = {content_type: 0 for content_type in ContentType}
        
        # Visual indicators
        if visual['face_frequency'] > 0.5:
            scores[ContentType.INTERVIEW] += 3
            scores[ContentType.VLOG] += 2
            scores[ContentType.NEWS] += 2
        
        if visual['object_diversity'] > 10:
            scores[ContentType.TUTORIAL] += 2
            scores[ContentType.DOCUMENTARY] += 2
        
        if visual['motion_level'] > 0.7:
            scores[ContentType.MUSIC_VIDEO] += 3
            scores[ContentType.SPORTS] += 2
            scores[ContentType.GAMING] += 2
        
        # Audio indicators
        if audio['speech_ratio'] > 0.8:
            scores[ContentType.INTERVIEW] += 3
            scores[ContentType.PRESENTATION] += 2
            scores[ContentType.NEWS] += 2
        
        if audio['music_presence']:
            scores[ContentType.MUSIC_VIDEO] += 3
            scores[ContentType.COMMERCIAL] += 1
        
        if audio['speaker_count'] > 1:
            scores[ContentType.INTERVIEW] += 2
            scores[ContentType.DOCUMENTARY] += 1
        
        # Text indicators
        if text['instruction_words'] > 3:
            scores[ContentType.TUTORIAL] += 4
            scores[ContentType.PRESENTATION] += 2
        
        if text['question_ratio'] > 0.2:
            scores[ContentType.INTERVIEW] += 2
            scores[ContentType.VLOG] += 1
        
        # Determine best match
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type] / max(sum(scores.values()), 1)
        
        # Extract key elements
        elements = self._extract_key_elements(visual, audio, text, best_type)
        
        return {
            'type': best_type,
            'confidence': confidence,
            'elements': elements,
            'scores': scores
        }
    
    def _suggest_editing_style(self, content_type: ContentType) -> str:
        """Suggest editing style based on content type."""
        style_map = {
            ContentType.INTERVIEW: "conversational",
            ContentType.VLOG: "dynamic",
            ContentType.TUTORIAL: "clear_and_methodical",
            ContentType.MUSIC_VIDEO: "rhythmic",
            ContentType.DOCUMENTARY: "cinematic",
            ContentType.PRESENTATION: "professional",
            ContentType.GAMING: "energetic",
            ContentType.NEWS: "authoritative",
            ContentType.SPORTS: "exciting",
            ContentType.COMMERCIAL: "persuasive"
        }
        return style_map.get(content_type, "balanced")
    
    def _determine_pacing(self, visual: Dict, audio: Dict) -> str:
        """Determine appropriate pacing for content."""
        motion_score = visual.get('motion_level', 0)
        speech_ratio = audio.get('speech_ratio', 0)
        
        if motion_score > 0.7 and speech_ratio < 0.5:
            return "fast"
        elif motion_score < 0.3 and speech_ratio > 0.7:
            return "slow"
        else:
            return "medium"
    
    def _infer_target_audience(self, content_type: ContentType, text: Dict) -> str:
        """Infer target audience based on content analysis."""
        if content_type in [ContentType.TUTORIAL, ContentType.PRESENTATION]:
            return "educational"
        elif content_type in [ContentType.VLOG, ContentType.GAMING]:
            return "entertainment"
        elif content_type in [ContentType.NEWS, ContentType.DOCUMENTARY]:
            return "informational"
        elif content_type == ContentType.COMMERCIAL:
            return "consumer"
        else:
            return "general"
    
    def generate_adaptive_suggestions(self, 
                                    content_context: ContentContext,
                                    base_suggestions: List[Dict]) -> List[Dict]:
        """
        Adapt editing suggestions based on content context.
        
        Args:
            content_context: Analyzed content context
            base_suggestions: Original AI suggestions
            
        Returns:
            Adapted suggestions optimized for content type
        """
        
        rules = self.editing_rules.get(content_context.type, {})
        adapted_suggestions = []
        
        for suggestion in base_suggestions:
            adapted = suggestion.copy()
            
            # Adjust confidence based on content relevance
            relevance_boost = self._calculate_relevance_boost(suggestion, content_context)
            adapted['confidence'] = min(1.0, suggestion['confidence'] + relevance_boost)
            
            # Modify suggestion based on content rules
            if rules.get('cut_frequency') == 'low' and suggestion['confidence'] < 0.8:
                adapted['confidence'] *= 0.7  # Reduce less confident cuts
            
            elif rules.get('cut_frequency') == 'high':
                adapted['confidence'] = min(1.0, suggestion['confidence'] * 1.2)  # Boost cuts
            
            # Add content-specific metadata
            adapted['content_context'] = {
                'type': content_context.type.value,
                'suggested_style': content_context.suggested_style,
                'relevance': relevance_boost
            }
            
            adapted_suggestions.append(adapted)
        
        # Sort by adapted confidence
        adapted_suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return adapted_suggestions
    
    def _calculate_relevance_boost(self, suggestion: Dict, context: ContentContext) -> float:
        """Calculate how much to boost suggestion confidence based on content context."""
        boost = 0.0
        
        # Type-specific boosts
        if context.type == ContentType.INTERVIEW:
            if 'speaker_change' in suggestion.get('reason', ''):
                boost += 0.2
            if 'emotional_beat' in suggestion.get('reason', ''):
                boost += 0.15
        
        elif context.type == ContentType.TUTORIAL:
            if 'step_completion' in suggestion.get('reason', ''):
                boost += 0.25
            if 'demonstration' in suggestion.get('reason', ''):
                boost += 0.2
        
        elif context.type == ContentType.MUSIC_VIDEO:
            if 'beat_sync' in suggestion.get('reason', ''):
                boost += 0.3
            if 'rhythm' in suggestion.get('reason', ''):
                boost += 0.25
        
        return min(0.3, boost)  # Cap boost at 0.3
    
    def _detect_faces_cv(self, frame: np.ndarray) -> List:
        """Simple face detection using OpenCV."""
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            return faces
        except:
            return []
    
    def _detect_objects(self, frame: np.ndarray) -> List[Dict]:
        """Detect objects in frame."""
        if not self.object_detector:
            return []
        
        try:
            from PIL import Image
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            results = self.object_detector(pil_image)
            return results
        except:
            return []
    
    def _calculate_motion(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Calculate motion between two frames."""
        try:
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowPyrLK(gray1, gray2, None, None)
            magnitude = np.mean(np.sqrt(flow[0][:, :, 0]**2 + flow[0][:, :, 1]**2)) if flow[0] is not None else 0
            
            return min(1.0, magnitude / 100)  # Normalize
        except:
            return 0.0
    
    def _detect_speech_segments(self, audio: np.ndarray, sr: int) -> List[Tuple[int, int]]:
        """Detect speech segments in audio."""
        # Simplified speech detection - in production use VAD
        try:
            import librosa
            
            # Use energy-based detection
            hop_length = 512
            energy = librosa.feature.rms(y=audio, hop_length=hop_length)[0]
            threshold = np.mean(energy) * 0.5
            
            speech_frames = energy > threshold
            segments = []
            
            start = None
            for i, is_speech in enumerate(speech_frames):
                if is_speech and start is None:
                    start = i
                elif not is_speech and start is not None:
                    segments.append((start * hop_length, i * hop_length))
                    start = None
            
            return segments
        except:
            return []
    
    def _detect_music(self, audio: np.ndarray, sr: int) -> bool:
        """Detect presence of music in audio."""
        try:
            import librosa
            
            # Use spectral features to detect music
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
            
            # Simple heuristic - music typically has consistent tempo and higher spectral centroid
            return tempo > 60 and spectral_centroid > 1000
        except:
            return False
    
    def _assess_audio_quality(self, audio: np.ndarray, sr: int) -> str:
        """Assess audio quality."""
        try:
            # Simple quality assessment based on signal-to-noise ratio
            signal_power = np.mean(audio ** 2)
            
            if signal_power > 0.1:
                return "high"
            elif signal_power > 0.01:
                return "medium"
            else:
                return "low"
        except:
            return "medium"
    
    def _estimate_speaker_count(self, audio: np.ndarray, sr: int) -> int:
        """Estimate number of speakers."""
        # Simplified speaker counting - in production use speaker diarization
        try:
            import librosa
            
            # Use MFCC clustering as proxy
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            
            # Simple heuristic based on MFCC variance
            variance = np.var(mfccs, axis=1)
            avg_variance = np.mean(variance)
            
            if avg_variance > 10:
                return 3  # Multiple speakers
            elif avg_variance > 5:
                return 2  # Two speakers
            else:
                return 1  # Single speaker
        except:
            return 1
    
    def _extract_key_elements(self, visual: Dict, audio: Dict, text: Dict, content_type: ContentType) -> List[str]:
        """Extract key elements for the detected content type."""
        elements = []
        
        if visual['face_frequency'] > 0.3:
            elements.append("talking_heads")
        
        if visual['motion_level'] > 0.5:
            elements.append("dynamic_visuals")
        
        if audio['music_presence']:
            elements.append("background_music")
        
        if audio['speech_ratio'] > 0.7:
            elements.append("speech_heavy")
        
        if text['instruction_words'] > 2:
            elements.append("instructional_content")
        
        return elements
