"""Trustwire Central Alert Hub & Event Dispatcher
Coordinates alerts across Video, Audio, and Financial Fraud detectors.
Implements deduplication, cooldown throttling, WebSocket broadcasting, and metadata persistence.
"""

import time
import json
import uuid
import logging
import threading
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field

from backend.config import settings

logger = logging.getLogger("trustwire.alerts")

class AlertItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    created_at_iso: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    category: str  # "video_deepfake", "audio_deepfake", "financial_fraud"
    severity: str  # "Informational", "Caution", "High", "Critical"
    title: str
    explanation: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    source: str  # "Live Monitoring", "Media Analysis"
    model_or_rule: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    suggested_action: str
    acknowledged: bool = False
    dismissed: bool = False
    repetition_count: int = 1

class AlertHub:
    """Thread-safe alert broker and metadata history store."""

    def __init__(self, store_dir: Optional[Path] = None, cooldown_seconds: float = 15.0):
        self.store_dir = Path(store_dir or settings.alerts_storage_dir)
        self.cooldown_seconds = cooldown_seconds
        self._lock = threading.Lock()
        self._alerts: List[AlertItem] = []
        self._cooldown_map: Dict[str, float] = {}  # key -> last_trigger_timestamp
        self._subscribers: Set[Any] = set()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self._history_file = self.store_dir / "alerts_history.json"
        self._load_history()

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        """Set the active asyncio event loop for thread-safe WebSocket broadcasts."""
        self._loop = loop

    def _load_history(self):
        """Load past alert metadata from storage."""
        if self._history_file.exists():
            try:
                data = json.loads(self._history_file.read_text(encoding="utf-8"))
                self._alerts = [AlertItem(**item) for item in data]
                logger.info(f"Loaded {len(self._alerts)} past alerts from storage.")
            except Exception as e:
                logger.error(f"Failed to load alert history: {e}")
                self._alerts = []

    def _save_history(self):
        """Persist alert metadata to JSON file (never raw media)."""
        try:
            # Keep at most 200 recent alerts in metadata history
            recent = self._alerts[-200:]
            data = [a.model_dump() for a in recent]
            self._history_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to save alert history: {e}")

    def add_subscriber(self, ws):
        """Add WebSocket client subscriber for real-time alert pushes."""
        with self._lock:
            self._subscribers.add(ws)

    def remove_subscriber(self, ws):
        with self._lock:
            self._subscribers.discard(ws)

    async def broadcast_alert(self, alert: AlertItem):
        """Push alert event to active WebSocket connections."""
        payload = json.dumps({"type": "NEW_ALERT", "alert": alert.model_dump()})
        dead_clients = []
        for client in list(self._subscribers):
            try:
                await client.send_text(payload)
            except Exception:
                dead_clients.append(client)
        with self._lock:
            for d in dead_clients:
                self._subscribers.discard(d)

    def dispatch_alert(
        self,
        category: str,
        severity: str,
        title: str,
        explanation: str,
        evidence: Dict[str, Any],
        source: str,
        model_or_rule: str,
        confidence_score: float,
        suggested_action: str
    ) -> Optional[AlertItem]:
        """Create, deduplicate, and record an alert item."""
        now = time.time()
        # Deduplication key based on category and title/primary trigger
        dedup_key = f"{category}:{title}"

        with self._lock:
            last_time = self._cooldown_map.get(dedup_key, 0.0)
            if (now - last_time) < self.cooldown_seconds:
                # Inside cooldown period: increment repetition on the most recent alert of this type
                for a in reversed(self._alerts):
                    if a.category == category and a.title == title and not a.dismissed:
                        a.repetition_count += 1
                        a.timestamp = now
                        a.created_at_iso = time.strftime("%Y-%m-%d %H:%M:%S")
                        self._save_history()
                        return None  # Suppress duplicate alert event

            # Create new alert item
            alert = AlertItem(
                category=category,
                severity=severity,
                title=title,
                explanation=explanation,
                evidence=evidence,
                source=source,
                model_or_rule=model_or_rule,
                confidence_score=round(confidence_score, 4),
                suggested_action=suggested_action,
                timestamp=now
            )
            self._alerts.append(alert)
            self._cooldown_map[dedup_key] = now
            self._save_history()

            # Broadcast over WebSocket only for real-time live monitoring alerts.
            # Offline media analysis alerts are saved to history but must not trigger live popups.
            if alert.source == "Live Monitoring":
                if self._loop and self._loop.is_running():
                    asyncio.run_coroutine_threadsafe(self.broadcast_alert(alert), self._loop)
                else:
                    try:
                        running_loop = asyncio.get_running_loop()
                        running_loop.create_task(self.broadcast_alert(alert))
                    except RuntimeError:
                        pass

            return alert

    def get_alerts(self, category: Optional[str] = None, severity: Optional[str] = None, include_dismissed: bool = False) -> List[AlertItem]:
        """Retrieve alerts with optional category/severity/dismissal filters."""
        with self._lock:
            results = []
            for a in reversed(self._alerts):
                if not include_dismissed and a.dismissed:
                    continue
                if category and a.category != category:
                    continue
                if severity and a.severity != severity:
                    continue
                results.append(a)
            return results

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark an alert as acknowledged."""
        with self._lock:
            for a in self._alerts:
                if a.id == alert_id:
                    a.acknowledged = True
                    self._save_history()
                    return True
        return False

    def dismiss_alert(self, alert_id: str) -> bool:
        """Mark an alert as dismissed."""
        with self._lock:
            for a in self._alerts:
                if a.id == alert_id:
                    a.dismissed = True
                    self._save_history()
                    return True
        return False

    def clear_all_alerts(self) -> int:
        """Clear all stored alerts."""
        with self._lock:
            count = len(self._alerts)
            self._alerts.clear()
            self._cooldown_map.clear()
            self._save_history()
            return count

# Global singleton
alert_hub = AlertHub()
