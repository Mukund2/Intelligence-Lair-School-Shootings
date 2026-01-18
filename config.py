import os
from dotenv import load_dotenv

load_dotenv()

# Camera configuration
# Format: {"name": "Camera Name", "url": "rtsp://..."}
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
DETECTION_CONFIDENCE = 0.5  # Minimum confidence for detection
WEAPON_CLASSES = ["knife", "gun", "rifle", "pistol"]  # Classes to flag as threats

# Alert settings
ALERT_COOLDOWN = 10  # Seconds between alerts for same camera
