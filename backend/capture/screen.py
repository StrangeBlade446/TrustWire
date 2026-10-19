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
    def _attach_thread_desktop():
        """Ensure current thread is attached to the interactive desktop (WinSta0\\default) on Windows."""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            # 0x01FF = DESKTOP_ALL
            hdesk = user32.OpenDesktopW("default", 0, False, 0x01FF)
            if hdesk:
                user32.SetThreadDesktop(hdesk)
        except Exception:
            pass

    @staticmethod
    def get_available_monitors() -> List[Dict[str, Any]]:
        """Enumerate system monitors using mss."""
        ScreenCaptureWorker._attach_thread_desktop()
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

    def _gdi_grab(self, mon: Dict[str, Any]) -> Optional[np.ndarray]:
        """Fallback direct Windows GDI BitBlt capture."""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32

            w = mon.get("width", 1920)
            h = mon.get("height", 1080)
            left = mon.get("left", 0)
            top = mon.get("top", 0)

            hdc_screen = user32.GetDC(0)
            if not hdc_screen:
                return None
            hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
            hbm = gdi32.CreateCompatibleBitmap(hdc_screen, w, h)
            old_hbm = gdi32.SelectObject(hdc_mem, hbm)

            # BitBlt with standard SRCCOPY (0x00CC0020)
            success = gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc_screen, left, top, 0x00CC0020)
            if not success:
                user32.ReleaseDC(0, hdc_screen)
                gdi32.DeleteDC(hdc_mem)
                gdi32.DeleteObject(hbm)
                return None

            class BITMAPINFOHEADER(ctypes.Structure):
                _fields_ = [
                    ('biSize', ctypes.c_uint32),
                    ('biWidth', ctypes.c_int32),
                    ('biHeight', ctypes.c_int32),
                    ('biPlanes', ctypes.c_uint16),
                    ('biBitCount', ctypes.c_uint16),
                    ('biCompression', ctypes.c_uint32),
                    ('biSizeImage', ctypes.c_uint32),
                    ('biXPelsPerMeter', ctypes.c_int32),
                    ('biYPelsPerMeter', ctypes.c_int32),
                    ('biClrUsed', ctypes.c_uint32),
                    ('biClrImportant', ctypes.c_uint32),
                ]

            bmi = BITMAPINFOHEADER()
            bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
            bmi.biWidth = w
            bmi.biHeight = -h  # top-down
            bmi.biPlanes = 1
            bmi.biBitCount = 24
            bmi.biCompression = 0

            buf = ctypes.create_string_buffer(w * h * 3)
            lines = gdi32.GetDIBits(hdc_mem, hbm, 0, h, buf, ctypes.byref(bmi), 0)

            gdi32.SelectObject(hdc_mem, old_hbm)
            gdi32.DeleteObject(hbm)
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(0, hdc_screen)

            if lines == h:
                return np.frombuffer(buf, dtype=np.uint8).reshape((h, w, 3))
            return None
        except Exception as ge:
            logger.debug(f"GDI fallback grab error: {ge}")
            return None

    def _capture_loop(self):
        logger.info(f"Screen capture loop started on monitor {self.monitor_index}.")
        self._attach_thread_desktop()
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
                        frame_bgr = None
                        try:
                            # 1. Grab screenshot via high-performance mss
                            sct_img = sct.grab(mon)
                            frame_bgra = np.array(sct_img, dtype=np.uint8)
                            frame_bgr = frame_bgra[:, :, :3]
                        except Exception:
                            # 2. Seamless fallback via Win32 GDI
                            self._attach_thread_desktop()
                            frame_bgr = self._gdi_grab(mon)

                        if frame_bgr is not None:
                            # Put in bounded queue; drop previous stale frame if full
                            try:
                                self.frame_queue.put_nowait((frame_bgr, t_start))
                                self.frames_captured += 1
                            except queue.Full:
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
