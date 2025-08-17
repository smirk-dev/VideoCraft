"""
Music Recommendation API using AI models and content analysis
"""
import os
import json
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
import librosa

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from transformers import pipeline

from ..core.config import settings
from ..core.logging_config import get_logger

router = APIRouter()
logger = get_logger("music_recommendation")

# Global model cache
music_models = {}

# Predefined music database (in production, this would be a real database)
MUSIC_DATABASE = {
    "ambient": [
        {"id": 1, "title": "Peaceful Morning", "artist": "Nature Sounds", "duration": 180, "tempo": 60, "energy": 0.2, "valence": 0.7},
        {"id": 2, "title": "Ocean Waves", "artist": "Relaxation Music", "duration": 240, "tempo": 50, "energy": 0.1, "valence": 0.8},
        {"id": 3, "title": "Forest Rain", "artist": "Ambient Collective", "duration": 300, "tempo": 55, "energy": 0.15, "valence": 0.75}
    ],
    "upbeat": [
        {"id": 4, "title": "Summer Vibes", "artist": "Happy Beats", "duration": 210, "tempo": 128, "energy": 0.8, "valence": 0.9},
        {"id": 5, "title": "Energy Boost", "artist": "Electronic Mix", "duration": 195, "tempo": 140, "energy": 0.9, "valence": 0.85},
        {"id": 6, "title": "Feel Good", "artist": "Pop Collective", "duration": 180, "tempo": 120, "energy": 0.7, "valence": 0.9}
    ],
    "dramatic": [
        {"id": 7, "title": "Epic Journey", "artist": "Cinematic Orchestra", "duration": 270, "tempo": 90, "energy": 0.8, "valence": 0.3},
        {"id": 8, "title": "Dark Rising", "artist": "Film Score", "duration": 220, "tempo": 70, "energy": 0.7, "valence": 0.2},
        {"id": 9, "title": "Tension Build", "artist": "Soundtrack Pro", "duration": 150, "tempo": 80, "energy": 0.6, "valence": 0.25}
    ],
    "calm": [
        {"id": 10, "title": "Meditation Flow", "artist": "Zen Masters", "duration": 360, "tempo": 60, "energy": 0.2, "valence": 0.8},
        {"id": 11, "title": "Soft Piano", "artist": "Classical Moods", "duration": 200, "tempo": 65, "energy": 0.3, "valence": 0.7},
        {"id": 12, "title": "Gentle Strings", "artist": "Chamber Music", "duration": 240, "tempo": 70, "energy": 0.25, "valence": 0.75}
    ],
    "energetic": [
        {"id": 13, "title": "Workout Power", "artist": "Fitness Beats", "duration": 180, "tempo": 150, "energy": 0.95, "valence": 0.8},
        {"id": 14, "title": "Rock Anthem", "artist": "Electric Guitar", "duration": 200, "tempo": 130, "energy": 0.9, "valence": 0.7},
        {"id": 15, "title": "Dance Floor", "artist": "EDM Collective", "duration": 220, "tempo": 128, "energy": 0.85, "valence": 0.9}
    ]
}


def load_music_classification_model():
    """Load music genre classification model"""
    if "music_classifier" not in music_models:
        try:
            logger.info("Loading music classification model...")
            # Using a general audio classification model
            # In production, you'd use a music-specific model
            classifier = pipeline(
                "audio-classification",
                model="MIT/ast-finetuned-audioset-10-10-0.4593",
                device=0 if settings.DEVICE == "cuda" else -1
            )
            music_models["music_classifier"] = classifier
            logger.info("Music classification model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading music classification model: {str(e)}")
            music_models["music_classifier"] = None
    return music_models["music_classifier"]


def analyze_video_mood(video_analysis: Dict) -> Dict:
    """Analyze mood from video analysis results"""
    try:
        mood_scores = {
            "energy": 0.5,
            "valence": 0.5,  # Positive/negative sentiment
            "arousal": 0.5,  # Intensity/excitement
            "dominance": 0.5  # Control/power
        }
        
        # Analyze objects detected
        if "object_detection" in video_analysis:
            objects = video_analysis["object_detection"].get("object_summary", {})
            
            # High energy objects
            energetic_objects = ["person", "car", "motorcycle", "bicycle", "sports", "ball"]
            energy_boost = sum(objects.get(obj, 0) for obj in energetic_objects) / 100
            mood_scores["energy"] = min(1.0, mood_scores["energy"] + energy_boost)
            
            # Positive valence objects
            positive_objects = ["person", "dog", "cat", "flower", "food", "cake"]
            valence_boost = sum(objects.get(obj, 0) for obj in positive_objects) / 100
            mood_scores["valence"] = min(1.0, mood_scores["valence"] + valence_boost)
        
        # Analyze scene changes (indicates dynamic content)
        if "scene_changes" in video_analysis:
            change_frequency = video_analysis["scene_changes"].get("change_frequency", 0)
            if change_frequency > 0.1:  # Frequent changes
                mood_scores["arousal"] = min(1.0, mood_scores["arousal"] + 0.3)
                mood_scores["energy"] = min(1.0, mood_scores["energy"] + 0.2)
        
        # Analyze video quality (affects perceived mood)
        if "quality" in video_analysis:
            quality_score = video_analysis["quality"]["quality_metrics"]["quality_score"]
            if quality_score > 70:
                mood_scores["dominance"] = min(1.0, mood_scores["dominance"] + 0.2)
        
        return mood_scores
        
    except Exception as e:
        logger.error(f"Error analyzing video mood: {str(e)}")
        return {"energy": 0.5, "valence": 0.5, "arousal": 0.5, "dominance": 0.5}


def analyze_audio_mood(audio_analysis: Dict) -> Dict:
    """Analyze mood from audio analysis results"""
    try:
        mood_scores = {
            "energy": 0.5,
            "valence": 0.5,
            "arousal": 0.5,
            "dominance": 0.5
        }
        
        # Analyze audio features
        if "features" in audio_analysis:
            features = audio_analysis["features"]
            
            # Tempo affects energy and arousal
            tempo = features.get("tempo", 120)
            if tempo > 120:
                mood_scores["energy"] = min(1.0, mood_scores["energy"] + (tempo - 120) / 200)
                mood_scores["arousal"] = min(1.0, mood_scores["arousal"] + (tempo - 120) / 300)
            elif tempo < 80:
                mood_scores["energy"] = max(0.0, mood_scores["energy"] - (80 - tempo) / 200)
            
            # RMS energy affects perceived energy
            rms_energy = features.get("rms_energy", {}).get("mean", 0)
            if rms_energy > 0.05:
                mood_scores["energy"] = min(1.0, mood_scores["energy"] + 0.2)
                mood_scores["arousal"] = min(1.0, mood_scores["arousal"] + 0.15)
            
            # Spectral centroid affects brightness/valence
            spectral_centroid = features.get("spectral_centroid", {}).get("mean", 1000)
            if spectral_centroid > 2000:
                mood_scores["valence"] = min(1.0, mood_scores["valence"] + 0.2)
            elif spectral_centroid < 1000:
                mood_scores["valence"] = max(0.0, mood_scores["valence"] - 0.2)
        
        # Analyze speech quality
        if "quality" in audio_analysis:
            speech_ratio = audio_analysis["quality"].get("speech_ratio", 0.5)
            if speech_ratio > 0.7:
                mood_scores["dominance"] = min(1.0, mood_scores["dominance"] + 0.2)
        
        return mood_scores
        
    except Exception as e:
        logger.error(f"Error analyzing audio mood: {str(e)}")
        return {"energy": 0.5, "valence": 0.5, "arousal": 0.5, "dominance": 0.5}


def analyze_emotion_mood(emotion_analysis: Dict) -> Dict:
    """Analyze mood from emotion analysis results"""
    try:
        mood_scores = {
            "energy": 0.5,
            "valence": 0.5,
            "arousal": 0.5,
            "dominance": 0.5
        }
        
        # Map emotions to mood dimensions
        emotion_mapping = {
            "joy": {"energy": 0.8, "valence": 0.9, "arousal": 0.7, "dominance": 0.6},
            "excitement": {"energy": 0.9, "valence": 0.8, "arousal": 0.9, "dominance": 0.7},
            "anger": {"energy": 0.8, "valence": 0.1, "arousal": 0.8, "dominance": 0.8},
            "sadness": {"energy": 0.2, "valence": 0.2, "arousal": 0.3, "dominance": 0.3},
            "fear": {"energy": 0.6, "valence": 0.2, "arousal": 0.8, "dominance": 0.2},
            "surprise": {"energy": 0.7, "valence": 0.6, "arousal": 0.8, "dominance": 0.5},
            "calm": {"energy": 0.3, "valence": 0.7, "arousal": 0.2, "dominance": 0.5},
            "neutral": {"energy": 0.5, "valence": 0.5, "arousal": 0.5, "dominance": 0.5}
        }
        
        # Analyze audio emotions
        if "audio_emotions" in emotion_analysis:
            audio_emotions = emotion_analysis["audio_emotions"]
            
            for chunk in audio_emotions:
                for emotion in chunk.get("emotions", []):
                    emotion_label = emotion.get("label", "neutral").lower()
                    confidence = emotion.get("score", 0)
                    
                    if emotion_label in emotion_mapping:
                        emotion_mood = emotion_mapping[emotion_label]
                        for dim in mood_scores:
                            mood_scores[dim] += emotion_mood[dim] * confidence * 0.1
        
        # Analyze visual emotions
        if "visual_emotions" in emotion_analysis:
            visual_emotions = emotion_analysis["visual_emotions"]
            
            for frame in visual_emotions:
                for face in frame.get("faces", []):
                    for emotion in face.get("emotions", []):
                        emotion_label = emotion.get("label", "neutral").lower()
                        confidence = emotion.get("score", 0)
                        
                        if emotion_label in emotion_mapping:
                            emotion_mood = emotion_mapping[emotion_label]
                            for dim in mood_scores:
                                mood_scores[dim] += emotion_mood[dim] * confidence * 0.05
        
        # Normalize scores to [0, 1]
        for dim in mood_scores:
            mood_scores[dim] = max(0.0, min(1.0, mood_scores[dim]))
        
        return mood_scores
        
    except Exception as e:
        logger.error(f"Error analyzing emotion mood: {str(e)}")
        return {"energy": 0.5, "valence": 0.5, "arousal": 0.5, "dominance": 0.5}


def recommend_music_by_mood(mood_scores: Dict, duration_preference: Optional[int] = None) -> List[Dict]:
    """Recommend music based on mood scores"""
    try:
        recommendations = []
        
        # Determine primary mood category
        energy = mood_scores["energy"]
        valence = mood_scores["valence"]
        arousal = mood_scores["arousal"]
        
        # Select appropriate music categories
        if energy > 0.7 and valence > 0.6:
            # High energy, positive = upbeat/energetic
            categories = ["upbeat", "energetic"]
        elif energy < 0.4 and valence > 0.6:
            # Low energy, positive = calm/ambient
            categories = ["calm", "ambient"]
        elif arousal > 0.7 and valence < 0.4:
            # High arousal, negative = dramatic
            categories = ["dramatic"]
        elif energy > 0.6:
            # Medium-high energy = energetic
            categories = ["energetic", "upbeat"]
        else:
            # Default to calm
            categories = ["calm", "ambient"]
        
        # Get music from selected categories
        for category in categories:
            if category in MUSIC_DATABASE:
                for track in MUSIC_DATABASE[category]:
                    # Calculate compatibility score
                    track_energy = track["energy"]
                    track_valence = track["valence"]
                    
                    # Calculate mood similarity
                    energy_diff = abs(energy - track_energy)
                    valence_diff = abs(valence - track_valence)
                    compatibility = 1.0 - (energy_diff + valence_diff) / 2
                    
                    # Duration preference
                    duration_score = 1.0
                    if duration_preference:
                        duration_diff = abs(track["duration"] - duration_preference)
                        duration_score = max(0.5, 1.0 - duration_diff / duration_preference)
                    
                    final_score = compatibility * 0.7 + duration_score * 0.3
                    
                    recommendations.append({
                        **track,
                        "compatibility_score": compatibility,
                        "final_score": final_score,
                        "category": category,
                        "mood_match": {
                            "energy_match": 1.0 - energy_diff,
                            "valence_match": 1.0 - valence_diff
                        }
                    })
        
        # Sort by final score and return top recommendations
        recommendations.sort(key=lambda x: x["final_score"], reverse=True)
        return recommendations[:10]  # Top 10 recommendations
        
    except Exception as e:
        logger.error(f"Error recommending music: {str(e)}")
        return []


def analyze_existing_audio_for_music(audio_path: str) -> Dict:
    """Analyze existing audio to recommend complementary music"""
    try:
        # Load audio
        y, sr = librosa.load(audio_path, sr=22050)
        
        # Extract musical features
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        # Spectral features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
        
        # Energy
        rms = np.mean(librosa.feature.rms(y=y))
        
        # Chroma (harmonic content)
        chroma = np.mean(librosa.feature.chroma(y=y, sr=sr), axis=1)
        
        # MFCC features
        mfcc = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13), axis=1)
        
        # Derive mood from features
        mood_scores = {
            "energy": min(1.0, rms * 10),  # Scale RMS to energy
            "valence": min(1.0, (spectral_centroid / 4000)),  # Brightness -> positivity
            "arousal": min(1.0, (tempo / 200)),  # Tempo -> arousal
            "dominance": min(1.0, (spectral_rolloff / 8000))  # High frequencies -> dominance
        }
        
        return {
            "tempo": float(tempo),
            "spectral_centroid": float(spectral_centroid),
            "spectral_rolloff": float(spectral_rolloff),
            "rms_energy": float(rms),
            "chroma": chroma.tolist(),
            "mfcc": mfcc.tolist(),
            "mood_scores": mood_scores
        }
        
    except Exception as e:
        logger.error(f"Error analyzing audio for music recommendation: {str(e)}")
        raise


@router.post("/recommend")
async def recommend_music(
    video_analysis: Optional[Dict] = None,
    audio_analysis: Optional[Dict] = None,
    emotion_analysis: Optional[Dict] = None,
    duration_preference: Optional[int] = None,
    genre_preference: Optional[str] = None
):
    """
    Recommend music based on content analysis
    
    - **video_analysis**: Results from video analysis
    - **audio_analysis**: Results from audio analysis
    - **emotion_analysis**: Results from emotion analysis
    - **duration_preference**: Preferred music duration in seconds
    - **genre_preference**: Preferred genre/category
    """
    
    try:
        logger.info("Generating music recommendations...")
        
        # Initialize mood scores
        combined_mood = {"energy": 0.5, "valence": 0.5, "arousal": 0.5, "dominance": 0.5}
        analysis_count = 0
        
        # Analyze different inputs
        mood_analyses = []
        
        if video_analysis:
            video_mood = analyze_video_mood(video_analysis)
            mood_analyses.append(("video", video_mood))
            
        if audio_analysis:
            audio_mood = analyze_audio_mood(audio_analysis)
            mood_analyses.append(("audio", audio_mood))
            
        if emotion_analysis:
            emotion_mood = analyze_emotion_mood(emotion_analysis)
            mood_analyses.append(("emotion", emotion_mood))
        
        # Combine mood scores
        if mood_analyses:
            for analysis_type, mood in mood_analyses:
                for dim in combined_mood:
                    combined_mood[dim] += mood[dim]
                analysis_count += 1
            
            # Average the scores
            for dim in combined_mood:
                combined_mood[dim] /= analysis_count
        
        # Get music recommendations
        recommendations = recommend_music_by_mood(combined_mood, duration_preference)
        
        # Filter by genre preference if specified
        if genre_preference and genre_preference in MUSIC_DATABASE:
            recommendations = [r for r in recommendations if r["category"] == genre_preference]
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Music recommendations generated successfully",
                "data": {
                    "mood_analysis": {
                        "combined_mood": combined_mood,
                        "individual_analyses": {name: mood for name, mood in mood_analyses}
                    },
                    "recommendations": recommendations,
                    "parameters": {
                        "duration_preference": duration_preference,
                        "genre_preference": genre_preference,
                        "analysis_sources": len(mood_analyses)
                    },
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating music recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.post("/analyze-audio")
async def analyze_audio_for_music_recommendation(filename: str):
    """
    Analyze existing audio file to recommend complementary music
    
    - **filename**: Name of uploaded audio file
    """
    
    audio_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        logger.info(f"Analyzing audio for music recommendation: {filename}")
        
        # Analyze audio
        audio_features = analyze_existing_audio_for_music(audio_path)
        
        # Get recommendations based on audio mood
        recommendations = recommend_music_by_mood(audio_features["mood_scores"])
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Audio analysis and music recommendations completed",
                "data": {
                    "filename": filename,
                    "audio_features": audio_features,
                    "recommendations": recommendations,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error analyzing audio for music recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing audio: {str(e)}")


@router.get("/genres")
async def get_available_genres():
    """Get list of available music genres/categories"""
    
    return JSONResponse(
        status_code=200,
        content={
            "message": "Available music genres retrieved",
            "data": {
                "genres": list(MUSIC_DATABASE.keys()),
                "total_tracks": sum(len(tracks) for tracks in MUSIC_DATABASE.values()),
                "track_count_by_genre": {genre: len(tracks) for genre, tracks in MUSIC_DATABASE.items()}
            }
        }
    )


@router.post("/custom-mood")
async def recommend_by_custom_mood(
    energy: float = 0.5,
    valence: float = 0.5,
    arousal: float = 0.5,
    dominance: float = 0.5,
    duration_preference: Optional[int] = None
):
    """
    Recommend music based on custom mood parameters
    
    - **energy**: Energy level (0.0 - 1.0)
    - **valence**: Positivity/negativity (0.0 - 1.0)
    - **arousal**: Excitement/intensity (0.0 - 1.0)  
    - **dominance**: Control/power (0.0 - 1.0)
    - **duration_preference**: Preferred duration in seconds
    """
    
    # Validate parameters
    for param, value in [("energy", energy), ("valence", valence), ("arousal", arousal), ("dominance", dominance)]:
        if not 0.0 <= value <= 1.0:
            raise HTTPException(status_code=400, detail=f"{param} must be between 0.0 and 1.0")
    
    try:
        custom_mood = {
            "energy": energy,
            "valence": valence,
            "arousal": arousal,
            "dominance": dominance
        }
        
        recommendations = recommend_music_by_mood(custom_mood, duration_preference)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Custom mood recommendations generated",
                "data": {
                    "custom_mood": custom_mood,
                    "recommendations": recommendations,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating custom mood recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")
