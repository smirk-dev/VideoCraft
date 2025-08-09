import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel, pipeline
from typing import Dict, List, Optional, Tuple
import logging
from skimage import color  # Add this line
from scipy import ndimage  # Add this line


logger = logging.getLogger(__name__)

class VisualAnalyzer:
    """
    Analyzes visual content using CLIP and other vision models.
    Provides semantic understanding of video frames for editing context.
    """
    
    def __init__(self, config: dict):
        """
        Initialize VisualAnalyzer with vision models.
        
        Args:
            config: Configuration dictionary containing model settings
        """
        self.config = config
        
        # Load CLIP model for general visual understanding
        try:
            clip_model_name = config['models']['visual_features']
            # Load with proper device handling to avoid meta tensor issues
            self.clip_model = CLIPModel.from_pretrained(
                clip_model_name,
                torch_dtype=torch.float32,
                device_map=None  # Don't use device_map to avoid meta tensors
            )
            self.clip_processor = CLIPProcessor.from_pretrained(clip_model_name)
            
            # Explicitly move to CPU (or GPU if available)
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.clip_model = self.clip_model.to(device)
            self.device = device
            
            logger.info(f"CLIP model loaded: {clip_model_name} on {device}")
        except Exception as e:
            logger.error(f"Could not load CLIP model: {e}")
            self.clip_model = None
            self.clip_processor = None
            self.device = torch.device('cpu')
        
        # Try to load face emotion model with proper error handling
        try:
            face_model_name = config['models']['face_emotion']
            self.face_emotion = pipeline(
                "image-classification",
                model=face_model_name,
                torch_dtype=torch.float32,
                device=0 if torch.cuda.is_available() else -1  # Use CPU if no GPU
            )
            logger.info(f"Face emotion model loaded: {face_model_name}")
        except Exception as e:
            logger.warning(f"Could not load face emotion model: {e}")
            self.face_emotion = None
        
        # Define visual concepts for film analysis
        self.cinematography_concepts = [
            "close-up shot", "medium shot", "wide shot", "extreme wide shot",
            "over-the-shoulder shot", "point of view shot", "establishing shot",
            "high angle shot", "low angle shot", "bird's eye view"
        ]
        
        self.mood_concepts = [
            "dramatic lighting", "bright scene", "dark scene", "moody atmosphere",
            "romantic scene", "tense moment", "peaceful setting", "chaotic scene",
            "melancholic mood", "uplifting atmosphere"
        ]
        
        self.content_concepts = [
            "dialogue scene", "action sequence", "emotional moment", "comedy scene",
            "indoor scene", "outdoor scene", "urban setting", "nature scene",
            "crowd scene", "intimate moment", "conflict scene", "resolution scene"
        ]
    
    def analyze_frame_content(self, frame: np.ndarray) -> Dict[str, float]:
        """
        Analyze frame content using CLIP model.
        
        Args:
            frame: Video frame as numpy array
            
        Returns:
            Dictionary with content analysis scores
        """
        if self.clip_model is None or self.clip_processor is None:
            return {}
        
        try:
            # Convert frame to PIL Image
            if frame.dtype == np.float64:
                frame = (frame * 255).astype(np.uint8)
            image = Image.fromarray(frame)
            
            # Combine all concept categories
            all_concepts = (self.cinematography_concepts + 
                          self.mood_concepts + 
                          self.content_concepts)
            
            # Process with CLIP
            inputs = self.clip_processor(
                text=all_concepts,
                images=image,
                return_tensors="pt",
                padding=True
            )
            
            # Move inputs to the same device as the model
            if hasattr(self, 'device'):
                inputs = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                         for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            # Organize results by category
            results = {
                'cinematography': {},
                'mood': {},
                'content': {},
                'overall_scores': {}
            }
            
            # Categorize results
            for i, concept in enumerate(all_concepts):
                score = probs[0][i].item()
                results['overall_scores'][concept] = score
                
                if concept in self.cinematography_concepts:
                    results['cinematography'][concept] = score
                elif concept in self.mood_concepts:
                    results['mood'][concept] = score
                elif concept in self.content_concepts:
                    results['content'][concept] = score
            
            # Find dominant concepts
            results['dominant_shot_type'] = max(results['cinematography'], 
                                              key=results['cinematography'].get)
            results['dominant_mood'] = max(results['mood'], 
                                         key=results['mood'].get)
            results['dominant_content'] = max(results['content'], 
                                            key=results['content'].get)
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing frame content: {e}")
            return {}
    
    def analyze_facial_emotions(self, frame: np.ndarray) -> Dict[str, float]:
        """
        Analyze facial emotions in frame.
        
        Args:
            frame: Video frame as numpy array
            
        Returns:
            Dictionary with facial emotion scores
        """
        if self.face_emotion is None:
            return {}
        
        try:
            # Convert frame to PIL Image
            if frame.dtype == np.float64:
                frame = (frame * 255).astype(np.uint8)
            image = Image.fromarray(frame)
            
            # Analyze facial emotions
            results = self.face_emotion(image)
            
            # Convert to consistent format
            emotions = {}
            for result in results:
                emotion = result['label'].lower()
                score = result['score']
                emotions[emotion] = score
            
            return emotions
            
        except Exception as e:
            logger.error(f"Error analyzing facial emotions: {e}")
            return {}
    
    def analyze_visual_composition(self, frame: np.ndarray) -> Dict:
        """
        Analyze visual composition elements of frame.
        
        Args:
            frame: Video frame as numpy array
            
        Returns:
            Dictionary with composition analysis
        """
        try:
            # Convert to different color spaces for analysis
            gray = np.mean(frame, axis=2) if len(frame.shape) == 3 else frame
            
            composition = {
                'brightness': float(np.mean(gray) / 255.0),
                'contrast': float(np.std(gray) / 255.0),
                'color_saturation': self._calculate_saturation(frame),
                'edge_density': self._calculate_edge_density(gray),
                'symmetry_score': self._calculate_symmetry(gray),
                'rule_of_thirds': self._analyze_rule_of_thirds(gray)
            }
            
            return composition
            
        except Exception as e:
            logger.error(f"Error analyzing visual composition: {e}")
            return {}
    
    def detect_visual_style(self, frames: List[np.ndarray]) -> Dict:
        """
        Detect overall visual style across multiple frames.
        
        Args:
            frames: List of video frames
            
        Returns:
            Dictionary with visual style analysis
        """
        if not frames:
            return {}
        
        try:
            # Analyze each frame
            frame_analyses = []
            for frame in frames:
                composition = self.analyze_visual_composition(frame)
                content = self.analyze_frame_content(frame)
                frame_analyses.append({**composition, **content.get('overall_scores', {})})
            
            # Aggregate style metrics
            style_analysis = {
                'average_brightness': np.mean([f.get('brightness', 0.5) for f in frame_analyses]),
                'average_contrast': np.mean([f.get('contrast', 0.5) for f in frame_analyses]),
                'color_palette': self._analyze_color_palette(frames),
                'visual_consistency': self._calculate_visual_consistency(frame_analyses),
                'predominant_shot_types': self._find_predominant_elements(
                    frame_analyses, self.cinematography_concepts),
                'mood_progression': self._analyze_mood_progression(frame_analyses)
            }
            
            return style_analysis
            
        except Exception as e:
            logger.error(f"Error detecting visual style: {e}")
            return {}
    
    def _calculate_saturation(self, frame: np.ndarray) -> float:
        """Calculate color saturation of frame."""
        if len(frame.shape) != 3:
            return 0.0
        
        # Convert to HSV
        from skimage import color
        try:
            hsv = color.rgb2hsv(frame / 255.0)
            return float(np.mean(hsv[:, :, 1]))
        except:
            return 0.0
    
    def _calculate_edge_density(self, gray_frame: np.ndarray) -> float:
        """Calculate edge density using Sobel operator."""
        try:
            from scipy import ndimage
            sobel_x = ndimage.sobel(gray_frame, axis=0)
            sobel_y = ndimage.sobel(gray_frame, axis=1)
            edges = np.hypot(sobel_x, sobel_y)
            return float(np.mean(edges) / 255.0)
        except:
            return 0.0
    
    def _calculate_symmetry(self, gray_frame: np.ndarray) -> float:
        """Calculate symmetry score of frame."""
        try:
            height, width = gray_frame.shape
            left_half = gray_frame[:, :width//2]
            right_half = np.fliplr(gray_frame[:, width//2:])
            
            # Resize to match if different sizes
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = left_half[:, :min_width]
            right_half = right_half[:, :min_width]
            
            # Calculate correlation
            correlation = np.corrcoef(left_half.flatten(), right_half.flatten())[0, 1]
            return max(0.0, correlation) if not np.isnan(correlation) else 0.0
        except:
            return 0.0
    
    def _analyze_rule_of_thirds(self, gray_frame: np.ndarray) -> Dict[str, float]:
        """Analyze adherence to rule of thirds."""
        try:
            height, width = gray_frame.shape
            
            # Define rule of thirds grid lines
            h_lines = [height // 3, 2 * height // 3]
            v_lines = [width // 3, 2 * width // 3]
            
            # Calculate interest points near grid intersections
            interest_score = 0.0
            total_intersections = 4
            
            for h_line in h_lines:
                for v_line in v_lines:
                    # Sample area around intersection
                    region = gray_frame[max(0, h_line-10):min(height, h_line+10),
                                      max(0, v_line-10):min(width, v_line+10)]
                    
                    # High variance indicates interesting content
                    if region.size > 0:
                        interest_score += np.var(region)
            
            return {
                'rule_of_thirds_score': float(interest_score / total_intersections / 10000),
                'composition_balance': self._calculate_balance(gray_frame)
            }
        except:
            return {'rule_of_thirds_score': 0.0, 'composition_balance': 0.5}
    
    def _calculate_balance(self, gray_frame: np.ndarray) -> float:
        """Calculate visual balance of frame."""
        try:
            height, width = gray_frame.shape
            center_y, center_x = height // 2, width // 2
            
            # Calculate moments
            y_indices, x_indices = np.ogrid[:height, :width]
            
            # Weight by pixel intensity
            weights = gray_frame
            
            # Calculate center of mass
            total_weight = np.sum(weights)
            if total_weight == 0:
                return 0.5
            
            center_of_mass_y = np.sum(y_indices * weights) / total_weight
            center_of_mass_x = np.sum(x_indices * weights) / total_weight
            
            # Distance from geometric center
            distance = np.sqrt((center_of_mass_y - center_y)**2 + (center_of_mass_x - center_x)**2)
            max_distance = np.sqrt(center_y**2 + center_x**2)
            
            # Balance score (1 = perfectly balanced, 0 = very unbalanced)
            balance = 1.0 - (distance / max_distance)
            return float(max(0.0, balance))
        except:
            return 0.5
    
    def _analyze_color_palette(self, frames: List[np.ndarray]) -> Dict:
        """Analyze color palette across frames."""
        try:
            # Sample colors from frames
            all_colors = []
            for frame in frames[::max(1, len(frames)//10)]:  # Sample every 10th frame
                resized = frame[::10, ::10]  # Downsample for efficiency
                all_colors.extend(resized.reshape(-1, 3))
            
            all_colors = np.array(all_colors)
            
            # Simple color analysis
            avg_color = np.mean(all_colors, axis=0)
            color_std = np.std(all_colors, axis=0)
            
            return {
                'dominant_color_rgb': avg_color.tolist(),
                'color_variance': color_std.tolist(),
                'color_temperature': self._estimate_color_temperature(avg_color)
            }
        except:
            return {}
    
    def _estimate_color_temperature(self, rgb: np.ndarray) -> str:
        """Estimate color temperature from RGB values."""
        r, g, b = rgb
        
        if b > r and b > g:
            return 'cool'
        elif r > b and r > g:
            return 'warm'
        else:
            return 'neutral'
    
    def _calculate_visual_consistency(self, frame_analyses: List[Dict]) -> float:
        """Calculate visual consistency across frames."""
        if len(frame_analyses) < 2:
            return 1.0
        
        try:
            # Calculate standard deviation of key visual metrics
            brightness_std = np.std([f.get('brightness', 0.5) for f in frame_analyses])
            contrast_std = np.std([f.get('contrast', 0.5) for f in frame_analyses])
            
            # Consistency is inverse of variance
            consistency = 1.0 / (1.0 + brightness_std + contrast_std)
            return float(consistency)
        except:
            return 0.5
    
    def _find_predominant_elements(self, frame_analyses: List[Dict], concepts: List[str]) -> Dict[str, float]:
        """Find predominant elements across frames."""
        concept_scores = {}
        
        for concept in concepts:
            scores = [f.get(concept, 0.0) for f in frame_analyses if concept in f]
            if scores:
                concept_scores[concept] = np.mean(scores)
        
        return concept_scores
    
    def _analyze_mood_progression(self, frame_analyses: List[Dict]) -> List[str]:
        """Analyze mood progression across frames."""
        mood_progression = []
        
        for analysis in frame_analyses:
            # Find dominant mood concept
            mood_scores = {k: v for k, v in analysis.items() if any(mood in k for mood in self.mood_concepts)}
            if mood_scores:
                dominant_mood = max(mood_scores, key=mood_scores.get)
                mood_progression.append(dominant_mood)
        
        return mood_progression
