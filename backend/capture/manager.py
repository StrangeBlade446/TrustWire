"""Trustwire Live Monitoring Coordinator
Coordinates Windows screen capture and WASAPI loopback audio capture with real-time
inference pipelines for Video Deepfake and Audio Deepfake detection.
"""

import time
import queue
import logging
import threading
from typing import Dict, Any, Optional

from backend.capture.screen import ScreenCaptureWorker
from backend.capture.audio import AudioLoopbackWorker
from backend.detectors.video.detector import video_detector
from backend.detectors.audio.detector import audio_detector
from backend.alerts.hub import alert_hub

logger = logging.getLogger("trustwire.capture.manager")

class LiveMonitoringCoordinator:
    """Orchestrates live capture, thread-isolated model inference, and alert triggering."""

    def __init__(self):
        self.screen_worker = ScreenCaptureWorker(sample_interval_seconds=1.0)
        self.audio_worker = AudioLoopbackWorker(chunk_duration_sec=2.5)

        self.video_analysis_enabled: bool = True
        self.audio_analysis_enabled: bool = True

        self._is_monitoring = False
        self._stop_event = threading.Event()
        self._inference_thread: Optional[threading.Thread] = None

        self.last_activity_timestamp = time.time()
        self.total_video_frames_processed = 0
        self.total_audio_chunks_processed = 0
        self.recent_activity: Dict[str, Any] = {
            "last_video_score": 0.0,
            "last_audio_score": 0.0,
        }

    @property
    def is_monitoring(self) -> bool:
        return self._is_monitoring

    def configure(self, video_enabled: bool, audio_enabled: bool, monitor_index: int = 1, audio_device_id: Optional[str] = None):
        """Update detector toggles and capture sources."""
        self.video_analysis_enabled = video_enabled
        self.audio_analysis_enabled = audio_enabled
        self.screen_worker.monitor_index = monitor_index
        self.audio_worker.device_id = audio_device_id

    def _inference_loop(self):
        logger.info("Live inference pipeline started.")
        while not self._stop_event.is_set():
            loop_active = False

            # 1. Process Pending Screen Frame
            if self.video_analysis_enabled and video_detector.is_available:
                try:
                    frame_bgr, t_capture = self.screen_worker.frame_queue.get_nowait()
                    loop_active = True
                    self.total_video_frames_processed += 1
                    evidence = video_detector.analyze_frame(frame_bgr, timestamp_seconds=time.time())

                    # If watermark was not in desktop bottom-right, check active foreground window sub-region
                    if evidence.fake_score < 0.85:
                        try:
                            import ctypes
                            from ctypes import wintypes
                            user32 = ctypes.windll.user32
                            hwnd = user32.GetForegroundWindow()
                            if hwnd:
                                rect = wintypes.RECT()
                                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                                wl = max(0, rect.left)
                                wt = max(0, rect.top)
                                wr = min(frame_bgr.shape[1], rect.right)
                                wb = min(frame_bgr.shape[0], rect.bottom)
                                if (wr - wl) >= 200 and (wb - wt) >= 150:
                                    win_crop = frame_bgr[wt:wb, wl:wr]
                                    has_wm_win, wm_score_win = video_detector.detect_watermark(win_crop)
                                    if has_wm_win:
                                        evidence.fake_score = max(evidence.fake_score, 0.96)
                        except Exception:
                            pass

                    self.recent_activity["last_video_score"] = evidence.fake_score
                    self.last_activity_timestamp = time.time()

                    # Trigger alert if suspicious face or generative watermark detected
                    if (evidence.face_detected and evidence.fake_score >= 0.52) or evidence.fake_score >= 0.85:
                        severity = "Critical" if evidence.fake_score >= 0.80 else "High"
                        title = "Suspicious Facial Generation Detected on Screen" if evidence.face_detected else "Generative AI Video / Watermark Detected on Screen"
                        explanation = (
                            f"A facial region displayed on screen exhibited high-probability manipulation artifacts ({evidence.fake_score*100:.1f}% confidence)."
                            if evidence.face_detected else
                            f"Generative AI video watermark signatures detected on screen ({evidence.fake_score*100:.1f}% confidence)."
                        )
                        alert_hub.dispatch_alert(
                            category="video_deepfake",
                            severity=severity,
                            title=title,
                            explanation=explanation,
                            evidence={
                                "fake_score": evidence.fake_score,
                                "face_detected": evidence.face_detected,
                                "bounding_box": evidence.bounding_box
                            },
                            source="Live Monitoring",
                            model_or_rule=getattr(video_detector, "model_name", "Vision Transformer Deepfake Classifier"),
                            confidence_score=evidence.fake_score,
                            suggested_action="Verify caller identity via a trusted secondary channel. Avoid taking actions based solely on video appearance."
                        )
                except queue.Empty:
                    pass
                except Exception as ve:
                    logger.error(f"Live video inference/alert error: {ve}", exc_info=True)

            # 2. Process Pending Audio Loopback Chunk
            if self.audio_analysis_enabled:
                try:
                    chunk_item = self.audio_worker.audio_queue.get_nowait()
                    loop_active = True
                    samples = chunk_item["samples"]
                    has_signal = chunk_item["has_signal"]
                    self.total_audio_chunks_processed += 1
                    self.last_activity_timestamp = time.time()

                    # Audio Deepfake Analysis (synchronized with media analyzer threshold)
                    if audio_detector.is_available and has_signal:
                        try:
                            score = audio_detector.analyze_samples(samples)
                            self.recent_activity["last_audio_score"] = round(score, 4)

                            if score >= 0.65:
                                severity = "Critical" if score >= 0.85 else "High"
                                alert_hub.dispatch_alert(
                                    category="audio_deepfake",
                                    severity=severity,
                                    title="Synthetic Speech or Voice Cloning Detected in System Audio",
                                    explanation=f"Playback audio features match neural voice synthesis or vocoder cloning artifacts ({score*100:.1f}% confidence).",
                                    evidence={"fake_score": round(score, 4), "rms": chunk_item["rms"]},
                                    source="Live Monitoring",
                                    model_or_rule="Wav2Vec2 Audio Classifier",
                                    confidence_score=score,
                                    suggested_action="Do not confirm personal details or financial transactions over this call. Hang up and verify."
                                )
                        except Exception as ae:
                            logger.error(f"Live audio inference error: {ae}")

                except queue.Empty:
                    pass
                except Exception:
                    pass

            # Sleep briefly if no data to avoid busy waiting
            if not loop_active:
                self._stop_event.wait(timeout=0.08)

        logger.info("Live inference pipeline terminated.")

    def start_monitoring(self):
        """Start screen capture, audio loopback capture, and inference pipeline."""
        if self._is_monitoring:
            return

        self._stop_event.clear()
        # Start capture workers based on configuration
        if self.video_analysis_enabled:
            self.screen_worker.start()
        if self.audio_analysis_enabled:
            self.audio_worker.start()

        # Start background inference loop
        self._inference_thread = threading.Thread(target=self._inference_loop, daemon=True, name="TrustwireInferencePipeline")
        self._inference_thread.start()

        self._is_monitoring = True
        logger.info("Trustwire Live Monitoring started.")

    def stop_monitoring(self):
        """Stop all capture workers and inference loops immediately."""
        if not self._is_monitoring:
            return

        self._stop_event.set()
        self.screen_worker.stop()
        self.audio_worker.stop()

        if self._inference_thread and self._inference_thread.is_alive():
            self._inference_thread.join(timeout=1.5)

        self._is_monitoring = False
        logger.info("Trustwire Live Monitoring stopped.")

    def get_status(self) -> Dict[str, Any]:
        """Return real-time monitoring and capture diagnostics."""
        return {
            "is_monitoring": self._is_monitoring,
            "video_analysis_enabled": self.video_analysis_enabled,
            "audio_analysis_enabled": self.audio_analysis_enabled,
            "screen_source": self.screen_worker.active_monitor_info or "Display 1",
            "audio_source": self.audio_worker.active_device_name,
            "frames_captured": self.screen_worker.frames_captured,
            "frames_dropped": self.screen_worker.frames_dropped,
            "audio_chunks_captured": self.audio_worker.chunks_captured,
            "audio_chunks_dropped": self.audio_worker.chunks_dropped,
            "video_frames_processed": self.total_video_frames_processed,
            "audio_chunks_processed": self.total_audio_chunks_processed,
            "recent_activity": self.recent_activity,
            "last_activity_seconds_ago": round(time.time() - self.last_activity_timestamp, 1)
        }

# Global singleton
monitoring_coordinator = LiveMonitoringCoordinator()
