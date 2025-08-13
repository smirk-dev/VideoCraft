import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import moviepy.editor as mp
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class SceneDetector:
    """
    Detects scene changes in video using various computer vision techniques.
    Combines histogram analysis, edge detection, and optical flow for robust scene detection.
    """
    
    def __init__(self, config: dict):
        """
        Initialize SceneDetector with configuration settings.
        
        Args:
            config: Configuration dictionary containing detection thresholds
        """
        self.config = config
        self.scene_threshold = config['suggestions'].get('scene_change_threshold', 0.4)
        self.video_config = config.get('video', {})
        
        # Detection parameters
        self.min_scene_length = 2.0  # Minimum scene length in seconds
        self.detection_methods = ['histogram', 'edge_density', 'optical_flow']
        
    def detect_scenes(self, video_path: str, method: str = 'combined') -> List[Dict]:
        """
        Detect scene changes in video using specified method.
        
        Args:
            video_path: Path to video file
            method: Detection method ('histogram', 'edge_density', 'optical_flow', 'combined')
            
        Returns:
            List of scene change points with metadata
        """
        logger.info(f"Detecting scenes in {video_path} using {method} method")
        
        try:
            if method == 'combined':
                return self._detect_scenes_combined(video_path)
            elif method == 'histogram':
                return self._detect_scenes_histogram(video_path)
            elif method == 'edge_density':
                return self._detect_scenes_edge_density(video_path)
            elif method == 'optical_flow':
                return self._detect_scenes_optical_flow(video_path)
            else:
                raise ValueError(f"Unknown detection method: {method}")
                
        except Exception as e:
            logger.error(f"Error in scene detection: {e}")
            raise
    
    def _detect_scenes_combined(self, video_path: str) -> List[Dict]:
        """
        Detect scenes using combined methods for better accuracy.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of scene changes with confidence scores
        """
        # Get detections from different methods
        hist_scenes = self._detect_scenes_histogram(video_path)
        edge_scenes = self._detect_scenes_edge_density(video_path)
        
        # Combine and rank scene changes
        all_scenes = {}
        
        # Add histogram-based detections
        for scene in hist_scenes:
            timestamp = scene.get('timestamp', 0.0) if hasattr(scene, 'get') else scene.get('timestamp', 0.0)
            all_scenes[timestamp] = {
                'timestamp': timestamp,
                'confidence': scene.get('confidence', 0.5) if hasattr(scene, 'get') else scene.get('confidence', 0.5),
                'methods': ['histogram'],
                'scores': {'histogram': scene.get('confidence', 0.5) if hasattr(scene, 'get') else scene.get('confidence', 0.5)}
            }
        
        # Add edge-based detections
        for scene in edge_scenes:
            timestamp = scene.get('timestamp', 0.0) if hasattr(scene, 'get') else scene.get('timestamp', 0.0)
            if timestamp in all_scenes:
                all_scenes[timestamp]['methods'].append('edge_density')
                all_scenes[timestamp]['scores']['edge_density'] = scene.get('confidence', 0.5) if hasattr(scene, 'get') else scene.get('confidence', 0.5)
                # Boost confidence for multiple detections
                scene_confidence = scene.get('confidence', 0.5) if hasattr(scene, 'get') else scene.get('confidence', 0.5)
                all_scenes[timestamp]['confidence'] = min(1.0, 
                    all_scenes[timestamp]['confidence'] + scene_confidence * 0.3)
            else:
                all_scenes[timestamp] = {
                    'timestamp': timestamp,
                    'confidence': scene['confidence'],
                    'methods': ['edge_density'],
                    'scores': {'edge_density': scene['confidence']}
                }
        
        # Filter and sort scenes
        combined_scenes = []
        for scene_data in all_scenes.values():
            # Calculate final confidence
            method_count = len(scene_data['methods'])
            confidence_boost = 0.1 * (method_count - 1)  # Boost for multiple methods
            final_confidence = min(1.0, scene_data['confidence'] + confidence_boost)
            
            if final_confidence >= self.scene_threshold:
                combined_scenes.append({
                    'timestamp': scene_data['timestamp'],
                    'confidence': final_confidence,
                    'detection_methods': scene_data['methods'],
                    'method_scores': scene_data['scores'],
                    'reason': f"Scene change detected by {', '.join(scene_data['methods'])}"
                })
        
        # Sort by timestamp and filter close detections
        combined_scenes.sort(key=lambda x: x.get('timestamp', 0.0) if hasattr(x, 'get') else x.get('timestamp', 0.0))
        filtered_scenes = self._filter_close_scenes(combined_scenes)
        
        logger.info(f"Detected {len(filtered_scenes)} scene changes using combined methods")
        return filtered_scenes
    
    def _detect_scenes_histogram(self, video_path: str) -> List[Dict]:
        """
        Detect scenes using color histogram comparison.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of scene changes based on histogram analysis
        """
        logger.info("Detecting scenes using histogram method")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        scenes = []
        prev_hist = None
        frame_idx = 0
        
        # Process every nth frame for efficiency
        frame_skip = max(1, int(fps * 0.5))  # Sample every 0.5 seconds
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % frame_skip == 0:
                # Calculate histogram
                hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                
                if prev_hist is not None:
                    # Calculate histogram similarity
                    similarity = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                    dissimilarity = 1.0 - similarity
                    
                    # Check for scene change
                    if dissimilarity > self.scene_threshold:
                        timestamp = frame_idx / fps
                        
                        scenes.append({
                            'timestamp': timestamp,
                            'confidence': dissimilarity,
                            'frame_number': frame_idx,
                            'method': 'histogram',
                            'similarity_score': similarity
                        })
                
                prev_hist = hist
                
            frame_idx += 1
        
        cap.release()
        return scenes
    
    def _detect_scenes_edge_density(self, video_path: str) -> List[Dict]:
        """
        Detect scenes using edge density changes.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of scene changes based on edge analysis
        """
        logger.info("Detecting scenes using edge density method")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        scenes = []
        prev_edge_density = None
        frame_idx = 0
        
        # Process every nth frame
        frame_skip = max(1, int(fps * 0.5))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % frame_skip == 0:
                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Calculate edge density using Canny
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges) / (edges.shape[0] * edges.shape[1])
                
                if prev_edge_density is not None:
                    # Calculate change in edge density
                    density_change = abs(edge_density - prev_edge_density) / max(prev_edge_density, 0.001)
                    
                    # Normalize to 0-1 range
                    normalized_change = np.tanh(density_change * 5)
                    
                    if normalized_change > self.scene_threshold:
                        timestamp = frame_idx / fps
                        
                        scenes.append({
                            'timestamp': timestamp,
                            'confidence': normalized_change,
                            'frame_number': frame_idx,
                            'method': 'edge_density',
                            'edge_density': edge_density,
                            'density_change': density_change
                        })
                
                prev_edge_density = edge_density
                
            frame_idx += 1
        
        cap.release()
        return scenes
    
    def _detect_scenes_optical_flow(self, video_path: str) -> List[Dict]:
        """
        Detect scenes using optical flow analysis.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of scene changes based on motion analysis
        """
        logger.info("Detecting scenes using optical flow method")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        scenes = []
        
        # Read first frame
        ret, prev_frame = cap.read()
        if not ret:
            cap.release()
            return scenes
        
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        frame_idx = 1
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowPyrLK(
                prev_gray, gray, 
                np.array([[]], dtype=np.float32), None
            )
            
            # Calculate motion magnitude
            if flow[0] is not None and len(flow[0]) > 0:
                motion_magnitude = np.mean(np.sqrt(flow[0][:, :, 0]**2 + flow[0][:, :, 1]**2))
            else:
                motion_magnitude = 0
            
            # Detect sudden motion changes (potential scene cuts)
            if frame_idx > 1:  # Need at least 2 frames for comparison
                # This is a simplified approach - in practice, you'd track motion over time
                if motion_magnitude > 50:  # Threshold for significant motion change
                    timestamp = frame_idx / fps
                    
                    scenes.append({
                        'timestamp': timestamp,
                        'confidence': min(1.0, motion_magnitude / 100),
                        'frame_number': frame_idx,
                        'method': 'optical_flow',
                        'motion_magnitude': motion_magnitude
                    })
            
            prev_gray = gray
            frame_idx += 1
        
        cap.release()
        return scenes
    
    def _filter_close_scenes(self, scenes: List[Dict]) -> List[Dict]:
        """
        Filter out scene changes that are too close to each other.
        
        Args:
            scenes: List of detected scene changes
            
        Returns:
            Filtered list of scene changes
        """
        if not scenes:
            return scenes
        
        filtered = [scenes[0]]  # Always keep first scene
        
        for scene in scenes[1:]:
            # Check if this scene is far enough from the last kept scene
            scene_timestamp = scene.get('timestamp', 0.0) if hasattr(scene, 'get') else scene.get('timestamp', 0.0)
            last_timestamp = filtered[-1].get('timestamp', 0.0) if hasattr(filtered[-1], 'get') else filtered[-1].get('timestamp', 0.0)
            time_diff = scene_timestamp - last_timestamp
            
            if time_diff >= self.min_scene_length:
                filtered.append(scene)
            elif scene.get('confidence', 0.5) > filtered[-1].get('confidence', 0.5):
                # Replace with higher confidence scene if within minimum interval
                filtered[-1] = scene
        
        return filtered
    
    def analyze_scene_content(self, video_path: str, scene_timestamps: List[float]) -> List[Dict]:
        """
        Analyze the content of detected scenes.
        
        Args:
            video_path: Path to video file
            scene_timestamps: List of scene start timestamps
            
        Returns:
            List of scene analysis data
        """
        logger.info(f"Analyzing content of {len(scene_timestamps)} scenes")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        scene_analysis = []
        
        for i, timestamp in enumerate(scene_timestamps):
            # Seek to scene start
            frame_number = int(timestamp * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Analyze scene content
            analysis = {
                'scene_number': i + 1,
                'start_timestamp': timestamp,
                'frame_number': frame_number,
                'brightness': self._calculate_brightness(frame),
                'contrast': self._calculate_contrast(frame),
                'color_dominance': self._analyze_color_dominance(frame),
                'motion_level': 'unknown'  # Would need multiple frames to determine
            }
            
            # Determine scene next timestamp for duration
            if i + 1 < len(scene_timestamps):
                analysis['end_timestamp'] = scene_timestamps[i + 1]
                analysis['duration'] = scene_timestamps[i + 1] - timestamp
            else:
                # Last scene - estimate duration
                analysis['end_timestamp'] = timestamp + 30.0  # Default 30 seconds
                analysis['duration'] = 30.0
            
            scene_analysis.append(analysis)
        
        cap.release()
        logger.info(f"Completed scene content analysis")
        return scene_analysis
    
    def _calculate_brightness(self, frame: np.ndarray) -> float:
        """Calculate average brightness of frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return np.mean(gray) / 255.0
    
    def _calculate_contrast(self, frame: np.ndarray) -> float:
        """Calculate contrast of frame using standard deviation."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return np.std(gray) / 255.0
    
    def _analyze_color_dominance(self, frame: np.ndarray) -> Dict[str, float]:
        """Analyze dominant colors in frame."""
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define color ranges in HSV
        color_ranges = {
            'red': [(0, 50, 50), (10, 255, 255)],
            'blue': [(100, 50, 50), (130, 255, 255)],
            'green': [(40, 50, 50), (80, 255, 255)],
            'yellow': [(20, 50, 50), (40, 255, 255)]
        }
        
        color_dominance = {}
        total_pixels = frame.shape[0] * frame.shape[1]
        
        for color_name, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            color_pixels = np.sum(mask > 0)
            color_dominance[color_name] = color_pixels / total_pixels
        
        return color_dominance
