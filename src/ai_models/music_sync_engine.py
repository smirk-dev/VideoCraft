import librosa
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
from scipy.signal import find_peaks
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BeatInfo:
    timestamp: float
    confidence: float
    strength: float
    tempo: float
    beat_type: str  # downbeat, upbeat, accent

@dataclass
class MusicalStructure:
    sections: List[Dict]  # verse, chorus, bridge, etc.
    tempo_changes: List[Tuple[float, float]]  # (timestamp, new_tempo)
    key_changes: List[Tuple[float, str]]  # (timestamp, new_key)
    energy_profile: List[Tuple[float, float]]  # (timestamp, energy_level)

class MusicSyncEngine:
    """
    Advanced music synchronization for beat-perfect video editing.
    Analyzes musical structure and suggests cuts that align with musical elements.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.sample_rate = 22050  # Standard for music analysis
        
        # Musical analysis parameters
        self.hop_length = 512
        self.frame_length = 2048
        
        # Beat detection sensitivity
        self.beat_threshold = 0.3
        self.tempo_tolerance = 0.1
        
    def analyze_musical_structure(self, audio_path: str) -> MusicalStructure:
        """
        Comprehensive musical analysis including tempo, beats, and structure.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            MusicalStructure with detailed musical information
        """
        logger.info(f"Analyzing musical structure: {audio_path}")
        
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Analyze different musical elements
            beats = self._detect_beats(y, sr)
            tempo_changes = self._detect_tempo_changes(y, sr)
            sections = self._detect_musical_sections(y, sr)
            energy_profile = self._analyze_energy_profile(y, sr)
            key_changes = self._detect_key_changes(y, sr)
            
            structure = MusicalStructure(
                sections=sections,
                tempo_changes=tempo_changes,
                key_changes=key_changes,
                energy_profile=energy_profile
            )
            
            logger.info(f"Musical analysis complete: {len(sections)} sections, {len(tempo_changes)} tempo changes")
            return structure
            
        except Exception as e:
            logger.error(f"Musical analysis failed: {e}")
            return MusicalStructure([], [], [], [])
    
    def _detect_beats(self, y: np.ndarray, sr: int) -> List[BeatInfo]:
        """Detect beats with detailed information."""
        
        # Track beats
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
        beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=self.hop_length)
        
        # Onset detection for beat strength
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
        onset_times = librosa.frames_to_time(librosa.onset.onset_detect(
            onset_envelope=onset_env, sr=sr, hop_length=self.hop_length
        ), sr=sr, hop_length=self.hop_length)
        
        # Downbeat detection
        downbeats = self._detect_downbeats(y, sr, beat_times)
        
        beat_info = []
        for i, beat_time in enumerate(beat_times):
            # Calculate beat strength
            frame_idx = librosa.time_to_frames(beat_time, sr=sr, hop_length=self.hop_length)
            strength = onset_env[min(frame_idx, len(onset_env) - 1)]
            
            # Determine beat type
            beat_type = "downbeat" if beat_time in downbeats else "upbeat"
            
            # Calculate confidence based on onset alignment
            confidence = self._calculate_beat_confidence(beat_time, onset_times)
            
            beat_info.append(BeatInfo(
                timestamp=beat_time,
                confidence=confidence,
                strength=float(strength),
                tempo=float(tempo),
                beat_type=beat_type
            ))
        
        return beat_info
    
    def _detect_downbeats(self, y: np.ndarray, sr: int, beat_times: np.ndarray) -> List[float]:
        """Detect downbeats (strong beats) in the music."""
        try:
            # Use chroma features to detect harmonic changes indicating downbeats
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=self.hop_length)
            
            # Calculate harmonic change strength
            chroma_diff = np.diff(chroma, axis=1)
            harmonic_novelty = np.sum(np.abs(chroma_diff), axis=0)
            
            # Find peaks in harmonic novelty that align with beats
            novelty_peaks, _ = find_peaks(harmonic_novelty, height=np.mean(harmonic_novelty))
            novelty_times = librosa.frames_to_time(novelty_peaks, sr=sr, hop_length=self.hop_length)
            
            # Align with beats to find downbeats
            downbeats = []
            for beat_time in beat_times:
                # Find closest harmonic change
                closest_novelty = min(novelty_times, key=lambda x: abs(x - beat_time))
                if abs(closest_novelty - beat_time) < 0.1:  # Within 100ms
                    downbeats.append(beat_time)
            
            return downbeats
            
        except Exception as e:
            logger.warning(f"Downbeat detection failed: {e}")
            return []
    
    def _calculate_beat_confidence(self, beat_time: float, onset_times: np.ndarray) -> float:
        """Calculate confidence that a beat is correctly placed."""
        if len(onset_times) == 0:
            return 0.5
        
        # Find closest onset
        closest_onset = min(onset_times, key=lambda x: abs(x - beat_time))
        distance = abs(closest_onset - beat_time)
        
        # Confidence decreases with distance from nearest onset
        confidence = max(0.1, 1.0 - (distance * 10))  # 100ms = 0 confidence
        return confidence
    
    def _detect_tempo_changes(self, y: np.ndarray, sr: int) -> List[Tuple[float, float]]:
        """Detect tempo changes throughout the track."""
        
        # Analyze tempo in sliding windows
        window_duration = 10  # seconds
        hop_duration = 5     # seconds
        
        tempo_changes = []
        duration = len(y) / sr
        
        prev_tempo = None
        
        for start_time in np.arange(0, duration - window_duration, hop_duration):
            # Extract window
            start_sample = int(start_time * sr)
            end_sample = int((start_time + window_duration) * sr)
            window = y[start_sample:end_sample]
            
            # Estimate tempo for this window
            tempo, _ = librosa.beat.beat_track(y=window, sr=sr)
            
            # Check for significant tempo change
            if prev_tempo is not None:
                tempo_ratio = tempo / prev_tempo
                if tempo_ratio < (1 - self.tempo_tolerance) or tempo_ratio > (1 + self.tempo_tolerance):
                    tempo_changes.append((start_time, float(tempo)))
            
            prev_tempo = tempo
        
        return tempo_changes
    
    def _detect_musical_sections(self, y: np.ndarray, sr: int) -> List[Dict]:
        """Detect musical sections (verse, chorus, etc.)."""
        
        # Use structural segmentation
        try:
            # Compute chroma and MFCC features
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=self.hop_length)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=self.hop_length, n_mfcc=13)
            
            # Combine features
            features = np.vstack([chroma, mfcc])
            
            # Use recurrence matrix for structure detection
            R = librosa.segment.recurrence_matrix(features, mode='affinity')
            
            # Find segment boundaries
            boundaries = librosa.segment.agglomerative(features, k=8)  # Assume max 8 sections
            boundary_times = librosa.frames_to_time(boundaries, sr=sr, hop_length=self.hop_length)
            
            # Label sections
            sections = []
            section_labels = ['intro', 'verse', 'chorus', 'verse', 'chorus', 'bridge', 'chorus', 'outro']
            
            for i, (start_time, end_time) in enumerate(zip(boundary_times[:-1], boundary_times[1:])):
                label = section_labels[i] if i < len(section_labels) else 'section'
                
                sections.append({
                    'label': label,
                    'start_time': float(start_time),
                    'end_time': float(end_time),
                    'duration': float(end_time - start_time)
                })
            
            return sections
            
        except Exception as e:
            logger.warning(f"Section detection failed: {e}")
            return []
    
    def _analyze_energy_profile(self, y: np.ndarray, sr: int) -> List[Tuple[float, float]]:
        """Analyze energy levels throughout the track."""
        
        # Calculate RMS energy
        hop_length = self.hop_length * 4  # Lower time resolution
        rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
        
        # Smooth the energy curve
        from scipy.ndimage import gaussian_filter1d
        smoothed_rms = gaussian_filter1d(rms, sigma=2)
        
        energy_profile = [(float(t), float(e)) for t, e in zip(times, smoothed_rms)]
        return energy_profile
    
    def _detect_key_changes(self, y: np.ndarray, sr: int) -> List[Tuple[float, str]]:
        """Detect key changes in the music."""
        
        try:
            # Use chroma features for key detection
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=self.hop_length)
            
            # Key detection using template matching
            key_changes = []
            window_size = sr // self.hop_length * 10  # 10 second windows
            
            prev_key = None
            for i in range(0, chroma.shape[1] - window_size, window_size // 2):
                window_chroma = chroma[:, i:i + window_size]
                
                # Simple key detection (could be improved with proper key detection algorithms)
                key_profile = np.mean(window_chroma, axis=1)
                detected_key = self._estimate_key_from_chroma(key_profile)
                
                if prev_key is not None and detected_key != prev_key:
                    timestamp = librosa.frames_to_time(i, sr=sr, hop_length=self.hop_length)
                    key_changes.append((float(timestamp), detected_key))
                
                prev_key = detected_key
            
            return key_changes
            
        except Exception as e:
            logger.warning(f"Key detection failed: {e}")
            return []
    
    def _estimate_key_from_chroma(self, chroma_profile: np.ndarray) -> str:
        """Estimate musical key from chroma profile."""
        # Simplified key detection - in production use proper key detection
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        strongest_chroma = np.argmax(chroma_profile)
        return keys[strongest_chroma]
    
    def generate_music_sync_cuts(self, 
                                music_structure: MusicalStructure,
                                beat_info: List[BeatInfo],
                                cut_preferences: Dict = None) -> List[Dict]:
        """
        Generate cut suggestions synchronized to musical elements.
        
        Args:
            music_structure: Analyzed musical structure
            beat_info: Detected beat information
            cut_preferences: User preferences for music sync
            
        Returns:
            List of music-synchronized cut suggestions
        """
        
        preferences = cut_preferences or {
            'sync_to_beats': True,
            'prefer_downbeats': True,
            'section_boundaries': True,
            'energy_changes': True,
            'min_confidence': 0.7
        }
        
        cuts = []
        
        # Cuts at section boundaries
        if preferences.get('section_boundaries'):
            for section in music_structure.sections:
                cuts.append({
                    'timestamp': section['start_time'],
                    'confidence': 0.9,
                    'reason': f"Musical section change: {section['label']}",
                    'type': 'music_section',
                    'sync_type': 'section_boundary'
                })
        
        # Cuts at strong beats
        if preferences.get('sync_to_beats'):
            for beat in beat_info:
                if beat.confidence >= preferences.get('min_confidence', 0.7):
                    # Prefer downbeats
                    confidence_boost = 0.2 if (beat.beat_type == 'downbeat' and preferences.get('prefer_downbeats')) else 0
                    
                    cuts.append({
                        'timestamp': beat.timestamp,
                        'confidence': min(1.0, beat.confidence + confidence_boost),
                        'reason': f"{beat.beat_type} (strength: {beat.strength:.2f})",
                        'type': 'music_beat',
                        'sync_type': beat.beat_type,
                        'beat_strength': beat.strength
                    })
        
        # Cuts at energy changes
        if preferences.get('energy_changes'):
            energy_cuts = self._detect_energy_changes(music_structure.energy_profile)
            cuts.extend(energy_cuts)
        
        # Cuts at tempo changes
        for timestamp, new_tempo in music_structure.tempo_changes:
            cuts.append({
                'timestamp': timestamp,
                'confidence': 0.8,
                'reason': f"Tempo change to {new_tempo:.1f} BPM",
                'type': 'music_tempo',
                'sync_type': 'tempo_change',
                'new_tempo': new_tempo
            })
        
        # Sort by timestamp and remove duplicates
        cuts = sorted(cuts, key=lambda x: x['timestamp'])
        cuts = self._remove_duplicate_cuts(cuts, tolerance=0.5)  # 500ms tolerance
        
        return cuts
    
    def _detect_energy_changes(self, energy_profile: List[Tuple[float, float]]) -> List[Dict]:
        """Detect significant energy changes for cut suggestions."""
        
        if len(energy_profile) < 3:
            return []
        
        cuts = []
        times, energies = zip(*energy_profile)
        energies = np.array(energies)
        
        # Find significant energy changes
        energy_diff = np.diff(energies)
        
        # Find peaks and valleys in energy changes
        peaks, _ = find_peaks(np.abs(energy_diff), height=np.std(energy_diff))
        
        for peak_idx in peaks:
            if peak_idx < len(times) - 1:
                timestamp = times[peak_idx + 1]
                energy_change = energy_diff[peak_idx]
                
                change_type = "energy_increase" if energy_change > 0 else "energy_decrease"
                confidence = min(1.0, abs(energy_change) / np.max(np.abs(energy_diff)))
                
                cuts.append({
                    'timestamp': timestamp,
                    'confidence': confidence,
                    'reason': f"Musical {change_type}",
                    'type': 'music_energy',
                    'sync_type': change_type,
                    'energy_delta': float(energy_change)
                })
        
        return cuts
    
    def _remove_duplicate_cuts(self, cuts: List[Dict], tolerance: float = 0.5) -> List[Dict]:
        """Remove cuts that are too close together."""
        
        if not cuts:
            return cuts
        
        filtered_cuts = [cuts[0]]
        
        for cut in cuts[1:]:
            # Check if this cut is too close to any existing cut
            too_close = any(
                abs(cut['timestamp'] - existing['timestamp']) < tolerance
                for existing in filtered_cuts
            )
            
            if not too_close:
                filtered_cuts.append(cut)
            else:
                # Keep the cut with higher confidence
                for i, existing in enumerate(filtered_cuts):
                    if abs(cut['timestamp'] - existing['timestamp']) < tolerance:
                        if cut['confidence'] > existing['confidence']:
                            filtered_cuts[i] = cut
                        break
        
        return filtered_cuts
    
    def create_beat_visualization(self, beat_info: List[BeatInfo], duration: float) -> Dict:
        """Create visualization data for beat timeline."""
        
        return {
            'beats': [
                {
                    'time': beat.timestamp,
                    'strength': beat.strength,
                    'type': beat.beat_type,
                    'confidence': beat.confidence
                }
                for beat in beat_info
            ],
            'duration': duration,
            'tempo_average': np.mean([beat.tempo for beat in beat_info]) if beat_info else 0
        }
    
    def export_music_sync_data(self, 
                              music_structure: MusicalStructure,
                              beat_info: List[BeatInfo],
                              output_path: str) -> str:
        """Export detailed music synchronization data."""
        
        sync_data = {
            'musical_structure': {
                'sections': music_structure.sections,
                'tempo_changes': [(t, float(tempo)) for t, tempo in music_structure.tempo_changes],
                'key_changes': music_structure.key_changes,
                'energy_profile': music_structure.energy_profile
            },
            'beats': [
                {
                    'timestamp': beat.timestamp,
                    'confidence': beat.confidence,
                    'strength': beat.strength,
                    'tempo': beat.tempo,
                    'type': beat.beat_type
                }
                for beat in beat_info
            ],
            'metadata': {
                'total_beats': len(beat_info),
                'average_tempo': np.mean([beat.tempo for beat in beat_info]) if beat_info else 0,
                'sections_detected': len(music_structure.sections),
                'tempo_changes': len(music_structure.tempo_changes)
            }
        }
        
        import json
        with open(output_path, 'w') as f:
            json.dump(sync_data, f, indent=2)
        
        return output_path
