"""Trustwire Backend Configuration
Manages server settings, model paths, security tokens, and privacy retention rules.
"""
import os
import secrets
from pathlib import Path
from pydantic import BaseModel

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
TEMP_DIR = BASE_DIR / "temp_media"
ALERTS_DIR = BASE_DIR / "alerts_store"

# Ensure runtime directories exist
TEMP_DIR.mkdir(parents=True, exist_ok=True)
ALERTS_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    app_name: str = "Trustwire"
    app_version: str = "1.0.0"
    host: str = "127.0.0.1"  # Localhost only for security
    port: int = 8765
    
    # Capability token authentication between Electron UI and FastAPI backend
    api_token: str = os.environ.get("TRUSTWIRE_API_TOKEN", secrets.token_hex(24))
    
    # Privacy & Retention Configuration
    # Strict maximum retention: 15 minutes (900 seconds)
    max_retention_seconds: int = 900
    cleanup_interval_seconds: int = 30
    
    # Model Paths
    video_model_dir: Path = MODELS_DIR / "video"
    video_model_onnx: Path = MODELS_DIR / "video" / "onnx" / "model_quantized.onnx"
    video_model_config: Path = MODELS_DIR / "video" / "config.json"
    
    audio_model_dir: Path = MODELS_DIR / "audio"
    audio_model_safetensors: Path = MODELS_DIR / "audio" / "model.safetensors"
    audio_model_config: Path = MODELS_DIR / "audio" / "config.json"
    
    # Whisper Transcription Configuration
    whisper_model_name: str = "tiny"  # Lightweight for fast real-time local transcription
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"

    # Temporary Media Storage
    temp_storage_dir: Path = TEMP_DIR
    alerts_storage_dir: Path = ALERTS_DIR

settings = Settings()
