"""Détection et tracking de la balle de babyfoot avec YOLOv8."""

import cv2
import numpy as np
from ultralytics import YOLO

from config import YOLO_MODEL, CONFIDENCE_THRESHOLD

# ID de classe "sports ball" dans COCO dataset (utilisé par YOLOv8 de base)
SPORTS_BALL_CLASS_ID = 32


class BallTracker:
    """Détecte et tracke la balle de babyfoot avec YOLOv8."""

    def __init__(self):
        self.model = YOLO(YOLO_MODEL)
        self.last_position: tuple[int, int] | None = None
        self.trail: list[tuple[int, int]] = []  # historique des positions
        self.trail_length = 15

    def detect(self, frame: np.ndarray) -> tuple[int, int] | None:
        """
        Détecte la balle dans le frame.
        Retourne (cx, cy) centre de la balle, ou None si non détectée.
        """
        results = self.model(frame, verbose=False, conf=CONFIDENCE_THRESHOLD)

        best_ball = None
        best_conf = 0.0

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])

                # On cherche "sports ball" — si modèle custom, adapter cls
                if cls == SPORTS_BALL_CLASS_ID and conf > best_conf:
                    best_conf = conf
                    best_ball = box.xyxy[0].cpu().numpy()

        if best_ball is not None:
            x1, y1, x2, y2 = best_ball
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)
            self.last_position = (cx, cy)
            self.trail.append((cx, cy))
            if len(self.trail) > self.trail_length:
                self.trail.pop(0)
            return cx, cy

        return None

    def draw(self, frame: np.ndarray) -> np.ndarray:
        """Dessine la position de la balle et sa trajectoire sur le frame."""
        # Trajectoire (trail)
        for i, point in enumerate(self.trail):
            alpha = int(255 * (i + 1) / len(self.trail))
            radius = max(2, int(8 * (i + 1) / len(self.trail)))
            cv2.circle(frame, point, radius, (0, alpha, 255), -1)

        # Position actuelle
        if self.last_position:
            cx, cy = self.last_position
            cv2.circle(frame, (cx, cy), 12, (0, 255, 0), 2)
            cv2.putText(
                frame, "BALLE", (cx - 25, cy - 16),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
            )

        return frame
