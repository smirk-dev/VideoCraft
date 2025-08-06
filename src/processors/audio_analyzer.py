import librosa
import numpy as np
import torch
from transformers import pipeline, Wav2Vec2Processor, Wav2Vec2ForSequenceClassification
from typing import List, Dict, Tuple, Optional
import moviepy.editor as mp
import tempfile
import os
import logging
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class AudioAnalyzer:
    """
    Analyzes audio content for speech emotion, speaker changes, and audio features.
    Uses pre-trained models for speech emotion recognition and audio processing.
    """
    
    def __init__(self, config: dict):
        """
        Initialize AudioAnalyzer with configuration settings.
        
        Args:
            config: Configuration dictionary containing model settings
        """
        self.config = config
        self.audio_config = config.get('audio', {})
        
        # Load speech emotion recognition model
        emotion_model = config['models']['emotion_speech']
        logger.info(f"Loading speech emotion model: {emotion_model}")
        
        try:
            self.speech_emotion = pipeline(
                "audio-classification",
                model=emotion_model,
                return_all_scores=True
            )
        except Exception as e:
            logger.warning(f"Could not load speech emotion model: {e}")
            self.speech_emotion = None
        
        # Audio processing parameters
        self.sample_rate = self.audio_config.get('sample_rate', 16000)
        self.chunk_duration = self.audio_config.get('chunk_duration', 5)
        
    def extract_audio_from_video(self, video_path: str) -> str:
        """
        Extract audio from video file and save as temporary WAV file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to extracted audio file
        """
        logger.info(f"Extracting audio from video: {video_path}")
        
        try:
            # Create temporary file for audio
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_audio_path = temp_audio.name
            temp_audio.close()
            
            # Extract audio using moviepy
            video = mp.VideoFileClip(video_path)
            if video.audio is None:
                raise ValueError("Video has no audio track")
                
            audio = video.audio
            audio.write_audiofile(
                temp_audio_path,
                # sample_rate=self.sample_rate,
                verbose=False,
                logger=None
            )
            
            video.close()
            audio.close()
            
            logger.info(f"Audio extracted to: {temp_audio_path}")
            return temp_audio_path
            
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            raise
    
    def extract_audio_features(self, audio_path: str) -> Dict:
        """
        Extract comprehensive audio features using librosa.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary containing audio features
        """
        logger.info(f"Extracting audio features from: {audio_path}")
        
        try:
            # Load audio with librosa
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Extract various audio features
            features = {
                'duration': len(y) / sr,
                'sample_rate': sr,
                
                # Energy features
                'rms_energy': librosa.feature.rms(y=y)[0],
                'energy_mean': np.mean(librosa.feature.rms(y=y)[0]),
                'energy_std': np.std(librosa.feature.rms(y=y)[0]),
                
                # Spectral features
                'spectral_centroids': librosa.feature.spectral_centroid(y=y, sr=sr)[0],
                'spectral_rolloff': librosa.feature.spectral_rolloff(y=y, sr=sr)[0],
                'spectral_bandwidth': librosa.feature.spectral_bandwidth(y=y, sr=sr)[0],
                
                # Rhythm features
                'zero_crossing_rate': librosa.feature.zero_crossing_rate(y)[0],
                'tempo': librosa.beat.tempo(y=y, sr=sr)[0] if len(y) > sr else 120.0,
                
                # MFCC features (for speaker identification)
                'mfcc': librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13),
                
                # Chroma features
                'chroma': librosa.feature.chroma_stft(y=y, sr=sr),
                
                # Raw audio for further processing
                'audio_data': y,
                'timestamps': np.arange(len(y)) / sr
            }
            
            logger.info("Audio features extracted successfully")
            return features
            
        except Exception as e:
            logger.error(f"Error extracting audio features: {e}")
            raise
    
    def analyze_speech_emotion(self, audio_path: str) -> List[Dict]:
        """
        Analyze emotional content of speech in chunks.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of emotion analysis results with timestamps
        """
        if self.speech_emotion is None:
            logger.warning("Speech emotion model not available")
            return []
            
        logger.info(f"Analyzing speech emotion: {audio_path}")
        
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            chunk_samples = int(self.chunk_duration * sr)
            emotion_timeline = []
            
            for i in range(0, len(y), chunk_samples // 2):  # 50% overlap
                chunk = y[i:i + chunk_samples]
                
                if len(chunk) < chunk_samples // 4:  # Skip very short chunks
                    continue
                
                # Pad chunk if necessary
                if len(chunk) < chunk_samples:
                    chunk = np.pad(chunk, (0, chunk_samples - len(chunk)), mode='constant')
                
                # Create temporary chunk file
                chunk_path = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_chunk:
                        chunk_path = temp_chunk.name
                    
                    # Save chunk
                    librosa.output.write_wav(chunk_path, chunk, sr)
                    
                    # Analyze emotion
                    emotions = self.speech_emotion(chunk_path)
                    
                    # Find dominant emotion
                    if emotions and len(emotions) > 0:
                        if isinstance(emotions[0], list):
                            emotions = emotions[0]  # Handle nested list
                        
                        dominant_emotion = max(emotions, key=lambda x: x['score'])
                        
                        emotion_timeline.append({
                            'start_time': i / sr,
                            'end_time': min((i + len(chunk)) / sr, len(y) / sr),
                            'emotion': dominant_emotion['label'],
                            'confidence': dominant_emotion['score'],
                            'all_emotions': {e['label']: e['score'] for e in emotions}
                        })
                    
                except Exception as e:
                    logger.warning(f"Error analyzing chunk at {i/sr:.1f}s: {e}")
                    continue
                    
                finally:
                    # Clean up temporary file
                    if chunk_path and os.path.exists(chunk_path):
                        os.unlink(chunk_path)
            
            logger.info(f"Completed speech emotion analysis with {len(emotion_timeline)} segments")
            return emotion_timeline
            
        except Exception as e:
            logger.error(f"Error in speech emotion analysis: {e}")
            return []
    
    def detect_speaker_changes(self, audio_path: str) -> List[float]:
        """
        Detect potential speaker changes using MFCC feature analysis.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of timestamps where speaker changes are detected
        """
        logger.info(f"Detecting speaker changes: {audio_path}")
        
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Extract MFCC features for speaker identification
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # Simple speaker change detection using MFCC variance
            speaker_changes = [0.0]  # Always include start
            window_size = int(sr * 2)  # 2-second windows
            step_size = window_size // 2  # 1-second steps
            
            for i in range(window_size, len(y) - window_size, step_size):
                # Get MFCC windows
                start_frame = librosa.frames_to_samples([i // 512])[0] // 512
                end_frame = librosa.frames_to_samples([(i + window_size) // 512])[0] // 512
                
                prev_start = max(0, start_frame - window_size // 512)
                
                if prev_start < start_frame < end_frame <= mfccs.shape[1]:
                    window1 = mfccs[:, prev_start:start_frame]
                    window2 = mfccs[:, start_frame:end_frame]
                    
                    if window1.size > 0 and window2.size > 0:
                        # Calculate similarity between windows
                        mean1 = np.mean(window1, axis=1)
                        mean2 = np.mean(window2, axis=1)
                        
                        similarity = np.corrcoef(mean1, mean2)[0, 1]
                        
                        # Threshold for speaker change
                        threshold = self.config['suggestions'].get('speaker_change_threshold', 0.6)
                        if not np.isnan(similarity) and similarity < threshold:
                            timestamp = i / sr
                            # Avoid too close speaker changes
                            if not speaker_changes or timestamp - speaker_changes[-1] > 5.0:
                                speaker_changes.append(timestamp)
            
            logger.info(f"Detected {len(speaker_changes)-1} potential speaker changes")
            return speaker_changes
            
        except Exception as e:
            logger.error(f"Error detecting speaker changes: {e}")
            return [0.0]
    
    def analyze_audio_energy(self, audio_path: str) -> List[Dict]:
        """
        Analyze audio energy levels over time.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of energy analysis data with timestamps
        """
        logger.info(f"Analyzing audio energy: {audio_path}")
        
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Calculate RMS energy in chunks
            chunk_samples = int(sr * 1.0)  # 1-second chunks
            energy_timeline = []
            
            for i in range(0, len(y), chunk_samples):
                chunk = y[i:i + chunk_samples]
                if len(chunk) > 0:
                    rms = np.sqrt(np.mean(chunk**2))
                    
                    energy_timeline.append({
                        'start_time': i / sr,
                        'end_time': min((i + len(chunk)) / sr, len(y) / sr),
                        'rms_energy': float(rms),
                        'db_level': float(20 * np.log10(rms + 1e-10))  # Avoid log(0)
                    })
            
            return energy_timeline
            
        except Exception as e:
            logger.error(f"Error analyzing audio energy: {e}")
            return []
    
    def cleanup_temp_files(self, file_paths: List[str]):
        """
        Clean up temporary audio files.
        
        Args:
            file_paths: List of file paths to delete
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.warning(f"Could not delete temporary file {file_path}: {e}")
