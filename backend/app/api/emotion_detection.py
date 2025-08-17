"""
Emotion Detection API using HuggingFace models
"""
import os
import cv2
import torch
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from transformers import (
    pipeline, AutoTokenizer, AutoModelForSequenceClassification,
    AutoProcessor, AutoModel
)
import librosa

from ..core.config import settings
from ..core.logging_config import get_logger

router = APIRouter()
logger = get_logger("emotion_detection")

# Global model cache
emotion_models = {}


def load_text_emotion_model():
    """Load text emotion classification model"""
    if "text_emotion" not in emotion_models:
        try:
            logger.info("Loading text emotion model...")
            emotion_pipeline = pipeline(
                "text-classification",
                model="cardiffnlp/twitter-roberta-base-emotion",
                device=0 if settings.DEVICE == "cuda" else -1
            )
            emotion_models["text_emotion"] = emotion_pipeline
            logger.info("Text emotion model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading text emotion model: {str(e)}")
            # Fallback to a simpler model
            emotion_pipeline = pipeline("sentiment-analysis")
            emotion_models["text_emotion"] = emotion_pipeline
    return emotion_models["text_emotion"]


def load_audio_emotion_model():
    """Load audio emotion classification model"""
    if "audio_emotion" not in emotion_models:
        try:
            logger.info("Loading audio emotion model...")
            # Using a general audio classification model
            # In production, you'd use a specialized emotion detection model
            emotion_pipeline = pipeline(
                "audio-classification",
                model="superb/wav2vec2-base-superb-er",
                device=0 if settings.DEVICE == "cuda" else -1
            )
            emotion_models["audio_emotion"] = emotion_pipeline
            logger.info("Audio emotion model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading audio emotion model: {str(e)}")
            # Create a placeholder
            emotion_models["audio_emotion"] = None
    return emotion_models["audio_emotion"]


def load_facial_emotion_model():
    """Load facial emotion detection model"""
    if "facial_emotion" not in emotion_models:
        try:
            logger.info("Loading facial emotion model...")
            # Using a general image classification model
            # In production, you'd use FER2013 or other emotion-specific models
            emotion_pipeline = pipeline(
                "image-classification",
                model="trpakov/vit-face-expression",
                device=0 if settings.DEVICE == "cuda" else -1
            )
            emotion_models["facial_emotion"] = emotion_pipeline
            logger.info("Facial emotion model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading facial emotion model: {str(e)}")
            # Fallback to general image classification
            emotion_pipeline = pipeline("image-classification")
            emotion_models["facial_emotion"] = emotion_pipeline
    return emotion_models["facial_emotion"]


def extract_audio_from_video(video_path: str, output_path: str = None) -> str:
    """Extract audio from video file"""
    try:
        import moviepy.editor as mp
        
        if output_path is None:
            output_path = video_path.replace(Path(video_path).suffix, "_audio.wav")
        
        # Load video and extract audio
        video = mp.VideoFileClip(video_path)
        audio = video.audio
        
        if audio is None:
            raise ValueError("No audio track found in video")
        
        # Save audio as WAV file
        audio.write_audiofile(output_path, verbose=False, logger=None)
        audio.close()
        video.close()
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error extracting audio from {video_path}: {str(e)}")
        raise


def analyze_audio_emotion(audio_path: str, chunk_duration: int = 30) -> List[Dict]:
    """Analyze emotion in audio using chunks"""
    try:
        emotion_model = load_audio_emotion_model()
        
        if emotion_model is None:
            logger.warning("Audio emotion model not available, using fallback analysis")
            return analyze_audio_emotion_fallback(audio_path, chunk_duration)
        
        # Load audio file
        audio, sr = librosa.load(audio_path, sr=16000)
        duration = len(audio) / sr
        
        # Split into chunks
        chunk_samples = chunk_duration * sr
        chunks = []
        
        for i in range(0, len(audio), chunk_samples):
            chunk = audio[i:i + chunk_samples]
            if len(chunk) > sr:  # At least 1 second
                chunks.append(chunk)
        
        # Analyze each chunk
        emotions = []
        for i, chunk in enumerate(chunks):
            try:
                # Convert to the format expected by the model
                chunk_normalized = chunk / np.max(np.abs(chunk)) if np.max(np.abs(chunk)) > 0 else chunk
                
                # Run emotion detection
                result = emotion_model(chunk_normalized, sampling_rate=16000)
                
                timestamp = i * chunk_duration
                emotions.append({
                    "timestamp": timestamp,
                    "duration": min(chunk_duration, duration - timestamp),
                    "emotions": result
                })
                
            except Exception as e:
                logger.warning(f"Error analyzing audio chunk {i}: {str(e)}")
                continue
        
        return emotions
        
    except Exception as e:
        logger.error(f"Error analyzing audio emotion: {str(e)}")
        return []


def analyze_audio_emotion_fallback(audio_path: str, chunk_duration: int = 30) -> List[Dict]:
    """Fallback audio emotion analysis using basic features"""
    try:
        # Load audio
        audio, sr = librosa.load(audio_path, sr=16000)
        duration = len(audio) / sr
        
        # Split into chunks
        chunk_samples = chunk_duration * sr
        emotions = []
        
        for i in range(0, len(audio), chunk_samples):
            chunk = audio[i:i + chunk_samples]
            if len(chunk) < sr:  # Skip chunks less than 1 second
                continue
            
            # Extract basic audio features
            mfccs = librosa.feature.mfcc(y=chunk, sr=sr, n_mfcc=13)
            chroma = librosa.feature.chroma(y=chunk, sr=sr)
            spectral_centroid = librosa.feature.spectral_centroid(y=chunk, sr=sr)
            
            # Calculate energy and tempo
            energy = np.mean(chunk ** 2)
            tempo, _ = librosa.beat.beat_track(y=chunk, sr=sr)
            
            # Simple heuristic emotion classification
            emotion_scores = []
            
            # High energy + high tempo = excitement/joy
            if energy > 0.01 and tempo > 120:
                emotion_scores.append({"label": "joy", "score": 0.7})
                emotion_scores.append({"label": "excitement", "score": 0.6})
            
            # Low energy + low tempo = sadness/calm
            elif energy < 0.005 and tempo < 80:
                emotion_scores.append({"label": "sadness", "score": 0.6})
                emotion_scores.append({"label": "calm", "score": 0.5})
            
            # Medium values = neutral
            else:
                emotion_scores.append({"label": "neutral", "score": 0.5})
            
            timestamp = i * chunk_duration / len(audio) * duration
            emotions.append({
                "timestamp": timestamp,
                "duration": min(chunk_duration, duration - timestamp),
                "emotions": emotion_scores,
                "features": {
                    "energy": float(energy),
                    "tempo": float(tempo),
                    "spectral_centroid": float(np.mean(spectral_centroid))
                }
            })
        
        return emotions
        
    except Exception as e:
        logger.error(f"Error in fallback audio emotion analysis: {str(e)}")
        return []


def detect_faces_and_emotions(frame: np.ndarray) -> List[Dict]:
    """Detect faces and analyze emotions in a frame"""
    try:
        # Load face detection cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return []
        
        # Load emotion model
        emotion_model = load_facial_emotion_model()
        
        face_emotions = []
        
        for (x, y, w, h) in faces:
            # Extract face region
            face_roi = frame[y:y+h, x:x+w]
            
            # Resize face for emotion analysis
            face_resized = cv2.resize(face_roi, (224, 224))
            
            try:
                # Convert to PIL Image
                from PIL import Image
                face_image = Image.fromarray(face_resized)
                
                # Run emotion detection
                emotions = emotion_model(face_image)
                
                face_emotions.append({
                    "bbox": [int(x), int(y), int(w), int(h)],
                    "emotions": emotions,
                    "face_size": w * h
                })
                
            except Exception as e:
                logger.warning(f"Error analyzing face emotion: {str(e)}")
                continue
        
        return face_emotions
        
    except Exception as e:
        logger.error(f"Error detecting faces and emotions: {str(e)}")
        return []


def analyze_text_emotion(text: str) -> List[Dict]:
    """Analyze emotion in text"""
    try:
        emotion_model = load_text_emotion_model()
        
        # Split text into sentences for better analysis
        sentences = text.split('.')
        sentence_emotions = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Skip very short sentences
                try:
                    emotions = emotion_model(sentence)
                    sentence_emotions.append({
                        "text": sentence,
                        "emotions": emotions
                    })
                except Exception as e:
                    logger.warning(f"Error analyzing sentence emotion: {str(e)}")
                    continue
        
        # Overall text emotion
        if sentence_emotions:
            overall_emotions = emotion_model(text)
        else:
            overall_emotions = []
        
        return {
            "overall_emotions": overall_emotions,
            "sentence_emotions": sentence_emotions
        }
        
    except Exception as e:
        logger.error(f"Error analyzing text emotion: {str(e)}")
        return {"overall_emotions": [], "sentence_emotions": []}


@router.post("/video")
async def analyze_video_emotions(
    filename: str,
    analyze_audio: bool = True,
    analyze_visual: bool = True,
    max_frames: int = 20
):
    """
    Comprehensive emotion analysis for video (audio + visual)
    
    - **filename**: Name of uploaded video file
    - **analyze_audio**: Enable audio emotion analysis
    - **analyze_visual**: Enable visual/facial emotion analysis
    - **max_frames**: Maximum frames to analyze for facial emotions
    """
    
    video_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    try:
        logger.info(f"Starting emotion analysis for video: {filename}")
        start_time = datetime.now()
        
        results = {
            "filename": filename,
            "analysis_timestamp": start_time.isoformat(),
            "parameters": {
                "analyze_audio": analyze_audio,
                "analyze_visual": analyze_visual,
                "max_frames": max_frames
            }
        }
        
        # Audio emotion analysis
        if analyze_audio:
            logger.info("Analyzing audio emotions...")
            try:
                # Extract audio from video
                audio_path = extract_audio_from_video(video_path)
                
                # Analyze audio emotions
                audio_emotions = analyze_audio_emotion(audio_path, chunk_duration=30)
                results["audio_emotions"] = audio_emotions
                
                # Clean up temporary audio file
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    
            except Exception as e:
                logger.error(f"Error in audio emotion analysis: {str(e)}")
                results["audio_emotions"] = []
                results["audio_error"] = str(e)
        
        # Visual emotion analysis
        if analyze_visual:
            logger.info("Analyzing visual emotions...")
            try:
                # Extract frames from video
                cap = cv2.VideoCapture(video_path)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                # Calculate frame extraction interval
                interval = max(1, total_frames // max_frames)
                
                visual_emotions = []
                frame_count = 0
                
                while cap.isOpened() and len(visual_emotions) < max_frames:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    if frame_count % interval == 0:
                        # Convert BGR to RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        
                        # Detect faces and emotions
                        face_emotions = detect_faces_and_emotions(frame_rgb)
                        
                        timestamp = frame_count / fps if fps > 0 else 0
                        
                        visual_emotions.append({
                            "frame_index": frame_count,
                            "timestamp": timestamp,
                            "faces": face_emotions,
                            "face_count": len(face_emotions)
                        })
                    
                    frame_count += 1
                
                cap.release()
                results["visual_emotions"] = visual_emotions
                
            except Exception as e:
                logger.error(f"Error in visual emotion analysis: {str(e)}")
                results["visual_emotions"] = []
                results["visual_error"] = str(e)
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        results["processing_time"] = processing_time
        
        # Generate emotion summary
        emotion_summary = generate_emotion_summary(results)
        results["summary"] = emotion_summary
        
        logger.info(f"Emotion analysis completed in {processing_time:.2f}s")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Emotion analysis completed successfully",
                "data": results
            }
        )
        
    except Exception as e:
        logger.error(f"Error analyzing emotions for {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing emotions: {str(e)}")


@router.post("/text")
async def analyze_text_emotions(text: str):
    """
    Analyze emotions in text (e.g., script, subtitles)
    
    - **text**: Text content to analyze
    """
    
    if not text or len(text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Text is too short for analysis")
    
    try:
        logger.info("Analyzing text emotions...")
        
        results = analyze_text_emotion(text)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Text emotion analysis completed",
                "data": {
                    "text_length": len(text),
                    "analysis_timestamp": datetime.now().isoformat(),
                    "emotions": results
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error analyzing text emotions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing text emotions: {str(e)}")


@router.post("/audio")
async def analyze_audio_emotions_endpoint(filename: str, chunk_duration: int = 30):
    """
    Analyze emotions in audio file
    
    - **filename**: Name of uploaded audio file
    - **chunk_duration**: Duration of audio chunks to analyze (seconds)
    """
    
    audio_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        logger.info(f"Analyzing audio emotions for: {filename}")
        
        emotions = analyze_audio_emotion(audio_path, chunk_duration)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Audio emotion analysis completed",
                "data": {
                    "filename": filename,
                    "chunk_duration": chunk_duration,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "emotions": emotions,
                    "total_chunks": len(emotions)
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error analyzing audio emotions for {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing audio emotions: {str(e)}")


def generate_emotion_summary(analysis_results: Dict) -> Dict:
    """Generate a summary of emotion analysis results"""
    try:
        summary = {
            "dominant_emotions": [],
            "emotion_timeline": [],
            "overall_sentiment": "neutral",
            "emotion_diversity": 0,
            "confidence": 0
        }
        
        # Analyze audio emotions
        if "audio_emotions" in analysis_results and analysis_results["audio_emotions"]:
            audio_emotions = analysis_results["audio_emotions"]
            
            # Count emotion occurrences
            emotion_counts = {}
            for chunk in audio_emotions:
                for emotion in chunk.get("emotions", []):
                    label = emotion.get("label", "unknown")
                    score = emotion.get("score", 0)
                    
                    if label not in emotion_counts:
                        emotion_counts[label] = {"count": 0, "total_score": 0}
                    emotion_counts[label]["count"] += 1
                    emotion_counts[label]["total_score"] += score
            
            # Calculate average scores
            for emotion in emotion_counts:
                emotion_counts[emotion]["avg_score"] = (
                    emotion_counts[emotion]["total_score"] / emotion_counts[emotion]["count"]
                )
        
        # Analyze visual emotions
        if "visual_emotions" in analysis_results and analysis_results["visual_emotions"]:
            visual_emotions = analysis_results["visual_emotions"]
            
            # Process facial emotions
            face_emotion_counts = {}
            for frame in visual_emotions:
                for face in frame.get("faces", []):
                    for emotion in face.get("emotions", []):
                        label = emotion.get("label", "unknown")
                        score = emotion.get("score", 0)
                        
                        if label not in face_emotion_counts:
                            face_emotion_counts[label] = {"count": 0, "total_score": 0}
                        face_emotion_counts[label]["count"] += 1
                        face_emotion_counts[label]["total_score"] += score
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating emotion summary: {str(e)}")
        return {"error": "Could not generate summary"}
