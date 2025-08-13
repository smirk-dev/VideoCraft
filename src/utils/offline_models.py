"""
Offline AI Models Manager - Handles model loading with fallbacks when internet is unavailable
"""

import os
import torch
import numpy as np
from pathlib import Path
import logging
from typing import Dict, Optional, Any, List
import warnings
import pickle
from datetime import datetime

logger = logging.getLogger(__name__)

class OfflineModelManager:
    """
    Manages AI model loading with offline fallbacks when Hugging Face is unavailable.
    Provides basic functionality even without internet connection.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.cache_dir = Path(config.get('ai_models', {}).get('cache_dir', './cache'))
        self.cache_dir.mkdir(exist_ok=True)
        
        # Create offline models directory
        self.offline_models_dir = self.cache_dir / 'offline_models'
        self.offline_models_dir.mkdir(exist_ok=True)
        
        # Model availability status
        self.model_status = {
            'clip_available': False,
            'emotion_available': False,
            'nlp_available': False,
            'offline_mode': True
        }
        
        self.models = {}
        self._initialize_offline_models()
    
    def _initialize_offline_models(self):
        """Initialize basic offline models and fallbacks."""
        try:
            # Try to load any cached models first
            self._load_cached_models()
            
            # If no cached models, initialize basic fallbacks
            if not any(self.model_status.values()):
                self._initialize_basic_fallbacks()
                
        except Exception as e:
            logger.warning(f"Could not initialize offline models: {e}")
            self._initialize_basic_fallbacks()
    
    def _load_cached_models(self):
        """Try to load previously cached models."""
        try:
            # Check for cached CLIP model
            clip_cache = self.offline_models_dir / 'clip_features.pkl'
            if clip_cache.exists():
                with open(clip_cache, 'rb') as f:
                    self.models['clip_features'] = pickle.load(f)
                self.model_status['clip_available'] = True
                logger.info("Loaded cached CLIP features")
            
            # Check for cached emotion model
            emotion_cache = self.offline_models_dir / 'emotion_classifier.pkl'
            if emotion_cache.exists():
                with open(emotion_cache, 'rb') as f:
                    self.models['emotion_classifier'] = pickle.load(f)
                self.model_status['emotion_available'] = True
                logger.info("Loaded cached emotion classifier")
                
        except Exception as e:
            logger.warning(f"Error loading cached models: {e}")
    
    def _initialize_basic_fallbacks(self):
        """Initialize basic rule-based fallbacks."""
        logger.info("Initializing offline fallback models...")
        
        # Basic visual analysis fallback
        self.models['visual_analyzer'] = BasicVisualAnalyzer()
        
        # Basic emotion detector fallback
        self.models['emotion_detector'] = BasicEmotionDetector()
        
        # Basic NLP processor fallback
        self.models['nlp_processor'] = BasicNLPProcessor()
        
        # Basic scene detector fallback
        self.models['scene_detector'] = BasicSceneDetector()
        
        logger.info("Offline fallback models initialized successfully")
    
    def get_model(self, model_type: str):
        """Get a model by type, with fallback to offline versions."""
        if model_type in self.models:
            return self.models[model_type]
        else:
            logger.warning(f"Model {model_type} not available, using basic fallback")
            return self._get_fallback_model(model_type)
    
    def _get_fallback_model(self, model_type: str):
        """Get fallback model for a specific type."""
        fallback_map = {
            'clip': self.models.get('visual_analyzer'),
            'emotion': self.models.get('emotion_detector'),
            'nlp': self.models.get('nlp_processor'),
            'nlp_processor': self.models.get('nlp_processor'),  # Additional mapping
            'scene': self.models.get('scene_detector'),
            'visual_analyzer': self.models.get('visual_analyzer'),
            'emotion_detector': self.models.get('emotion_detector'),
            'scene_detector': self.models.get('scene_detector')
        }
        
        return fallback_map.get(model_type, BasicFallbackModel())
    
    def is_online(self) -> bool:
        """Check if we can connect to Hugging Face."""
        try:
            import requests
            response = requests.get('https://huggingface.co', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get detailed status information."""
        return {
            'offline_mode': not self.is_online(),
            'models_available': self.model_status,
            'cache_dir': str(self.cache_dir),
            'fallback_active': True,
            'last_check': datetime.now().isoformat()
        }


class BasicVisualAnalyzer:
    """Basic visual analysis using OpenCV without pre-trained models."""
    
    def __init__(self):
        self.feature_extractors = {
            'brightness': self._calculate_brightness,
            'contrast': self._calculate_contrast,
            'color_histogram': self._calculate_color_histogram,
            'edge_density': self._calculate_edge_density
        }
    
    def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze a single frame using basic computer vision."""
        try:
            import cv2
            
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            
            features = {}
            for name, extractor in self.feature_extractors.items():
                try:
                    features[name] = extractor(frame, gray)
                except Exception as e:
                    logger.warning(f"Error extracting {name}: {e}")
                    features[name] = 0.0
            
            return features
            
        except Exception as e:
            logger.error(f"Error in basic frame analysis: {e}")
            return {'error': str(e)}
    
    def _calculate_brightness(self, frame: np.ndarray, gray: np.ndarray) -> float:
        """Calculate average brightness."""
        return float(np.mean(gray) / 255.0)
    
    def _calculate_contrast(self, frame: np.ndarray, gray: np.ndarray) -> float:
        """Calculate contrast using standard deviation."""
        return float(np.std(gray) / 255.0)
    
    def _calculate_color_histogram(self, frame: np.ndarray, gray: np.ndarray) -> List[float]:
        """Calculate basic color histogram."""
        try:
            import cv2
            if len(frame.shape) == 3:
                # Calculate histogram for each channel
                hist_b = cv2.calcHist([frame], [0], None, [8], [0, 256])
                hist_g = cv2.calcHist([frame], [1], None, [8], [0, 256])
                hist_r = cv2.calcHist([frame], [2], None, [8], [0, 256])
                
                # Normalize and combine
                hist = np.concatenate([hist_b, hist_g, hist_r]).flatten()
                return (hist / np.sum(hist)).tolist()
            else:
                hist = cv2.calcHist([gray], [0], None, [16], [0, 256])
                return (hist / np.sum(hist)).flatten().tolist()
        except:
            return [0.0] * 24  # Default empty histogram
    
    def _calculate_edge_density(self, frame: np.ndarray, gray: np.ndarray) -> float:
        """Calculate edge density using Canny edge detection."""
        try:
            import cv2
            edges = cv2.Canny(gray, 50, 150)
            return float(np.sum(edges > 0) / edges.size)
        except:
            return 0.0


class BasicEmotionDetector:
    """Basic emotion detection using rule-based analysis."""
    
    def __init__(self):
        # Basic emotion keywords
        self.emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'pleased', 'delighted', 'cheerful', 'glad', 'laugh', 'smile'],
            'sadness': ['sad', 'unhappy', 'depressed', 'melancholy', 'sorrow', 'grief', 'cry', 'tears'],
            'anger': ['angry', 'mad', 'furious', 'rage', 'irritated', 'annoyed', 'frustrated'],
            'fear': ['afraid', 'scared', 'terrified', 'anxious', 'worried', 'nervous', 'panic'],
            'surprise': ['surprised', 'amazed', 'astonished', 'shocked', 'wow', 'incredible'],
            'disgust': ['disgusted', 'revolted', 'repulsed', 'sick', 'gross', 'yuck']
        }
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """Analyze text for emotions using keyword matching."""
        if not text:
            return {'neutral': 1.0}
        
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = score
        
        # Normalize scores
        total_score = sum(emotion_scores.values())
        if total_score > 0:
            emotion_scores = {k: v / total_score for k, v in emotion_scores.items()}
        else:
            emotion_scores = {'neutral': 1.0}
        
        return emotion_scores
    
    def analyze_audio_features(self, audio_features: Dict) -> Dict[str, float]:
        """Analyze audio features for emotional content."""
        # Basic heuristics based on audio features
        energy = audio_features.get('energy', 0.5)
        tempo = audio_features.get('tempo', 120)
        
        emotions = {}
        
        if energy > 0.7:
            emotions['joy'] = 0.6
            emotions['anger'] = 0.3
        elif energy < 0.3:
            emotions['sadness'] = 0.7
        else:
            emotions['neutral'] = 0.8
        
        # Normalize
        total = sum(emotions.values())
        if total > 0:
            emotions = {k: v / total for k, v in emotions.items()}
        
        return emotions


class BasicNLPProcessor:
    """Basic NLP processing without external models."""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being'
        }
    
    def parse_script_file(self, script_path: str) -> List[Dict]:
        """
        Basic script file parsing without advanced NLP models.
        
        Args:
            script_path: Path to script file
            
        Returns:
            List of dialogue entries with basic metadata
        """
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic dialogue parsing
            lines = content.split('\n')
            dialogue_data = []
            line_number = 1
            cumulative_time = 0.0
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Simple speaker detection (UPPERCASE NAME followed by colon)
                if ':' in line and line.split(':')[0].isupper():
                    parts = line.split(':', 1)
                    speaker = parts[0].strip()
                    text = parts[1].strip() if len(parts) > 1 else ""
                else:
                    speaker = "UNKNOWN"
                    text = line
                
                if text:
                    # Basic duration estimation (150 words per minute)
                    word_count = len(text.split())
                    duration = max(0.5, (word_count / 150) * 60)
                    
                    dialogue_entry = {
                        'line_number': line_number,
                        'speaker': speaker,
                        'text': text,
                        'word_count': word_count,
                        'character_count': len(text),
                        'estimated_duration': duration,
                        'estimated_start_time': cumulative_time,
                        'estimated_end_time': cumulative_time + duration,
                        'has_parenthetical': '(' in text and ')' in text,
                        'is_action': speaker.upper() in ['ACTION', 'DESCRIPTION', 'SCENE'],
                        'scene_type': 'dialogue',
                        'emotion': 'neutral',
                        'emotion_confidence': 0.5
                    }
                    
                    dialogue_data.append(dialogue_entry)
                    cumulative_time += duration + 0.5
                    line_number += 1
            
            return dialogue_data
            
        except Exception as e:
            logger.error(f"Error parsing script file with basic parser: {e}")
            return []
    
    def analyze_emotions(self, dialogue_data: List[Dict]) -> List[Dict]:
        """Basic emotion analysis without transformer models."""
        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'wonderful', 'great', 'love', 'amazing'],
            'sadness': ['sad', 'cry', 'tears', 'sorrow', 'grief', 'depressed'],
            'anger': ['angry', 'mad', 'furious', 'rage', 'hate', 'annoyed'],
            'fear': ['scared', 'afraid', 'terrified', 'worried', 'anxious'],
            'surprise': ['surprised', 'shocked', 'amazed', 'unexpected'],
            'disgust': ['disgusted', 'gross', 'awful', 'terrible', 'horrible']
        }
        
        for item in dialogue_data:
            text = item['text'].lower()
            emotion_scores = {}
            
            for emotion, keywords in emotion_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > 0:
                    emotion_scores[emotion] = score
            
            if emotion_scores:
                dominant_emotion = max(emotion_scores, key=emotion_scores.get)
                confidence = min(0.8, emotion_scores[dominant_emotion] * 0.2)
            else:
                dominant_emotion = 'neutral'
                confidence = 0.5
            
            item.update({
                'emotion': dominant_emotion,
                'emotion_confidence': confidence,
                'all_emotions': {dominant_emotion: confidence}
            })
        
        return dialogue_data
    
    def detect_emotional_beats(self, dialogue_data: List[Dict]) -> List[Dict]:
        """Basic emotional beat detection."""
        beats = []
        prev_emotion = None
        
        for item in dialogue_data:
            current_emotion = item.get('emotion', 'neutral')
            
            if prev_emotion and prev_emotion != current_emotion:
                beat = {
                    'timestamp': item.get('estimated_start_time', 0.0),
                    'line_number': item['line_number'],
                    'speaker': item['speaker'],
                    'emotion_from': prev_emotion,
                    'emotion_to': current_emotion,
                    'change_magnitude': 0.5,  # Basic magnitude
                    'context': item['text'][:100] + '...' if len(item['text']) > 100 else item['text']
                }
                beats.append(beat)
            
            prev_emotion = current_emotion
        
        return beats
    
    def extract_character_analysis(self, dialogue_data: List[Dict]) -> Dict[str, Dict]:
        """Basic character analysis."""
        character_analysis = {}
        
        for item in dialogue_data:
            speaker = item['speaker']
            
            if speaker not in character_analysis:
                character_analysis[speaker] = {
                    'total_lines': 0,
                    'total_words': 0,
                    'emotions': {},
                    'average_line_length': 0,
                    'dominant_emotion': 'neutral',
                    'emotional_range': 0
                }
            
            char_data = character_analysis[speaker]
            char_data['total_lines'] += 1
            char_data['total_words'] += item['word_count']
            
            emotion = item.get('emotion', 'neutral')
            char_data['emotions'][emotion] = char_data['emotions'].get(emotion, 0) + 1
        
        # Calculate derived metrics
        for speaker, data in character_analysis.items():
            if data['total_lines'] > 0:
                data['average_line_length'] = data['total_words'] / data['total_lines']
                data['dominant_emotion'] = max(data['emotions'], key=data['emotions'].get)
                data['emotional_range'] = len(data['emotions'])
        
        return character_analysis

    def process_text(self, text: str) -> Dict[str, Any]:
        """Basic text processing and analysis."""
        if not text:
            return {'words': [], 'sentences': [], 'sentiment': 'neutral'}
        
        # Basic tokenization
        words = [word.strip('.,!?;:"').lower() for word in text.split()]
        words = [word for word in words if word and word not in self.stop_words]
        
        # Basic sentence splitting
        sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
        
        # Basic sentiment
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'wrong', 'problem']
        
        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)
        
        if pos_count > neg_count:
            sentiment = 'positive'
        elif neg_count > pos_count:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'words': words,
            'sentences': sentences,
            'sentiment': sentiment,
            'word_count': len(words),
            'sentence_count': len(sentences)
        }
    
    def process_script(self, text: str) -> List[Dict]:
        """Process script text and return basic structure."""
        if not text:
            return []
        
        lines = text.split('\n')
        processed = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            processed.append({
                'line_number': i + 1,
                'text': line,
                'type': 'dialogue' if ':' in line else 'action',
                'word_count': len(line.split()),
                'sentiment': self.process_text(line)['sentiment']
            })
        
        return processed


class BasicSceneDetector:
    """Basic scene change detection using frame differences."""
    
    def __init__(self):
        self.threshold = 0.3
    
    def detect_scene_changes(self, frames: List[np.ndarray]) -> List[float]:
        """Detect scene changes using frame difference analysis."""
        if len(frames) < 2:
            return []
        
        scene_changes = []
        
        try:
            import cv2
            
            for i in range(1, len(frames)):
                # Convert frames to grayscale
                prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY) if len(frames[i-1].shape) == 3 else frames[i-1]
                curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY) if len(frames[i].shape) == 3 else frames[i]
                
                # Calculate frame difference
                diff = cv2.absdiff(prev_gray, curr_gray)
                diff_score = np.mean(diff) / 255.0
                
                if diff_score > self.threshold:
                    scene_changes.append(float(i))  # Frame index as timestamp
            
        except Exception as e:
            logger.warning(f"Error in scene detection: {e}")
        
        return scene_changes


class BasicFallbackModel:
    """Generic fallback model for any AI functionality."""
    
    def __init__(self):
        self.name = "Basic Fallback Model"
        self._is_fallback = True
    
    def predict(self, *args, **kwargs):
        """Basic prediction that returns safe defaults."""
        return {
            'confidence': 0.5,
            'prediction': 'neutral',
            'features': [],
            'status': 'offline_fallback'
        }
    
    def analyze(self, *args, **kwargs):
        """Basic analysis that returns safe defaults."""
        return self.predict(*args, **kwargs)
    
    def parse_script_file(self, script_path: str) -> List[Dict]:
        """Basic script parsing fallback."""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            return [{
                'line_number': i + 1,
                'speaker': 'UNKNOWN',
                'text': line,
                'word_count': len(line.split()),
                'character_count': len(line),
                'estimated_duration': max(0.5, len(line.split()) / 150 * 60),
                'estimated_start_time': i * 2.0,
                'estimated_end_time': (i + 1) * 2.0,
                'has_parenthetical': False,
                'is_action': False,
                'scene_type': 'dialogue',
                'emotion': 'neutral',
                'emotion_confidence': 0.5
            } for i, line in enumerate(lines)]
            
        except Exception as e:
            logger.error(f"Error in fallback script parsing: {e}")
            return []
    
    def analyze_emotions(self, dialogue_data: List[Dict]) -> List[Dict]:
        """Basic emotion analysis fallback."""
        for item in dialogue_data:
            item.update({
                'emotion': 'neutral',
                'emotion_confidence': 0.5,
                'all_emotions': {'neutral': 0.5}
            })
        return dialogue_data
    
    def detect_emotional_beats(self, dialogue_data: List[Dict]) -> List[Dict]:
        """Basic emotional beat detection fallback."""
        return []
    
    def extract_character_analysis(self, dialogue_data: List[Dict]) -> Dict[str, Dict]:
        """Basic character analysis fallback."""
        characters = set(item.get('speaker', 'UNKNOWN') for item in dialogue_data)
        return {
            char: {
                'total_lines': 1,
                'total_words': 10,
                'emotions': {'neutral': 1},
                'average_line_length': 10,
                'dominant_emotion': 'neutral',
                'emotional_range': 1
            } for char in characters
        }
