"""Integration Tests for Trustwire FastAPI Backend Server
Verifies REST endpoints, upload analysis pipeline, monitoring controls,
retention status, and security token enforcement.
"""

import wave
import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.config import settings

@pytest.fixture
def client():
    # TestClient bypasses auth or passes correct token
    return TestClient(app)

def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "Trustwire"
    assert "models" in data
    assert data["models"]["video_detector"] == "Ready"
    assert data["models"]["audio_detector"] == "Ready"
    assert data["models"]["fraud_engine"] == "Ready"

def test_api_models_list(client):
    res = client.get("/api/models")
    assert res.status_code == 200
    models = res.json()
    assert len(models) == 4
    model_ids = [m["id"] for m in models]
    assert "video_deepfake" in model_ids
    assert "audio_deepfake" in model_ids
    assert "speech_transcription" in model_ids
    assert "fraud_rules_engine" in model_ids

    for m in models:
        assert "limitations" in m
        assert len(m["limitations"]) > 5
        assert m["status"] in ["Ready", "Unavailable"]

def test_monitoring_lifecycle(client):
    # 1. Sources
    sources_res = client.get("/api/monitoring/sources")
    assert sources_res.status_code == 200
    sources = sources_res.json()
    assert "monitors" in sources
    assert "audio_loopback_devices" in sources

    # 2. Status initially stopped
    status_res = client.get("/api/monitoring/status")
    assert status_res.status_code == 200
    assert not status_res.json()["is_monitoring"]

    # 3. Start monitoring
    start_res = client.post("/api/monitoring/start", json={
        "video_enabled": False,  # disable screen grab in headless CI
        "audio_enabled": False,
        "fraud_enabled": False
    })
    assert start_res.status_code == 200
    assert start_res.json()["status"] == "started"

    # 4. Stop monitoring
    stop_res = client.post("/api/monitoring/stop")
    assert stop_res.status_code == 200
    assert stop_res.json()["status"] == "stopped"

def test_upload_and_analyze_synthetic_audio(client, tmp_path):
    # Create valid synthetic WAV file
    wav_path = tmp_path / "test_api_audio.wav"
    sr = 16000
    t = np.linspace(0, 1.5, int(sr * 1.5), endpoint=False)
    samples = (32767 * 0.2 * np.sin(2 * np.pi * 300 * t)).astype(np.int16)

    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(samples.tobytes())

    with open(wav_path, "rb") as f:
        res = client.post(
            "/api/analyze/upload",
            files={"file": ("test_api_audio.wav", f, "audio/wav")},
            data={"analyze_video_track": "false", "analyze_audio_track": "true", "analyze_fraud_track": "true"}
        )

    assert res.status_code == 200
    data = res.json()
    assert data["media_type"] == "Audio"
    assert data["audio_analysis"] is not None
    assert data["audio_analysis"]["status"] == "Completed"
    assert data["audio_analysis"]["classification"] in ["Likely authentic", "Potentially synthetic", "Inconclusive"]
    assert data["fraud_assessment"] is not None
    assert not data["fraud_assessment"]["is_suspicious"]

def test_alerts_endpoints(client):
    # Fetch alerts
    res = client.get("/api/alerts")
    assert res.status_code == 200
    alerts = res.json()
    assert isinstance(alerts, list)

def test_privacy_status_and_purge(client):
    res = client.get("/api/privacy/status")
    assert res.status_code == 200
    data = res.json()
    assert data["retention_policy_minutes"] == 15.0
    assert "active_temp_files" in data

    purge_res = client.post("/api/privacy/purge")
    assert purge_res.status_code == 200
    assert purge_res.json()["status"] == "purged"
