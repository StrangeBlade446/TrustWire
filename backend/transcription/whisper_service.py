"""Trustwire Local Speech Transcription Service
Uses faster-whisper (CTranslate2) with int8 quantization for local, privacy-first,
bounded-memory speech transcription on Windows CPU.
"""

import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pydantic import BaseModel
from faster_whisper import WhisperModel

from backend.config import settings

logger = logging.getLogger("trustwire.transcription")

class TranscriptSegment(BaseModel):
    start_seconds: float
    end_seconds: float
    text: str

class TranscriptionResult(BaseModel):
    status: str  # "Completed", "Unavailable", "Error"
    full_text: str
    language: str
    language_probability: float
    segments: List[TranscriptSegment]
    duration_seconds: float
    processing_duration_ms: float

class WhisperTranscriptionService:
    """Manages local Whisper model for offline speech-to-text."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.whisper_model_name
        self.model: Optional[WhisperModel] = None
        self._load_error: Optional[str] = None
        self._initialize_model()

    def _initialize_model(self):
        try:
            logger.info(f"Loading Whisper model '{self.model_name}' (device={settings.whisper_device}, compute_type={settings.whisper_compute_type})...")
            self.model = WhisperModel(
                self.model_name,
                device=settings.whisper_device,
                compute_type=settings.whisper_compute_type
            )
            logger.info("Whisper speech model loaded successfully.")
        except Exception as e:
            self._load_error = str(e)
            logger.error(f"Failed to load Whisper model: {e}")

    @property
    def is_available(self) -> bool:
        return self.model is not None

    def transcribe_audio_samples(self, samples_16k: np.ndarray) -> TranscriptionResult:
        """Transcribe an in-memory 16kHz mono float32 audio array."""
        t0 = time.time()
        if not self.is_available:
            return TranscriptionResult(
                status="Unavailable",
                full_text="",
                language="unknown",
                language_probability=0.0,
                segments=[],
                duration_seconds=0.0,
                processing_duration_ms=round((time.time() - t0) * 1000, 2)
            )

        duration_sec = len(samples_16k) / 16000.0
        try:
            segments_gen, info = self.model.transcribe(
                samples_16k,
                beam_size=1,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            segments = []
            texts = []
            for s in segments_gen:
                clean_text = s.text.strip()
                if clean_text:
                    segments.append(TranscriptSegment(
                        start_seconds=round(s.start, 2),
                        end_seconds=round(s.end, 2),
                        text=clean_text
                    ))
                    texts.append(clean_text)

            full_text = " ".join(texts)
            return TranscriptionResult(
                status="Completed",
                full_text=full_text,
                language=info.language,
                language_probability=round(info.language_probability, 4),
                segments=segments,
                duration_seconds=round(duration_sec, 2),
                processing_duration_ms=round((time.time() - t0) * 1000, 2)
            )
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return TranscriptionResult(
                status="Error",
                full_text="",
                language="unknown",
                language_probability=0.0,
                segments=[],
                duration_seconds=round(duration_sec, 2),
                processing_duration_ms=round((time.time() - t0) * 1000, 2)
            )

    def transcribe_file(self, audio_path: Path) -> TranscriptionResult:
        """Transcribe an audio file from disk."""
        t0 = time.time()
        if not self.is_available:
            return TranscriptionResult(
                status="Unavailable",
                full_text="",
                language="unknown",
                language_probability=0.0,
                segments=[],
                duration_seconds=0.0,
                processing_duration_ms=round((time.time() - t0) * 1000, 2)
            )

        try:
            segments_gen, info = self.model.transcribe(
                str(audio_path),
                beam_size=1,
                vad_filter=True
            )
            segments = []
            texts = []
            for s in segments_gen:
                clean_text = s.text.strip()
                if clean_text:
                    segments.append(TranscriptSegment(
                        start_seconds=round(s.start, 2),
                        end_seconds=round(s.end, 2),
                        text=clean_text
                    ))
                    texts.append(clean_text)

            full_text = " ".join(texts)
            return TranscriptionResult(
                status="Completed",
                full_text=full_text,
                language=info.language,
                language_probability=round(info.language_probability, 4),
                segments=segments,
                duration_seconds=round(info.duration, 2),
                processing_duration_ms=round((time.time() - t0) * 1000, 2)
            )
        except Exception as e:
            logger.error(f"File transcription failed: {e}")
            return TranscriptionResult(
                status="Error",
                full_text="",
                language="unknown",
                language_probability=0.0,
                segments=[],
                duration_seconds=0.0,
                processing_duration_ms=round((time.time() - t0) * 1000, 2)
            )

# Global singleton
whisper_service = WhisperTranscriptionService()
