"""
Configuration settings for VideoCraft AI Video Editor
"""
import os
from typing import List


class Settings:
    # Application Settings
    APP_NAME: str = "VideoCraft AI Video Editor"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))
    
    # CORS Settings
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",  # React development server
        "http://localhost:3001",  # Alternative React port
        "http://localhost:3002",  # Alternative React port  
        "http://localhost:3080",  # Alternative React port
        "http://localhost:8080",  # Alternative frontend port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3080",
        "http://127.0.0.1:8080",
        "*"  # Allow all origins in development (change for production)
    ]
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 2 * 1024 * 1024 * 1024  # 2GB
    ALLOWED_VIDEO_EXTENSIONS: List[str] = [
        ".mp4", ".avi", ".mov", ".mkv", ".wmv", 
        ".flv", ".webm", ".m4v", ".3gp", ".ogv"
    ]
    ALLOWED_AUDIO_EXTENSIONS: List[str] = [
        ".mp3", ".wav", ".aac", ".flac", ".ogg", 
        ".m4a", ".wma", ".aiff", ".au"
    ]
    
    # Storage Paths
    UPLOAD_DIR: str = "uploads"
    PROCESSED_DIR: str = "processed"
    TEMP_DIR: str = "temp"
    STATIC_DIR: str = "static"
    
    # AI Model Settings
    HUGGINGFACE_CACHE_DIR: str = os.getenv("HF_CACHE_DIR", "./models_cache")
    DEVICE: str = "cuda" if os.getenv("USE_GPU", "False").lower() == "true" else "cpu"
    
    # Video Processing Settings
    DEFAULT_VIDEO_QUALITY: str = "high"  # low, medium, high, ultra
    MAX_VIDEO_DURATION: int = 3600  # 1 hour in seconds
    
    # Audio Processing Settings
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHUNK_DURATION: int = 30  # seconds
    
    # Background Removal Settings
    BACKGROUND_MODEL: str = "u2net"  # u2net, silueta, isnet-general-use
    
    # Music Recommendation Settings
    MUSIC_GENRES: List[str] = [
        "ambient", "cinematic", "electronic", "acoustic", 
        "upbeat", "calm", "dramatic", "happy", "sad", "energetic"
    ]
    
    # Emotion Detection Settings
    EMOTION_LABELS: List[str] = [
        "anger", "anticipation", "disgust", "fear", 
        "joy", "love", "optimism", "pessimism", 
        "sadness", "surprise", "trust"
    ]
    
    # Database Settings (if using database)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./videocraft.db")
    
    # Redis Settings (for caching)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External API Keys (if needed)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # Performance Settings
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "8"))
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = "logs/videocraft.log"


# Create global settings instance
settings = Settings()
