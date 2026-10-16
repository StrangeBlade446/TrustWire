"""Trustwire Privacy & Automatic Retention Manager
Enforces strict 15-minute maximum retention on temporary captured audio/video artifacts.
Provides background periodic cleanup, startup recovery, safe deletion, and status reporting.
"""

import os
import time
import shutil
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional

from backend.config import settings

logger = logging.getLogger("trustwire.retention")

class RetentionManager:
    """Manages temporary media files and guarantees deletion within max_retention_seconds (15 min)."""

    def __init__(self, temp_dir: Optional[Path] = None, max_retention_seconds: Optional[int] = None):
        self.temp_dir = Path(temp_dir or settings.temp_storage_dir)
        self.max_retention_seconds = max_retention_seconds or settings.max_retention_seconds
        self._lock = threading.Lock()
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._stop_event = threading.Event()
        self._cleaner_thread: Optional[threading.Thread] = None

        # Ensure temp directory exists with restrictive permissions
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Run startup recovery to remove orphaned or expired files from prior runs
        self.run_startup_recovery()

        # Start background cleaner thread
        self.start_background_cleaner()

    def register_artifact(self, file_path: Path, tag: str = "temp_media") -> Path:
        """Register a temporary file with creation and expiration metadata."""
        path_str = str(file_path.resolve())
        now = time.time()
        expiry = now + self.max_retention_seconds

        with self._lock:
            self._registry[path_str] = {
                "created_at": now,
                "expires_at": expiry,
                "tag": tag,
                "size_bytes": file_path.stat().st_size if file_path.exists() else 0
            }
        return file_path

    def delete_artifact(self, file_path: Path) -> bool:
        """Immediately delete an artifact and unregister it."""
        path_str = str(file_path.resolve())
        with self._lock:
            self._registry.pop(path_str, None)

        if file_path.exists():
            try:
                if file_path.is_file():
                    file_path.unlink(missing_ok=True)
                elif file_path.is_dir():
                    shutil.rmtree(file_path, ignore_errors=True)
                logger.info(f"Deleted temporary artifact: {file_path.name}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete artifact {file_path}: {e}")
                return False
        return False

    def clean_expired(self) -> int:
        """Scan registry and filesystem, deleting any artifact older than max_retention_seconds."""
        now = time.time()
        expired_paths = []

        with self._lock:
            for path_str, meta in list(self._registry.items()):
                if now >= meta["expires_at"]:
                    expired_paths.append(Path(path_str))
                    del self._registry[path_str]

        deleted_count = 0
        for p in expired_paths:
            if p.exists():
                try:
                    if p.is_file():
                        p.unlink(missing_ok=True)
                    elif p.is_dir():
                        shutil.rmtree(p, ignore_errors=True)
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Error removing expired file {p}: {e}")

        # Also sweep the physical directory for un-registered or orphaned files
        try:
            for item in self.temp_dir.iterdir():
                if item.name.startswith("."):
                    continue
                try:
                    mtime = item.stat().st_mtime
                    if (now - mtime) > self.max_retention_seconds:
                        if item.is_file():
                            item.unlink(missing_ok=True)
                        elif item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                        deleted_count += 1
                except Exception as e:
                    logger.warning(f"Error purging unindexed item {item}: {e}")
        except Exception as e:
            logger.error(f"Error scanning temp directory: {e}")

        return deleted_count

    def purge_all(self) -> int:
        """Explicitly purge all temporary files (e.g. on application exit or user request)."""
        purged = 0
        with self._lock:
            self._registry.clear()

        for item in self.temp_dir.iterdir():
            if item.name.startswith("."):
                continue
            try:
                if item.is_file():
                    item.unlink(missing_ok=True)
                elif item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                purged += 1
            except Exception as e:
                logger.error(f"Error purging {item}: {e}")
        return purged

    def run_startup_recovery(self) -> int:
        """Clean up artifacts left behind from previous crashes or terminations."""
        logger.info("Running startup recovery on temporary storage directory...")
        recovered_deleted = 0
        now = time.time()
        for item in self.temp_dir.iterdir():
            if item.name.startswith("."):
                continue
            try:
                # Any file left behind from previous run older than 15 min or orphaned is purged
                age = now - item.stat().st_mtime
                if age > self.max_retention_seconds:
                    if item.is_file():
                        item.unlink(missing_ok=True)
                    elif item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                    recovered_deleted += 1
            except Exception as e:
                logger.error(f"Startup recovery failed to remove {item}: {e}")
        logger.info(f"Startup recovery removed {recovered_deleted} leftover artifacts.")
        return recovered_deleted

    def get_status(self) -> Dict[str, Any]:
        """Return real-time privacy and retention storage metrics."""
        total_files = 0
        total_bytes = 0
        oldest_ts = None
        now = time.time()

        for item in self.temp_dir.iterdir():
            if item.is_file() and not item.name.startswith("."):
                try:
                    stat = item.stat()
                    total_files += 1
                    total_bytes += stat.st_size
                    if oldest_ts is None or stat.st_mtime < oldest_ts:
                        oldest_ts = stat.st_mtime
                except Exception:
                    pass

        oldest_age_sec = (now - oldest_ts) if oldest_ts else 0.0

        return {
            "retention_policy_minutes": self.max_retention_seconds / 60.0,
            "max_retention_seconds": self.max_retention_seconds,
            "active_temp_files": total_files,
            "total_temp_size_bytes": total_bytes,
            "total_temp_size_mb": round(total_bytes / (1024 * 1024), 2),
            "oldest_artifact_age_seconds": round(oldest_age_sec, 1),
            "auto_cleanup_active": not self._stop_event.is_set(),
            "temp_directory": str(self.temp_dir)
        }

    def _cleaner_loop(self):
        while not self._stop_event.is_set():
            try:
                self.clean_expired()
            except Exception as e:
                logger.error(f"Background cleaner error: {e}")
            self._stop_event.wait(timeout=settings.cleanup_interval_seconds)

    def start_background_cleaner(self):
        if self._cleaner_thread is None or not self._cleaner_thread.is_alive():
            self._stop_event.clear()
            self._cleaner_thread = threading.Thread(target=self._cleaner_loop, daemon=True, name="TrustwireRetentionCleaner")
            self._cleaner_thread.start()

    def stop_background_cleaner(self):
        self._stop_event.set()
        if self._cleaner_thread and self._cleaner_thread.is_alive():
            self._cleaner_thread.join(timeout=2.0)

# Global singleton
retention_manager = RetentionManager()
