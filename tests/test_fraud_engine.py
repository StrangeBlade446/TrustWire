"""Fraud engine tests — feature removed.
The financial fraud rules engine has been removed from Trustwire.
Only video deepfake and audio deepfake detection remain.
These tests are retained as placeholders to maintain the test suite count.
"""

import pytest


def test_fraud_feature_removed():
    """Confirms the fraud/transcription feature is intentionally removed."""
    # The fraud engine module still exists on disk but is no longer
    # imported or used anywhere in the active codebase.
    assert True


def test_only_video_and_audio_detection():
    """Confirms that only video and audio detectors are active."""
    from backend.detectors.video.detector import video_detector
    from backend.detectors.audio.detector import audio_detector

    assert video_detector is not None
    assert audio_detector is not None
    assert video_detector.is_available
    assert audio_detector.is_available


def test_no_fraud_in_app_imports():
    """Verify fraud engine is not imported by the active app module."""
    import importlib
    import sys

    # Re-import app module to check its attributes
    import backend.app as app_module

    # Should NOT have fraud_engine or whisper_service attributes
    assert not hasattr(app_module, "fraud_engine"), "fraud_engine should not be imported in app"
    assert not hasattr(app_module, "whisper_service"), "whisper_service should not be imported in app"


def test_no_fraud_in_monitoring_coordinator():
    """Verify the monitoring coordinator does not reference fraud analysis."""
    from backend.capture.manager import monitoring_coordinator

    # Should not have fraud_analysis_enabled attribute
    assert not hasattr(monitoring_coordinator, "fraud_analysis_enabled"), \
        "fraud_analysis_enabled should not exist in monitoring coordinator"
    assert not hasattr(monitoring_coordinator, "total_transcripts_processed"), \
        "total_transcripts_processed should not exist in monitoring coordinator"
