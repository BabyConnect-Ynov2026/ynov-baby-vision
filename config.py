"""Chargement de la configuration depuis les variables d'environnement."""

import os

from dotenv import load_dotenv

load_dotenv()


def parse_line(env_var: str, default: str) -> tuple[int, int, int, int]:
    """Parse une variable d'env au format 'x1,y1,x2,y2' en tuple d'entiers."""
    raw = os.getenv(env_var, default)
    x1, y1, x2, y2 = map(int, raw.split(","))
    return x1, y1, x2, y2


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080/api/v1")
MATCH_ID = int(os.getenv("MATCH_ID", "1"))

CAMERA_SOURCE = os.getenv("CAMERA_SOURCE", "0")
try:
    CAMERA_SOURCE = int(CAMERA_SOURCE)
except ValueError:
    pass  # chemin vidéo

YOLO_MODEL = os.getenv("YOLO_MODEL", "yolov8n.pt")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))

GOAL_LEFT = parse_line("GOAL_LEFT", "100,0,100,480")
GOAL_RIGHT = parse_line("GOAL_RIGHT", "540,0,540,480")

WIN_SCORE = int(os.getenv("WIN_SCORE", "10"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
