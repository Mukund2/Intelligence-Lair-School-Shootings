# Intelligence Lair - School Threat Detection System

Real-time weapon detection system using AI vision to enhance school safety. Connects to existing camera infrastructure and provides instant alerts when threats are detected.

## Features

- **Live Camera Feeds**: Connect to multiple RTSP cameras
- **AI Weapon Detection**: YOLOv8-powered real-time detection
- **Visual Indicators**: Red bounding boxes on detected threats
- **Instant Alerts**: Dashboard alerts with audio notifications
- **Alert Management**: Acknowledge and track threat alerts

## Quick Start

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure cameras
cp .env.example .env
# Edit .env with your camera RTSP URLs

# 4. Run the server
python app.py
```

Open http://localhost:5000 to view the dashboard.

## Configuration

Edit `.env` with your camera RTSP URLs:

```
CAMERA_1_URL=rtsp://admin:password@192.168.1.100:554/stream1
CAMERA_2_URL=rtsp://admin:password@192.168.1.101:554/stream1
```

Edit `config.py` to customize:
- Camera names and IDs
- Detection confidence threshold
- Alert cooldown period

## Architecture

```
Camera (RTSP) → OpenCV → YOLOv8 Detection → Flask-SocketIO → Web Dashboard
                              ↓
                        Alert System → Push Notifications (Phase 2)
```

## Tech Stack

- **Backend**: Python, Flask, Flask-SocketIO
- **Vision AI**: YOLOv8 (Ultralytics)
- **Video Processing**: OpenCV
- **Real-time**: WebSockets
- **Frontend**: Vanilla JS with Socket.IO client

## Project Structure

```
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── detector/
│   ├── camera.py          # RTSP stream handler
│   ├── yolo_detector.py   # YOLOv8 detection
│   └── alert.py           # Alert management
├── templates/
│   └── dashboard.html     # Dashboard UI
└── requirements.txt
```

## Roadmap

- [x] Live camera feeds
- [x] YOLOv8 weapon detection
- [x] Web dashboard
- [x] Alert system
- [ ] Mobile app with push notifications
- [ ] Custom weapon detection model training
