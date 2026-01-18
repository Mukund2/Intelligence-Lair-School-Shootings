import cv2
import threading
import time
import os
from typing import Optional
import numpy as np

# Skip macOS camera authorization prompt (user must grant permission separately)
os.environ["OPENCV_AVFOUNDATION_SKIP_AUTH"] = "1"


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
        self.use_test_pattern = False

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

    def _generate_test_frame(self) -> np.ndarray:
        """Generate a test pattern frame for demo mode."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Dark background with grid
        frame[:] = (20, 20, 30)

        # Draw grid lines
        for i in range(0, 640, 40):
            cv2.line(frame, (i, 0), (i, 480), (40, 40, 50), 1)
        for i in range(0, 480, 40):
            cv2.line(frame, (0, i), (640, i), (40, 40, 50), 1)

        # Add camera name
        cv2.putText(frame, self.name, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "TEST PATTERN - No Camera", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)

        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(frame, timestamp, (520, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 0), 2)

        return frame

    def _connect(self) -> bool:
        """Attempt to connect to the camera."""
        try:
            if self.cap:
                self.cap.release()

            # Handle test pattern mode
            if self.url == "test":
                self.use_test_pattern = True
                self.connected = True
                print(f"[{self.name}] Using test pattern")
                return True

            # Handle webcam vs RTSP
            if self.url == "webcam":
                # Use default webcam (index 0)
                self.cap = cv2.VideoCapture(0)
                # If webcam fails, fall back to test pattern
                if not self.cap.isOpened():
                    print(f"[{self.name}] Webcam not available, using test pattern")
                    self.use_test_pattern = True
                    self.connected = True
                    return True
            else:
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
                # Handle test pattern mode
                if self.use_test_pattern:
                    frame = self._generate_test_frame()
                    with self.lock:
                        self.frame = frame
                        current_time = time.time()
                        if self.last_frame_time > 0:
                            self.fps = 1.0 / (current_time - self.last_frame_time)
                        self.last_frame_time = current_time
                    time.sleep(0.033)  # ~30 FPS for test pattern
                    continue

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
