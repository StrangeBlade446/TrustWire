"""Trustwire Windows WASAPI Loopback Audio Capture Worker
Records system audio output in real-time via soundcard MediaFoundation loopback,
resampling to 16kHz mono with bounded in-memory buffering and zero disk I/O.
"""

import time
import queue
import logging
import threading
from typing import Optional, Dict, Any, List
import numpy as np
import soundcard as sc

logger = logging.getLogger("trustwire.capture.audio")

class AudioLoopbackWorker:
    """Captures system output audio via Windows WASAPI loopback without writing to disk."""

    def __init__(self, sample_rate: int = 16000, chunk_duration_sec: float = 2.0, device_id: Optional[str] = None):
        self.sample_rate = sample_rate
        self.chunk_duration_sec = chunk_duration_sec
        self.device_id = device_id
        self._stop_event = threading.Event()
        self._capture_thread: Optional[threading.Thread] = None
        # Bounded audio chunk queue (holds at most 3 recent chunks ~6 seconds)
        self.audio_queue: queue.Queue = queue.Queue(maxsize=3)
        self.chunks_captured = 0
        self.chunks_dropped = 0
        self.active_device_name: str = "Default Speaker Loopback"

    @staticmethod
    def get_available_loopback_devices() -> List[Dict[str, Any]]:
        """List all available Windows WASAPI loopback playback audio devices."""
        try:
            mics = sc.all_microphones(include_loopback=True)
            devices = []
            for m in mics:
                if getattr(m, 'isloopback', False):
                    devices.append({
                        "id": str(m.id),
                        "name": m.name,
                        "channels": m.channels
                    })
            return devices
        except Exception as e:
            logger.error(f"Error enumerating audio loopback devices: {e}")
            return []

    def _select_loopback_device(self):
        """Find the requested loopback device or default speaker loopback."""
        mics = sc.all_microphones(include_loopback=True)
        loopbacks = [m for m in mics if getattr(m, 'isloopback', False)]
        if not loopbacks:
            raise RuntimeError("No WASAPI loopback audio devices found on system.")

        if self.device_id:
            for lb in loopbacks:
                if str(lb.id) == str(self.device_id):
                    return lb

        # Default to first loopback device
        return loopbacks[0]

    def _capture_loop(self):
        logger.info("Starting WASAPI audio loopback capture loop...")
        try:
            device = self._select_loopback_device()
            self.active_device_name = device.name
            logger.info(f"Using audio loopback device: {self.active_device_name}")

            chunk_samples = int(self.sample_rate * self.chunk_duration_sec)

            with device.recorder(samplerate=self.sample_rate, channels=1) as mic:
                while not self._stop_event.is_set():
                    t_start = time.time()
                    try:
                        # Record chunk_samples
                        data = mic.record(numframes=chunk_samples)
                        # Flatten to 1D mono float32 array
                        mono = data[:, 0].astype(np.float32)

                        # Check if audio has non-trivial signal
                        rms = np.sqrt(np.mean(mono ** 2))
                        has_signal = bool(rms > 0.005)

                        item = {
                            "samples": mono,
                            "timestamp": t_start,
                            "duration_sec": self.chunk_duration_sec,
                            "has_signal": has_signal,
                            "rms": float(rms)
                        }

                        try:
                            self.audio_queue.put_nowait(item)
                            self.chunks_captured += 1
                        except queue.Full:
                            # Drop oldest chunk to prevent latency accumulation
                            try:
                                _ = self.audio_queue.get_nowait()
                                self.audio_queue.put_nowait(item)
                                self.chunks_dropped += 1
                            except Exception:
                                pass

                    except Exception as rec_err:
                        logger.error(f"Error recording audio chunk: {rec_err}")
                        self._stop_event.wait(timeout=0.2)

        except Exception as e:
            logger.error(f"Fatal WASAPI audio loopback error: {e}")
        finally:
            logger.info("Audio loopback capture loop terminated.")

    def start(self):
        """Start audio loopback capture thread."""
        if self._capture_thread is None or not self._capture_thread.is_alive():
            self._stop_event.clear()
            self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True, name="TrustwireAudioCapture")
            self._capture_thread.start()

    def stop(self):
        """Stop audio loopback capture immediately."""
        self._stop_event.set()
        if self._capture_thread and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=1.5)
        # Empty queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except Exception:
                break
