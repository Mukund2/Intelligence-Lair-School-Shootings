import os
from dotenv import load_dotenv

load_dotenv()

# Demo mode: use webcam if no RTSP cameras configured
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# Camera configuration
# Format: {"name": "Camera Name", "url": "rtsp://..." or "webcam" for local camera}
if DEMO_MODE:
    # Demo mode: use webcam for all feeds (simulates multiple cameras)
    CAMERAS = [
        {
            "id": "cam1",
            "name": "Main Entrance",
            "url": "webcam"
        },
    ]
else:
    # Production mode: use RTSP cameras
    CAMERAS = [
        {
            "id": "cam1",
            "name": "Main Entrance",
            "url": os.getenv("CAMERA_1_URL", "rtsp://localhost:8554/stream1")
        },
        {
            "id": "cam2",
            "name": "Hallway A",
            "url": os.getenv("CAMERA_2_URL", "rtsp://localhost:8554/stream2")
        },
        {
            "id": "cam3",
            "name": "Cafeteria",
            "url": os.getenv("CAMERA_3_URL", "rtsp://localhost:8554/stream3")
        },
        {
            "id": "cam4",
            "name": "Parking Lot",
            "url": os.getenv("CAMERA_4_URL", "rtsp://localhost:8554/stream4")
        },
    ]

# Detection settings
DETECTION_CONFIDENCE = 0.35  # Lower threshold to catch more potential threats
WEAPON_CLASSES = ["knife", "scissors", "fork"]  # COCO classes that could be weapons

# Alert settings
ALERT_COOLDOWN = 10  # Seconds between alerts for same camera
