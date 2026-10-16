"""Unit Tests for Trustwire 15-Minute Privacy Retention Policy
Verifies artifact registration, automatic expiration cleanup, startup crash recovery,
and explicit purging.
"""

import time
from pathlib import Path
import pytest
from backend.privacy.retention import RetentionManager

@pytest.fixture
def test_retention(tmp_path):
    # Create an isolated RetentionManager with a 1-second retention limit for fast tests
    rm = RetentionManager(temp_dir=tmp_path, max_retention_seconds=1)
    # Stop background thread in unit test to test methods deterministically
    rm.stop_background_cleaner()
    yield rm
    rm.stop_background_cleaner()

def test_register_and_status(test_retention, tmp_path):
    test_file = tmp_path / "test_frame.jpg"
    test_file.write_bytes(b"sample_frame_bytes_data")

    test_retention.register_artifact(test_file, tag="frame")
    status = test_retention.get_status()

    assert status["active_temp_files"] == 1
    assert status["total_temp_size_bytes"] == len(b"sample_frame_bytes_data")
    assert status["max_retention_seconds"] == 1

def test_expired_cleanup(test_retention, tmp_path):
    test_file = tmp_path / "test_audio.wav"
    test_file.write_bytes(b"dummy_audio_bytes")
    test_retention.register_artifact(test_file, tag="audio_chunk")

    assert test_file.exists()

    # Sleep past the 1-second expiry limit
    time.sleep(1.2)

    deleted_count = test_retention.clean_expired()
    assert deleted_count >= 1
    assert not test_file.exists()

def test_startup_recovery(tmp_path):
    # Simulate a crashed session that left an old artifact behind
    leftover_file = tmp_path / "orphaned_capture.mp4"
    leftover_file.write_bytes(b"crash_leftover_data")

    # Manually set modification time to 20 minutes ago (1200s ago)
    old_time = time.time() - 1200
    import os
    os.utime(leftover_file, (old_time, old_time))

    # Initialize a new RetentionManager pointing at this directory
    rm = RetentionManager(temp_dir=tmp_path, max_retention_seconds=900)
    rm.stop_background_cleaner()

    # The startup recovery runs automatically in __init__
    assert not leftover_file.exists()

def test_purge_all(test_retention, tmp_path):
    file1 = tmp_path / "file1.tmp"
    file2 = tmp_path / "file2.tmp"
    file1.write_text("1")
    file2.write_text("2")

    test_retention.register_artifact(file1)
    test_retention.register_artifact(file2)

    purged = test_retention.purge_all()
    assert purged == 2
    assert not file1.exists()
    assert not file2.exists()
    assert test_retention.get_status()["active_temp_files"] == 0
