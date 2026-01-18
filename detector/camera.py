import cv2
import threading
import time
from typing import Optional
import numpy as np


class CameraStream:
    """Handles RTSP camera stream with automatic reconnection."""

    def __init__(self, camera_id: str, name: str, url: str):
        self.camera_id = camera_id
        self.name = name
        self.url = url
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame: Optional[np.ndarray] = None
        self.running = False
        self.connected = False
        self.lock = threading.Lock()
        self.thread: Optional[threading.Thread] = None
        self.last_frame_time = 0
        self.fps = 0

    def start(self):
        """Start the camera stream in a background thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the camera stream."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.cap:
            self.cap.release()

    def _connect(self) -> bool:
        """Attempt to connect to the camera."""
        try:
            if self.cap:
                self.cap.release()

            # Set RTSP transport to TCP for more reliable streaming
            self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer for lower latency

            if self.cap.isOpened():
                self.connected = True
                print(f"[{self.name}] Connected to camera")
                return True
            else:
                self.connected = False
                print(f"[{self.name}] Failed to connect")
                return False
        except Exception as e:
            print(f"[{self.name}] Connection error: {e}")
            self.connected = False
            return False

    def _capture_loop(self):
        """Main capture loop running in background thread."""
        reconnect_delay = 1
        max_reconnect_delay = 30

        while self.running:
            if not self.connected:
                if self._connect():
                    reconnect_delay = 1
                else:
                    time.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)
                    continue

            try:
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        self.frame = frame
                        current_time = time.time()
                        if self.last_frame_time > 0:
                            self.fps = 1.0 / (current_time - self.last_frame_time)
                        self.last_frame_time = current_time
                else:
                    print(f"[{self.name}] Lost connection, reconnecting...")
                    self.connected = False
                    time.sleep(0.1)
            except Exception as e:
                print(f"[{self.name}] Capture error: {e}")
                self.connected = False
                time.sleep(0.1)

    def get_frame(self) -> Optional[np.ndarray]:
        """Get the latest frame from the camera."""
        with self.lock:
            if self.frame is not None:
                return self.frame.copy()
            return None

    def get_status(self) -> dict:
        """Get camera status information."""
        return {
            "id": self.camera_id,
            "name": self.name,
            "connected": self.connected,
            "fps": round(self.fps, 1)
        }
