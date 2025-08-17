"""
Audio Analysis API using HuggingFace models and Librosa
"""
import os
import librosa
import numpy as np
import whisper
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import torch

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from transformers import pipeline, Wav2Vec2Processor, Wav2Vec2ForCTC

from ..core.config import settings
from ..core.logging_config import get_logger

router = APIRouter()
logger = get_logger("audio_analysis")

# Global model cache
audio_models = {}


def load_whisper_model(model_size: str = "base"):
    """Load Whisper model for speech recognition"""
    if f"whisper_{model_size}" not in audio_models:
        try:
            logger.info(f"Loading Whisper {model_size} model...")
            model = whisper.load_model(model_size)
            audio_models[f"whisper_{model_size}"] = model
            logger.info(f"Whisper {model_size} model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            raise
    return audio_models[f"whisper_{model_size}"]


def load_wav2vec2_model():
    """Load Wav2Vec2 model for speech recognition"""
    if "wav2vec2" not in audio_models:
        try:
            logger.info("Loading Wav2Vec2 model...")
            processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
            model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
            audio_models["wav2vec2"] = {"processor": processor, "model": model}
            logger.info("Wav2Vec2 model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Wav2Vec2 model: {str(e)}")
            # Fallback to Whisper
            audio_models["wav2vec2"] = None
    return audio_models["wav2vec2"]


def load_speaker_diarization_model():
    """Load speaker diarization model"""
    if "speaker_diarization" not in audio_models:
        try:
            logger.info("Loading speaker diarization model...")
            # Using pyannote.audio for speaker diarization
            # Note: This requires additional setup and authentication
            audio_models["speaker_diarization"] = None  # Placeholder
            logger.info("Speaker diarization model loaded")
        except Exception as e:
            logger.error(f"Error loading speaker diarization model: {str(e)}")
            audio_models["speaker_diarization"] = None
    return audio_models["speaker_diarization"]


def extract_audio_features(audio_path: str, sr: int = 22050) -> Dict:
    """Extract comprehensive audio features"""
    try:
        # Load audio file
        y, sr = librosa.load(audio_path, sr=sr)
        duration = len(y) / sr
        
        # Basic features
        features = {
            "duration": duration,
            "sample_rate": sr,
            "total_samples": len(y)
        }
        
        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        features["spectral_centroid"] = {
            "mean": float(np.mean(spectral_centroids)),
            "std": float(np.std(spectral_centroids)),
            "min": float(np.min(spectral_centroids)),
            "max": float(np.max(spectral_centroids))
        }
        
        # Spectral rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        features["spectral_rolloff"] = {
            "mean": float(np.mean(spectral_rolloff)),
            "std": float(np.std(spectral_rolloff))
        }
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        features["zero_crossing_rate"] = {
            "mean": float(np.mean(zcr)),
            "std": float(np.std(zcr))
        }
        
        # MFCCs (Mel-frequency cepstral coefficients)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        features["mfccs"] = {
            f"mfcc_{i}": {
                "mean": float(np.mean(mfccs[i])),
                "std": float(np.std(mfccs[i]))
            }
            for i in range(13)
        }
        
        # Chroma features
        chroma = librosa.feature.chroma(y=y, sr=sr)
        features["chroma"] = {
            "mean": float(np.mean(chroma)),
            "std": float(np.std(chroma))
        }
        
        # Tempo and beat tracking
        try:
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            features["tempo"] = float(tempo)
            features["beats"] = {
                "count": len(beats),
                "intervals": [float(beat / sr) for beat in beats[:10]]  # First 10 beats
            }
        except Exception as e:
            logger.warning(f"Error extracting tempo: {str(e)}")
            features["tempo"] = 0
            features["beats"] = {"count": 0, "intervals": []}
        
        # RMS Energy
        rms = librosa.feature.rms(y=y)[0]
        features["rms_energy"] = {
            "mean": float(np.mean(rms)),
            "std": float(np.std(rms)),
            "max": float(np.max(rms))
        }
        
        # Spectral bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        features["spectral_bandwidth"] = {
            "mean": float(np.mean(spectral_bandwidth)),
            "std": float(np.std(spectral_bandwidth))
        }
        
        return features
        
    except Exception as e:
        logger.error(f"Error extracting audio features: {str(e)}")
        raise


def transcribe_audio_whisper(audio_path: str, model_size: str = "base") -> Dict:
    """Transcribe audio using Whisper"""
    try:
        model = load_whisper_model(model_size)
        
        logger.info(f"Transcribing audio with Whisper {model_size}...")
        result = model.transcribe(audio_path)
        
        # Process segments
        segments = []
        for segment in result.get("segments", []):
            segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
                "confidence": segment.get("no_speech_prob", 0.0)
            })
        
        return {
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "segments": segments,
            "word_count": len(result["text"].split()),
            "duration": segments[-1]["end"] if segments else 0
        }
        
    except Exception as e:
        logger.error(f"Error transcribing audio with Whisper: {str(e)}")
        raise


def transcribe_audio_wav2vec2(audio_path: str) -> Dict:
    """Transcribe audio using Wav2Vec2"""
    try:
        model_data = load_wav2vec2_model()
        
        if model_data is None:
            logger.warning("Wav2Vec2 not available, falling back to Whisper")
            return transcribe_audio_whisper(audio_path)
        
        processor = model_data["processor"]
        model = model_data["model"]
        
        # Load and preprocess audio
        audio, sr = librosa.load(audio_path, sr=16000)
        
        # Process audio in chunks (Wav2Vec2 has input length limitations)
        chunk_duration = 30  # seconds
        chunk_samples = chunk_duration * sr
        
        transcriptions = []
        
        for i in range(0, len(audio), chunk_samples):
            chunk = audio[i:i + chunk_samples]
            
            # Prepare input
            input_values = processor(chunk, sampling_rate=sr, return_tensors="pt").input_values
            
            # Generate prediction
            with torch.no_grad():
                logits = model(input_values).logits
            
            # Decode prediction
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = processor.decode(predicted_ids[0])
            
            start_time = i / sr
            end_time = min((i + len(chunk)) / sr, len(audio) / sr)
            
            if transcription.strip():
                transcriptions.append({
                    "start": start_time,
                    "end": end_time,
                    "text": transcription.strip()
                })
        
        # Combine transcriptions
        full_text = " ".join([t["text"] for t in transcriptions])
        
        return {
            "text": full_text,
            "segments": transcriptions,
            "word_count": len(full_text.split()),
            "duration": len(audio) / sr
        }
        
    except Exception as e:
        logger.error(f"Error transcribing audio with Wav2Vec2: {str(e)}")
        # Fallback to Whisper
        return transcribe_audio_whisper(audio_path)


def analyze_speech_quality(audio_path: str) -> Dict:
    """Analyze speech quality metrics"""
    try:
        # Load audio
        y, sr = librosa.load(audio_path, sr=22050)
        
        # Voice Activity Detection (simple energy-based)
        frame_length = int(0.025 * sr)  # 25ms frames
        hop_length = int(0.010 * sr)    # 10ms hop
        
        # Calculate frame energy
        frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
        frame_energies = np.sum(frames ** 2, axis=0)
        
        # Threshold for voice activity (adaptive)
        energy_threshold = np.percentile(frame_energies, 30)
        voice_frames = frame_energies > energy_threshold
        
        # Speech metrics
        speech_ratio = np.sum(voice_frames) / len(voice_frames)
        
        # Signal-to-noise ratio estimation
        noise_frames = frame_energies <= energy_threshold
        if np.sum(noise_frames) > 0:
            signal_energy = np.mean(frame_energies[voice_frames]) if np.sum(voice_frames) > 0 else 0
            noise_energy = np.mean(frame_energies[noise_frames])
            snr = 10 * np.log10(signal_energy / noise_energy) if noise_energy > 0 else float('inf')
        else:
            snr = float('inf')
        
        # Pitch analysis
        try:
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = []
            
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if pitch_values:
                pitch_stats = {
                    "mean": float(np.mean(pitch_values)),
                    "std": float(np.std(pitch_values)),
                    "min": float(np.min(pitch_values)),
                    "max": float(np.max(pitch_values))
                }
            else:
                pitch_stats = {"mean": 0, "std": 0, "min": 0, "max": 0}
                
        except Exception as e:
            logger.warning(f"Error analyzing pitch: {str(e)}")
            pitch_stats = {"mean": 0, "std": 0, "min": 0, "max": 0}
        
        return {
            "speech_ratio": float(speech_ratio),
            "snr_db": float(snr) if snr != float('inf') else None,
            "pitch_statistics": pitch_stats,
            "voice_frames": int(np.sum(voice_frames)),
            "total_frames": len(voice_frames),
            "estimated_speech_duration": float(np.sum(voice_frames) * hop_length / sr)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing speech quality: {str(e)}")
        raise


def detect_silence_and_pauses(audio_path: str, silence_threshold: float = 0.01) -> List[Dict]:
    """Detect silence and pause segments in audio"""
    try:
        # Load audio
        y, sr = librosa.load(audio_path, sr=22050)
        
        # Calculate RMS energy
        frame_length = int(0.025 * sr)  # 25ms
        hop_length = int(0.010 * sr)    # 10ms
        
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Detect silence frames
        silence_frames = rms < silence_threshold
        
        # Find silence segments
        silence_segments = []
        in_silence = False
        silence_start = 0
        
        for i, is_silent in enumerate(silence_frames):
            time = i * hop_length / sr
            
            if is_silent and not in_silence:
                # Start of silence
                in_silence = True
                silence_start = time
            elif not is_silent and in_silence:
                # End of silence
                in_silence = False
                duration = time - silence_start
                
                if duration > 0.1:  # Only include silences longer than 100ms
                    silence_segments.append({
                        "start": silence_start,
                        "end": time,
                        "duration": duration,
                        "type": "pause" if duration < 2.0 else "silence"
                    })
        
        # Handle case where audio ends in silence
        if in_silence:
            final_time = len(y) / sr
            duration = final_time - silence_start
            if duration > 0.1:
                silence_segments.append({
                    "start": silence_start,
                    "end": final_time,
                    "duration": duration,
                    "type": "pause" if duration < 2.0 else "silence"
                })
        
        return silence_segments
        
    except Exception as e:
        logger.error(f"Error detecting silence: {str(e)}")
        return []


@router.post("/analyze")
async def analyze_audio_comprehensive(
    filename: str,
    transcribe: bool = True,
    extract_features: bool = True,
    quality_analysis: bool = True,
    silence_detection: bool = True,
    model: str = "whisper"
):
    """
    Comprehensive audio analysis
    
    - **filename**: Name of uploaded audio file
    - **transcribe**: Enable speech-to-text transcription
    - **extract_features**: Extract audio features (MFCCs, spectral features, etc.)
    - **quality_analysis**: Analyze speech quality metrics
    - **silence_detection**: Detect silence and pause segments
    - **model**: Transcription model ("whisper" or "wav2vec2")
    """
    
    audio_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        logger.info(f"Starting comprehensive audio analysis for: {filename}")
        start_time = datetime.now()
        
        results = {
            "filename": filename,
            "analysis_timestamp": start_time.isoformat(),
            "parameters": {
                "transcribe": transcribe,
                "extract_features": extract_features,
                "quality_analysis": quality_analysis,
                "silence_detection": silence_detection,
                "model": model
            }
        }
        
        # Transcription
        if transcribe:
            logger.info("Transcribing audio...")
            try:
                if model == "whisper":
                    transcription = transcribe_audio_whisper(audio_path)
                elif model == "wav2vec2":
                    transcription = transcribe_audio_wav2vec2(audio_path)
                else:
                    transcription = transcribe_audio_whisper(audio_path)  # Default fallback
                
                results["transcription"] = transcription
                
            except Exception as e:
                logger.error(f"Error in transcription: {str(e)}")
                results["transcription_error"] = str(e)
        
        # Feature extraction
        if extract_features:
            logger.info("Extracting audio features...")
            try:
                features = extract_audio_features(audio_path)
                results["features"] = features
                
            except Exception as e:
                logger.error(f"Error extracting features: {str(e)}")
                results["features_error"] = str(e)
        
        # Quality analysis
        if quality_analysis:
            logger.info("Analyzing speech quality...")
            try:
                quality = analyze_speech_quality(audio_path)
                results["quality"] = quality
                
            except Exception as e:
                logger.error(f"Error in quality analysis: {str(e)}")
                results["quality_error"] = str(e)
        
        # Silence detection
        if silence_detection:
            logger.info("Detecting silence and pauses...")
            try:
                silence_segments = detect_silence_and_pauses(audio_path)
                results["silence_analysis"] = {
                    "segments": silence_segments,
                    "total_silence_duration": sum(s["duration"] for s in silence_segments),
                    "pause_count": len([s for s in silence_segments if s["type"] == "pause"]),
                    "silence_count": len([s for s in silence_segments if s["type"] == "silence"])
                }
                
            except Exception as e:
                logger.error(f"Error in silence detection: {str(e)}")
                results["silence_error"] = str(e)
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        results["processing_time"] = processing_time
        
        logger.info(f"Audio analysis completed in {processing_time:.2f}s")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Audio analysis completed successfully",
                "data": results
            }
        )
        
    except Exception as e:
        logger.error(f"Error analyzing audio {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing audio: {str(e)}")


@router.post("/transcribe")
async def transcribe_audio_endpoint(
    filename: str,
    model: str = "whisper",
    model_size: str = "base"
):
    """
    Transcribe audio to text
    
    - **filename**: Name of uploaded audio file
    - **model**: Model to use ("whisper" or "wav2vec2")
    - **model_size**: Size of Whisper model ("tiny", "base", "small", "medium", "large")
    """
    
    audio_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        logger.info(f"Transcribing audio: {filename} with {model}")
        start_time = datetime.now()
        
        if model == "whisper":
            transcription = transcribe_audio_whisper(audio_path, model_size)
        elif model == "wav2vec2":
            transcription = transcribe_audio_wav2vec2(audio_path)
        else:
            raise HTTPException(status_code=400, detail="Invalid model. Use 'whisper' or 'wav2vec2'")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Transcription completed successfully",
                "data": {
                    "filename": filename,
                    "model": model,
                    "model_size": model_size if model == "whisper" else None,
                    "transcription": transcription,
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error transcribing {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")


@router.post("/quality")
async def analyze_audio_quality(filename: str):
    """
    Analyze audio quality metrics
    
    - **filename**: Name of uploaded audio file
    """
    
    audio_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        logger.info(f"Analyzing audio quality for: {filename}")
        
        quality_metrics = analyze_speech_quality(audio_path)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Audio quality analysis completed",
                "data": {
                    "filename": filename,
                    "quality_metrics": quality_metrics,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error analyzing audio quality for {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing audio quality: {str(e)}")


@router.post("/enhance")
async def enhance_audio(
    filename: str,
    noise_reduction: bool = True,
    normalize: bool = True,
    output_format: str = "wav"
):
    """
    Enhance audio quality (noise reduction, normalization)
    
    - **filename**: Name of uploaded audio file
    - **noise_reduction**: Apply noise reduction
    - **normalize**: Normalize audio levels
    - **output_format**: Output format ("wav", "mp3", "flac")
    """
    
    audio_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        logger.info(f"Enhancing audio: {filename}")
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        
        # Apply enhancements
        enhanced_audio = y.copy()
        
        if noise_reduction:
            # Simple noise reduction using spectral gating
            stft = librosa.stft(enhanced_audio)
            magnitude = np.abs(stft)
            
            # Estimate noise floor
            noise_floor = np.percentile(magnitude, 10)
            
            # Apply spectral gating
            mask = magnitude > (noise_floor * 2)
            stft_clean = stft * mask
            
            enhanced_audio = librosa.istft(stft_clean)
        
        if normalize:
            # Normalize to [-1, 1] range
            max_val = np.max(np.abs(enhanced_audio))
            if max_val > 0:
                enhanced_audio = enhanced_audio / max_val * 0.95
        
        # Save enhanced audio
        output_filename = f"enhanced_{filename}"
        output_path = os.path.join(settings.PROCESSED_DIR, output_filename)
        
        # Ensure processed directory exists
        os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
        
        # Save based on format
        if output_format.lower() == "wav":
            import soundfile as sf
            sf.write(output_path, enhanced_audio, sr)
        else:
            # For other formats, we'd need additional libraries like pydub
            import soundfile as sf
            sf.write(output_path.replace(f".{output_format}", ".wav"), enhanced_audio, sr)
            output_filename = output_filename.replace(f".{output_format}", ".wav")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Audio enhancement completed",
                "data": {
                    "original_filename": filename,
                    "enhanced_filename": output_filename,
                    "enhancements_applied": {
                        "noise_reduction": noise_reduction,
                        "normalize": normalize
                    },
                    "output_format": "wav",  # Currently only WAV supported
                    "file_path": output_path,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error enhancing audio {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error enhancing audio: {str(e)}")
