import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Alert:
    """Represents a threat alert."""
    id: str
    camera_id: str
    camera_name: str
    threat_type: str
    confidence: float
    timestamp: float
    acknowledged: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "camera_id": self.camera_id,
            "camera_name": self.camera_name,
            "threat_type": self.threat_type,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "time_str": datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S"),
            "acknowledged": self.acknowledged
        }


class AlertManager:
    """Manages threat alerts with cooldown and logging."""

    def __init__(self, cooldown_seconds: float = 10.0):
        """
        Initialize alert manager.

        Args:
            cooldown_seconds: Minimum time between alerts for same camera
        """
        self.cooldown_seconds = cooldown_seconds
        self.last_alert_time: Dict[str, float] = {}
        self.alerts: List[Alert] = []
        self.alert_counter = 0
        self.callbacks: List[callable] = []

    def register_callback(self, callback: callable):
        """Register a callback to be called when new alert is triggered."""
        self.callbacks.append(callback)

    def check_and_alert(
        self,
        camera_id: str,
        camera_name: str,
        threat_type: str,
        confidence: float
    ) -> Optional[Alert]:
        """
        Check if we should create an alert (respecting cooldown).

        Returns Alert if created, None if in cooldown.
        """
        current_time = time.time()

        # Check cooldown
        last_time = self.last_alert_time.get(camera_id, 0)
        if current_time - last_time < self.cooldown_seconds:
            return None

        # Create alert
        self.alert_counter += 1
        alert = Alert(
            id=f"alert_{self.alert_counter}",
            camera_id=camera_id,
            camera_name=camera_name,
            threat_type=threat_type,
            confidence=confidence,
            timestamp=current_time
        )

        self.alerts.append(alert)
        self.last_alert_time[camera_id] = current_time

        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

        # Trigger callbacks
        for callback in self.callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"Alert callback error: {e}")

        print(f"🚨 ALERT: {threat_type} detected on {camera_name} (confidence: {confidence:.2f})")
        return alert

    def get_recent_alerts(self, count: int = 10) -> List[dict]:
        """Get the most recent alerts."""
        return [a.to_dict() for a in reversed(self.alerts[-count:])]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark an alert as acknowledged."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False

    def get_active_alert_count(self) -> int:
        """Get count of unacknowledged alerts."""
        return sum(1 for a in self.alerts if not a.acknowledged)
