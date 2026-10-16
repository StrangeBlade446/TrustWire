"""Unit Tests and Real-Model Smoke Tests for Video and Audio Detectors
Verifies model loading, input validation, output shapes, score calibration,
and error handling on synthetic fixtures.
"""

import wave
import numpy as np
import pytest
from pathlib import Path

from backend.detectors.video.detector import video_detector
from backend.detectors.audio.detector import audio_detector

def test_video_detector_availability_and_smoke():
    # Model should be loaded from verified checkpoint
    assert video_detector.is_available, f"Video detector failed to load: {video_detector._load_error}"

    # Test single frame preprocessing
    dummy_bgr = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    tensor = video_detector.preprocess_image(dummy_bgr)
    assert tensor.shape == (1, 3, 224, 224)
    assert -1.0 <= tensor.min() <= tensor.max() <= 1.0

    # Test single frame analysis
    evidence = video_detector.analyze_frame(dummy_bgr, timestamp_seconds=1.5)
    assert evidence.timestamp_seconds == 1.5
    assert 0.0 <= evidence.fake_score <= 1.0
    assert not np.isnan(evidence.fake_score)
    assert not np.isinf(evidence.fake_score)

def test_video_detector_missing_file(tmp_path):
    missing_path = tmp_path / "non_existent.mp4"
    result = video_detector.analyze_video(missing_path)
    assert result.status == "Error"
    assert result.classification == "Unavailable"
    assert "not found" in result.evidence_summary

def test_audio_detector_availability_and_smoke():
    assert audio_detector.is_available, f"Audio detector failed to load: {audio_detector._load_error}"

    # 1 second of 16kHz sine wave audio
    t = np.linspace(0, 1, 16000, endpoint=False)
    sine_samples = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

    score = audio_detector.analyze_samples(sine_samples)
    assert 0.0 <= score <= 1.0
    assert not np.isnan(score)
    assert not np.isinf(score)

def test_audio_detector_missing_file(tmp_path):
    missing_path = tmp_path / "missing_audio.wav"
    result = audio_detector.analyze_audio(missing_path)
    assert result.status == "Error"
    assert result.classification == "Unavailable"
    assert "not found" in result.evidence_summary

def test_audio_detector_on_synthetic_wav(tmp_path):
    # Generate a valid 2-second 16kHz mono WAV file
    wav_path = tmp_path / "synthetic_test.wav"
    sr = 16000
    t = np.linspace(0, 2, sr * 2, endpoint=False)
    samples = (32767 * 0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.int16)

    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(samples.tobytes())

    result = audio_detector.analyze_audio(wav_path, chunk_duration_sec=1.5, stride_sec=1.0)
    assert result.status == "Completed"
    assert result.chunks_analyzed >= 1
    assert result.audio_duration_seconds > 1.8
    assert 0.0 <= result.confidence_score <= 1.0
    assert result.classification in ["Likely authentic", "Potentially synthetic", "Inconclusive"]
    assert len(result.evidence_summary) > 10
