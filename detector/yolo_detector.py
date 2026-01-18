import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Optional
import time


class Detection:
    """Represents a single detection."""

    def __init__(self, class_name: str, confidence: float, bbox: Tuple[int, int, int, int], is_threat: bool):
        self.class_name = class_name
        self.confidence = confidence
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.is_threat = is_threat
        self.timestamp = time.time()


class WeaponDetector:
    """YOLOv8-based weapon and person detector."""

    # Classes that are considered threats (knives, scissors, and any sharp objects)
    # Using lowercase for matching
    THREAT_CLASSES = {"knife", "scissors", "fork", "baseball bat"}

    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """
        Initialize the detector.

        Args:
            model_path: Path to YOLO model or model name (yolov8n.pt, yolov8s.pt, etc.)
            confidence_threshold: Minimum confidence for detections
        """
        self.confidence_threshold = confidence_threshold
        print(f"Loading YOLO model: {model_path}")
        self.model = YOLO(model_path)
        self.class_names = self.model.names
        print(f"Model loaded with {len(self.class_names)} classes")
        # Print threat-related classes for debugging
        for idx, name in self.class_names.items():
            if any(threat in name.lower() for threat in ["knife", "scissors", "fork", "bat"]):
                print(f"  Threat class found: {idx} = {name}")

    def detect(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Detection]]:
        """
        Run detection on a frame.

        Args:
            frame: BGR image from OpenCV

        Returns:
            Tuple of (annotated_frame, list of detections)
        """
        detections = []

        # Run inference
        results = self.model(frame, verbose=False, conf=self.confidence_threshold)

        # Process results
        annotated_frame = frame.copy()

        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.class_names[class_id]

                # Determine if this is a threat (check if class name contains any threat word)
                class_lower = class_name.lower()
                is_threat = any(threat in class_lower for threat in self.THREAT_CLASSES)

                # Log threat detections
                if is_threat:
                    print(f"🚨 THREAT DETECTED: {class_name} (confidence: {confidence:.2f})")

                # Create detection object
                detection = Detection(
                    class_name=class_name,
                    confidence=confidence,
                    bbox=(x1, y1, x2, y2),
                    is_threat=is_threat
                )
                detections.append(detection)

                # Draw bounding box - RED for ALL threats
                if is_threat:
                    # Bright RED box for threats - thick and visible
                    color = (0, 0, 255)  # BGR format - pure red
                    thickness = 4
                elif class_lower == "person":
                    # Green box for people
                    color = (0, 255, 0)
                    thickness = 2
                else:
                    # Blue box for other objects
                    color = (255, 200, 0)
                    thickness = 1

                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, thickness)

                # Draw label
                label = f"{class_name}: {confidence:.2f}"
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1 - label_size[1] - 10),
                    (x1 + label_size[0], y1),
                    color,
                    -1
                )
                cv2.putText(
                    annotated_frame,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2
                )

        return annotated_frame, detections

    def get_threats(self, detections: List[Detection]) -> List[Detection]:
        """Filter detections to only threats."""
        return [d for d in detections if d.is_threat]
