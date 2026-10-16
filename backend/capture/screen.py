"""Trustwire Windows Screen Capture Worker
Captures frames from Windows desktop using mss with bounded queue and automatic frame-dropping
to ensure zero latency buildup.
"""

import time
import queue
import logging
import threading
from typing import Optional, Dict, Any, List
import numpy as np
import mss

logger = logging.getLogger("trustwire.capture.screen")

class ScreenCaptureWorker:
    """Bounded, non-blocking Windows desktop screen capture worker."""

    def __init__(self, sample_interval_seconds: float = 1.0, monitor_index: int = 1):
        self.sample_interval = sample_interval_seconds
        self.monitor_index = monitor_index
        self._stop_event = threading.Event()
        self._capture_thread: Optional[threading.Thread] = None
        # Bounded frame queue: size 1 to discard stale frames instantly
        self.frame_queue: queue.Queue = queue.Queue(maxsize=1)
        self.frames_captured = 0
        self.frames_dropped = 0
        self.active_monitor_info: Dict[str, Any] = {}

    @staticmethod
    def get_available_monitors() -> List[Dict[str, Any]]:
        """Enumerate system monitors using mss."""
        try:
            with mss.MSS() as sct:
                monitors = []
                for idx, m in enumerate(sct.monitors):
                    if idx == 0:
                        # Index 0 represents the virtual composite of all monitors in mss
                        continue
                    monitors.append({
                        "index": idx,
                        "name": f"Display {idx}",
                        "width": m["width"],
                        "height": m["height"],
                        "left": m["left"],
                        "top": m["top"]
                    })
                return monitors
        except Exception as e:
            logger.error(f"Error enumerating monitors: {e}")
            return [{"index": 1, "name": "Primary Display", "width": 1920, "height": 1080}]

    def _capture_loop(self):
        logger.info(f"Screen capture loop started on monitor {self.monitor_index}.")
        try:
            with mss.MSS() as sct:
                if self.monitor_index >= len(sct.monitors):
                    mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                else:
                    mon = sct.monitors[self.monitor_index]

                self.active_monitor_info = {
                    "width": mon["width"],
                    "height": mon["height"],
                    "left": mon["left"],
                    "top": mon["top"]
                }

                while not self._stop_event.is_set():
                    t_start = time.time()
                    try:
                        # Grab screenshot
                        sct_img = sct.grab(mon)
                        # Convert to BGR numpy array
                        frame_bgra = np.array(sct_img, dtype=np.uint8)
                        frame_bgr = frame_bgra[:, :, :3]  # Drop alpha channel

                        # Put in bounded queue; drop previous stale frame if full
                        try:
                            self.frame_queue.put_nowait((frame_bgr, t_start))
                            self.frames_captured += 1
                        except queue.Full:
                            # Drop stale frame to keep latency real-time
                            try:
                                _ = self.frame_queue.get_nowait()
                                self.frame_queue.put_nowait((frame_bgr, t_start))
                                self.frames_dropped += 1
                            except Exception:
                                pass

                    except Exception as grab_err:
                        logger.error(f"Screen grab error: {grab_err}")

                    # Sleep remaining interval
                    elapsed = time.time() - t_start
                    sleep_time = max(0.01, self.sample_interval - elapsed)
                    self._stop_event.wait(timeout=sleep_time)

        except Exception as e:
            logger.error(f"Fatal screen capture worker error: {e}")
        finally:
            logger.info("Screen capture loop terminated.")

    def start(self):
        """Start screen capture thread."""
        if self._capture_thread is None or not self._capture_thread.is_alive():
            self._stop_event.clear()
            self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True, name="TrustwireScreenCapture")
            self._capture_thread.start()

    def stop(self):
        """Stop screen capture immediately."""
        self._stop_event.set()
        if self._capture_thread and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=1.5)
        # Empty queue
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except Exception:
                break
