"""
Central configuration for ProfAI system.
Manages API keys, model paths, and system constants.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """System-wide configuration settings."""
    
    # API Keys (from .env)
    GEMINI_API_KEY: str
    ELEVENLABS_API_KEY: str
    
    # Model Configuration
    EMOTION_MODEL_PATH: str = "speechbrain/emotion-recognition-wav2vec2-IEMOCAP"
    TTS_VOICE_ID: str = "Adam"
    
    # Audio Streaming Settings
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHUNK_SIZE: int = 1024
    
    # System Defaults
    DEFAULT_DIFFICULTY: float = 0.5
    DEFAULT_ENGAGEMENT: float = 0.8
    SESSION_TIMEOUT: int = 3600
    
    class Config:
        env_file = ".env"


settings = Settings()