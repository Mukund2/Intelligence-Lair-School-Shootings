# Intelligence Layer - School Threat Detection Platform

## Important Rules

**NEVER ask "should I run this?" or "do you want me to test this?" - JUST RUN IT.**

Always run, test, and verify code yourself. Don't ask for permission to execute.

---

## Overview

Palantir-style intelligence dashboard for school safety. Connects to existing camera systems, uses AI vision to detect weapons/threats, and alerts staff in real-time.

**CruzHacks 2026** - Justice Hacks track

## Quick Start

```bash
cd ~/Intelligence-Lair-School-Shootings
source venv/bin/activate
python app.py
```

Server runs at: http://localhost:5001

## Features (Implemented)

### Live Camera Dashboard
- Real-time video feed via WebSocket
- Support for RTSP streams, webcam, or test pattern fallback
- 15 FPS streaming to browser

### YOLOv8 Weapon Detection
- Model: `yolov8s.pt` (80 COCO classes)
- Detects: knife, scissors, fork, baseball bat
- Confidence threshold: 20% (tuned for scissors)
- Bounding boxes: **RED** for threats, **GREEN** for people

### Threat Alert System
- Real-time alerts panel with audio notification
- 30-second cooldown per camera + threat type (prevents spam)
- Threat level indicator: SAFE / ELEVATED / HIGH / CRITICAL
- Based on CURRENT live detections (resets when threat leaves frame)

### Stats Display
- People count (live)
- Objects count (excludes people and threats)
- Threats (session total)
- Uptime timer

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.13 + Flask |
| Real-time | Flask-SocketIO (threading mode) |
| Vision AI | YOLOv8s (Ultralytics) |
| Camera | OpenCV (RTSP, webcam, test pattern) |
| Frontend | Vanilla JS + WebSocket |

## Project Structure

```
~/Intelligence-Lair-School-Shootings/
├── app.py                 # Main Flask server
├── config.py              # Camera URLs, detection settings
├── requirements.txt       # Python dependencies
├── detector/
│   ├── __init__.py
│   ├── camera.py          # RTSP/webcam stream handler
│   ├── yolo_detector.py   # YOLOv8 weapon detection
│   └── alert.py           # Alert management with cooldown
├── templates/
│   └── dashboard.html     # Main dashboard page
└── CLAUDE.md              # This file
```

## Configuration

### config.py
```python
DEMO_MODE = True           # Use webcam instead of RTSP
DETECTION_CONFIDENCE = 0.20  # Low threshold to catch scissors
WEAPON_CLASSES = ["knife", "scissors", "fork", "baseball bat"]
ALERT_COOLDOWN = 30        # Seconds between alerts for same threat
```

### Environment Variables (Production)
```
DEMO_MODE=false
CAMERA_1_URL=rtsp://...
CAMERA_2_URL=rtsp://...
```

## Dependencies

```
flask
flask-socketio
opencv-python
ultralytics>=8.4.5
numpy
python-dotenv
```

Install: `pip install -r requirements.txt`

## Known Issues & Fixes

| Issue | Solution |
|-------|----------|
| Eventlet incompatible with Python 3.13 | Use `async_mode="threading"` |
| PyTorch 2.6 weights_only error | Upgrade ultralytics to 8.4.5+ |
| Port 5000 in use (macOS AirPlay) | Use port 5001 |
| Webcam permission denied | Grant Terminal camera access in System Settings, or uses test pattern fallback |
| Scissors not detecting | Use yolov8s (not yolov8n), lower confidence to 20% |

## Phase 2 (Not Built)

- Mobile app with push notifications (Amber Alert style)
- Firebase Cloud Messaging integration
- "I'm Safe" check-in button
- Multi-camera grid view

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/api/cameras` | GET | Camera statuses |
| `/api/alerts` | GET | Recent alerts (last 20) |
| `/api/alerts/<id>/acknowledge` | POST | Acknowledge alert |

## WebSocket Events

| Event | Direction | Data |
|-------|-----------|------|
| `frame_{camera_id}` | Server → Client | `{camera_id, frame (base64), detections, people, threats}` |
| `new_alert` | Server → Client | `{id, camera_id, camera_name, threat_type, confidence, timestamp}` |
| `camera_status` | Server → Client | Array of camera statuses |

## Demo Tips

1. Use scissors for reliable detection (knife/fork harder to detect)
2. Hold object clearly visible to camera
3. Threat level updates in real-time
4. Same threat won't spam alerts (30s cooldown)
5. Refresh browser if video freezes

## Commands

```bash
# Start server
python app.py

# Kill stuck processes
lsof -i :5001 | awk 'NR>1 {print $2}' | xargs kill -9

# Check camera access
# System Settings → Privacy & Security → Camera → Terminal
```
