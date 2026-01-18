import cv2
import base64
import time
import threading
from flask import Flask, render_template, Response, jsonify
from flask_socketio import SocketIO, emit
from detector import CameraStream, WeaponDetector, AlertManager
import config

app = Flask(__name__)
app.config["SECRET_KEY"] = "intelligence-lair-secret"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Initialize components
detector = WeaponDetector(model_path="yolov8s.pt", confidence_threshold=config.DETECTION_CONFIDENCE)
alert_manager = AlertManager(cooldown_seconds=config.ALERT_COOLDOWN)
cameras: dict[str, CameraStream] = {}


def init_cameras():
    """Initialize all camera streams."""
    for cam_config in config.CAMERAS:
        camera = CameraStream(
            camera_id=cam_config["id"],
            name=cam_config["name"],
            url=cam_config["url"]
        )
        cameras[cam_config["id"]] = camera
        camera.start()
    print(f"Initialized {len(cameras)} cameras")


def process_camera(camera_id: str):
    """Process frames from a camera and emit to clients."""
    camera = cameras.get(camera_id)
    if not camera:
        return

    while True:
        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue

        # Run detection
        annotated_frame, detections = detector.detect(frame)

        # Check for threats
        threats = detector.get_threats(detections)
        for threat in threats:
            alert = alert_manager.check_and_alert(
                camera_id=camera_id,
                camera_name=camera.name,
                threat_type=threat.class_name,
                confidence=threat.confidence
            )
            if alert:
                # Emit alert to all clients
                socketio.emit("new_alert", alert.to_dict())

        # Encode frame to JPEG
        _, buffer = cv2.imencode(".jpg", annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        frame_base64 = base64.b64encode(buffer).decode("utf-8")

        # Emit frame to clients
        socketio.emit(f"frame_{camera_id}", {
            "camera_id": camera_id,
            "frame": frame_base64,
            "detections": len(detections),
            "threats": len(threats)
        })

        # Cap at ~15 FPS for WebSocket
        time.sleep(0.066)


@app.route("/")
def dashboard():
    """Main dashboard page."""
    return render_template("dashboard.html", cameras=config.CAMERAS)


@app.route("/api/cameras")
def get_cameras():
    """Get all camera statuses."""
    statuses = [cam.get_status() for cam in cameras.values()]
    return jsonify(statuses)


@app.route("/api/alerts")
def get_alerts():
    """Get recent alerts."""
    return jsonify(alert_manager.get_recent_alerts(20))


@app.route("/api/alerts/<alert_id>/acknowledge", methods=["POST"])
def acknowledge_alert(alert_id):
    """Acknowledge an alert."""
    success = alert_manager.acknowledge_alert(alert_id)
    return jsonify({"success": success})


@socketio.on("connect")
def handle_connect():
    """Handle client connection."""
    print("Client connected")
    # Send current camera statuses
    emit("camera_status", [cam.get_status() for cam in cameras.values()])


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection."""
    print("Client disconnected")


def start_processing():
    """Start processing threads for all cameras."""
    for camera_id in cameras:
        thread = threading.Thread(target=process_camera, args=(camera_id,), daemon=True)
        thread.start()


# Alert callback to emit via SocketIO
def on_alert(alert):
    socketio.emit("new_alert", alert.to_dict())


alert_manager.register_callback(on_alert)


if __name__ == "__main__":
    print("=" * 50)
    print("Intelligence Lair - School Threat Detection")
    print("=" * 50)

    # Initialize cameras
    init_cameras()

    # Start processing in background
    socketio.start_background_task(start_processing)

    # Run server
    print("\nStarting server on http://localhost:5001")
    socketio.run(app, host="0.0.0.0", port=5001, debug=False, allow_unsafe_werkzeug=True)
