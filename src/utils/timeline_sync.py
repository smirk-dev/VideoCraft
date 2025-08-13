import numpy as np
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class TimelineSync:
    """
    Utilities for synchronizing timelines between different analysis components.
    Handles alignment of script, video, and audio timelines.
    """
    
    def __init__(self, config: dict):
        """
        Initialize TimelineSync with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
    def align_script_to_video(self, 
                             script_data: List[Dict],
                             video_duration: float,
                             speech_timeline: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Align script timeline to video duration.
        
        Args:
            script_data: Script dialogue data
            video_duration: Total video duration in seconds
            speech_timeline: Optional speech detection timeline for better alignment
            
        Returns:
            Script data with corrected timestamps
        """
        logger.info("Aligning script to video timeline")
        
        if not script_data:
            return []
        
        aligned_script = script_data.copy()
        
        # Calculate total estimated script duration
        estimated_duration = sum(item.get('estimated_duration', 0) for item in script_data)
        
        if estimated_duration == 0:
            logger.warning("No estimated durations in script data")
            return aligned_script
        
        # Calculate scaling factor
        scaling_factor = video_duration / estimated_duration
        
        logger.info(f"Script scaling factor: {scaling_factor:.2f}")
        
        # Apply scaling to timestamps
        cumulative_time = 0.0
        for item in aligned_script:
            original_start = item.get('estimated_start_time', cumulative_time)
            original_duration = item.get('estimated_duration', 2.0)
            
            # Scale timestamps
            scaled_start = original_start * scaling_factor
            scaled_duration = original_duration * scaling_factor
            scaled_end = scaled_start + scaled_duration
            
            # Update timestamps
            item['estimated_start_time'] = scaled_start
            item['estimated_end_time'] = scaled_end
            item['estimated_duration'] = scaled_duration
            item['scaling_applied'] = scaling_factor
            
            cumulative_time = scaled_end
        
        # Fine-tune alignment using speech detection if available
        if speech_timeline:
            aligned_script = self._fine_tune_with_speech(aligned_script, speech_timeline)
        
        return aligned_script
    
    def synchronize_emotion_timelines(self, 
                                    text_emotions: List[Dict],
                                    speech_emotions: List[Dict]) -> List[Dict]:
        """
        Synchronize text-based and speech-based emotion timelines.
        
        Args:
            text_emotions: Emotion analysis from script text
            speech_emotions: Emotion analysis from speech audio
            
        Returns:
            Synchronized emotion timeline
        """
        logger.info("Synchronizing emotion timelines")
        
        synchronized = []
        
        # Create time-based mapping
        for text_emotion in text_emotions:
            text_start = text_emotion.get('estimated_start_time', 0)
            text_end = text_emotion.get('estimated_end_time', text_start + 5)
            
            # Find overlapping speech emotions
            overlapping_speech = []
            for speech_emotion in speech_emotions:
                speech_start = speech_emotion.get('start_time', 0)
                speech_end = speech_emotion.get('end_time', speech_start + 5)
                
                # Check for overlap
                if self._time_ranges_overlap(
                    (text_start, text_end), 
                    (speech_start, speech_end)
                ):
                    overlapping_speech.append(speech_emotion)
            
            # Combine emotion data
            combined_emotion = {
                'start_time': text_start,
                'end_time': text_end,
                'text_emotion': text_emotion.get('emotion', 'neutral'),
                'text_confidence': text_emotion.get('emotion_confidence', 0.5),
                'speech_emotions': overlapping_speech,
                'speaker': text_emotion.get('speaker', 'Unknown'),
                'line_number': text_emotion.get('line_number', 0)
            }
            
            # Determine dominant emotion
            if overlapping_speech:
                # Use speech emotion if available and confident
                speech_emotion = overlapping_speech[0]  # Use first/strongest match
                if speech_emotion.get('confidence', 0) > 0.6:
                    combined_emotion['emotion'] = speech_emotion.get('emotion', 'neutral')
                    combined_emotion['confidence'] = speech_emotion.get('confidence', 0.5)
                else:
                    # Fall back to text emotion
                    combined_emotion['emotion'] = text_emotion.get('emotion', 'neutral')
                    combined_emotion['confidence'] = text_emotion.get('emotion_confidence', 0.5)
            else:
                # Use text emotion only
                combined_emotion['emotion'] = text_emotion.get('emotion', 'neutral')
                combined_emotion['confidence'] = text_emotion.get('emotion_confidence', 0.5)
            
            synchronized.append(combined_emotion)
        
        return synchronized
    
    def create_unified_timeline(self, 
                               video_analysis: Dict,
                               audio_analysis: Dict,
                               script_analysis: Dict) -> Dict:
        """
        Create a unified timeline combining all analysis results.
        
        Args:
            video_analysis: Video analysis results
            audio_analysis: Audio analysis results  
            script_analysis: Script analysis results
            
        Returns:
            Unified timeline data structure
        """
        logger.info("Creating unified timeline")
        
        # Get video duration as reference
        video_duration = audio_analysis.get('features', {}).get('duration', 60)
        
        # Create time grid (1-second intervals)
        time_points = np.arange(0, video_duration, 1.0)
        
        unified_timeline = {
            'time_points': time_points.tolist(),
            'video_features': [],
            'audio_features': [],
            'emotion_data': [],
            'script_data': [],
            'scene_changes': [],
            'speaker_changes': []
        }
        
        # Map video analysis
        scene_changes = video_analysis.get('scene_changes', [])
        for time_point in time_points:
            # Find closest video analysis point
            video_features = self._get_features_at_time(time_point, scene_changes)
            unified_timeline['video_features'].append(video_features)
        
        # Map audio analysis
        audio_timeline = audio_analysis.get('speech_emotions', [])
        for time_point in time_points:
            audio_features = self._get_audio_features_at_time(time_point, audio_timeline)
            unified_timeline['audio_features'].append(audio_features)
        
        # Map script analysis
        dialogue_data = script_analysis.get('dialogue_data', [])
        for time_point in time_points:
            script_features = self._get_script_features_at_time(time_point, dialogue_data)
            unified_timeline['script_data'].append(script_features)
        
        # Add events
        unified_timeline['scene_changes'] = self._extract_event_timestamps(scene_changes)
        unified_timeline['speaker_changes'] = audio_analysis.get('speaker_changes', [])
        
        return unified_timeline
    
    def interpolate_missing_timestamps(self, timeline_data: List[Dict]) -> List[Dict]:
        """
        Interpolate missing or irregular timestamps in timeline data.
        
        Args:
            timeline_data: Timeline data with potentially irregular timestamps
            
        Returns:
            Timeline with interpolated regular timestamps
        """
        if not timeline_data:
            return []
        
        # Extract timestamps and sort
        timestamps = [item.get('timestamp', 0) for item in timeline_data]
        sorted_indices = np.argsort(timestamps)
        sorted_data = [timeline_data[i] for i in sorted_indices]
        sorted_timestamps = [timestamps[i] for i in sorted_indices]
        
        # Determine regular interval
        if len(sorted_timestamps) > 1:
            intervals = np.diff(sorted_timestamps)
            regular_interval = np.median(intervals)
        else:
            regular_interval = 1.0
        
        # Create regular timeline
        start_time = min(sorted_timestamps)
        end_time = max(sorted_timestamps)
        regular_times = np.arange(start_time, end_time + regular_interval, regular_interval)
        
        interpolated_data = []
        for time_point in regular_times:
            # Find closest data point
            closest_idx = np.argmin([abs(t - time_point) for t in sorted_timestamps])
            closest_data = sorted_data[closest_idx].copy()
            
            # Update timestamp
            closest_data['timestamp'] = time_point
            closest_data['interpolated'] = abs(sorted_timestamps[closest_idx] - time_point) > regular_interval / 2
            
            interpolated_data.append(closest_data)
        
        return interpolated_data
    
    def _fine_tune_with_speech(self, 
                              script_data: List[Dict], 
                              speech_timeline: List[Dict]) -> List[Dict]:
        """Fine-tune script alignment using speech detection."""
        fine_tuned = script_data.copy()
        
        # Simple alignment: match script segments to speech segments
        for script_item in fine_tuned:
            script_start = script_item.get('estimated_start_time', 0)
            script_duration = script_item.get('estimated_duration', 2.0)
            
            # Find closest speech segment
            closest_speech = None
            min_distance = float('inf')
            
            for speech_item in speech_timeline:
                speech_start = speech_item.get('start_time', 0)
                distance = abs(speech_start - script_start)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_speech = speech_item
            
            # Adjust timing if close speech segment found
            if closest_speech and min_distance < script_duration:
                script_item['estimated_start_time'] = closest_speech.get('start_time', script_start)
                script_item['speech_aligned'] = True
        
        return fine_tuned
    
    def _time_ranges_overlap(self, range1: Tuple[float, float], range2: Tuple[float, float]) -> bool:
        """Check if two time ranges overlap."""
        start1, end1 = range1
        start2, end2 = range2
        return start1 < end2 and start2 < end1
    
    def _get_features_at_time(self, time_point: float, features: List) -> Dict:
        """Get video features at specific time point."""
        # Find closest feature point
        if not features:
            logger.warning(f"No features available for time point {time_point}")
            return {
                'timestamp': time_point,
                'scene_type': 'unknown',
                'confidence': 0.0,
                'status': 'no_data_available',
                'interpolated': True
            }
        
        closest_feature = None
        min_distance = float('inf')
        
        for feature in features:
            if isinstance(feature, dict):
                timestamp = feature.get('timestamp', 0)
            else:
                timestamp = float(feature)
            
            distance = abs(timestamp - time_point)
            if distance < min_distance:
                min_distance = distance
                closest_feature = feature
        
        # Return the closest feature or create a default one
        if isinstance(closest_feature, dict):
            result = closest_feature.copy()
            result['distance_from_query'] = min_distance
            result['interpolated'] = min_distance > 1.0  # Mark as interpolated if > 1 second away
            return result
        else:
            return {
                'timestamp': closest_feature if closest_feature is not None else time_point,
                'scene_type': 'default',
                'confidence': 0.3,
                'status': 'basic_timestamp_only',
                'distance_from_query': min_distance,
                'interpolated': True
            }
    
    def _get_audio_features_at_time(self, time_point: float, audio_timeline: List[Dict]) -> Dict:
        """Get audio features at specific time point."""
        # First try exact match
        for audio_item in audio_timeline:
            start_time = audio_item.get('start_time', 0)
            end_time = audio_item.get('end_time', start_time + 5)
            
            if start_time <= time_point <= end_time:
                result = audio_item.copy()
                result['exact_match'] = True
                return result
        
        # If no exact match, find closest
        if audio_timeline:
            closest_item = None
            min_distance = float('inf')
            
            for audio_item in audio_timeline:
                start_time = audio_item.get('start_time', 0)
                distance = abs(start_time - time_point)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_item = audio_item
            
            if closest_item:
                result = closest_item.copy()
                result['exact_match'] = False
                result['distance_from_query'] = min_distance
                result['interpolated'] = min_distance > 2.0
                return result
        
        # No audio data available - return silence default
        logger.warning(f"No audio features available for time point {time_point}")
        return {
            'timestamp': time_point,
            'emotion': 'neutral',
            'confidence': 0.0,
            'energy': 0.0,
            'speaker': 'unknown',
            'status': 'no_audio_data',
            'exact_match': False,
            'interpolated': True
        }
    
    def _get_script_features_at_time(self, time_point: float, dialogue_data: List[Dict]) -> Dict:
        """Get script features at specific time point."""
        # First try exact match
        for dialogue_item in dialogue_data:
            start_time = dialogue_item.get('estimated_start_time', 0)
            end_time = dialogue_item.get('estimated_end_time', start_time + 2)
            
            if start_time <= time_point <= end_time:
                result = dialogue_item.copy()
                result['exact_match'] = True
                return result
        
        # If no exact match, find closest dialogue
        if dialogue_data:
            closest_item = None
            min_distance = float('inf')
            
            for dialogue_item in dialogue_data:
                start_time = dialogue_item.get('estimated_start_time', 0)
                distance = abs(start_time - time_point)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_item = dialogue_item
            
            if closest_item and min_distance < 10.0:  # Within 10 seconds
                result = closest_item.copy()
                result['exact_match'] = False
                result['distance_from_query'] = min_distance
                result['interpolated'] = True
                return result
        
        # No script data available - return silence/action default
        logger.debug(f"No script features available for time point {time_point}")
        return {
            'timestamp': time_point,
            'dialogue': '',
            'speaker': 'none',
            'emotion': 'neutral',
            'scene_type': 'action',
            'confidence': 0.0,
            'status': 'no_script_data',
            'exact_match': False,
            'interpolated': True
        }
    
    def _extract_event_timestamps(self, events: List) -> List[float]:
        """Extract timestamps from event list."""
        timestamps = []
        for event in events:
            if isinstance(event, dict):
                timestamp = event.get('timestamp', 0)
            else:
                timestamp = float(event)
            timestamps.append(timestamp)
        
        return sorted(timestamps)
