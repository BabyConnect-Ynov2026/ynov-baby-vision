"""
ynov-baby-vision — Arbitrage IA pour babyfoot connecté
-------------------------------------------------------
Caméra au-dessus du terrain. Détecte la balle avec YOLOv8,
repère les franchissements de ligne de but, et envoie les scores
automatiquement à l'API BabyConnect.
"""

import cv2
import logging
import sys
import time

from config import CAMERA_SOURCE, DEBUG
from tracker import BallTracker
from goal_detector import GoalDetector
from api_client import get_current_score, update_score, finish_match

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Démarrage de ynov-baby-vision...")

    cap = cv2.VideoCapture(CAMERA_SOURCE)
    if not cap.isOpened():
        logger.error(f"Impossible d'ouvrir la caméra/vidéo : {CAMERA_SOURCE}")
        sys.exit(1)

    tracker = BallTracker()
    detector = GoalDetector()

    # Synchronise le score local avec l'API au démarrage
    red, blue = get_current_score()
    detector.red_score = red
    detector.blue_score = blue
    logger.info(f"Score initial récupéré depuis l'API: Rouge {red} - Bleu {blue}")

    last_api_update = 0.0
    API_UPDATE_INTERVAL = 1.0  # Envoie le score à l'API max 1 fois/seconde

    logger.info("Analyse vidéo en cours... (Appuie sur 'q' pour quitter)")

    while True:
        ret, frame = cap.read()
        if not ret:
            logger.warning("Fin du flux vidéo.")
            break

        # 1. Détecter la balle
        ball_pos = tracker.detect(frame)

        # 2. Vérifier les buts
        scorer = detector.update(ball_pos)

        if scorer:
            logger.info(f"BUT détecté par la caméra ! Equipe : {scorer.upper()}")
            now = time.time()
            if now - last_api_update >= API_UPDATE_INTERVAL:
                update_score(detector.red_score, detector.blue_score)
                last_api_update = now

        # 3. Vérifier fin de match
        winner = detector.is_match_over()
        if winner:
            logger.info(f"Match terminé ! Vainqueur : {winner.upper()}")
            update_score(detector.red_score, detector.blue_score)
            finish_match()
            if DEBUG:
                cv2.putText(
                    frame,
                    f"MATCH TERMINE - {'ROUGE' if winner == 'red' else 'BLEU'} GAGNE !",
                    (50, frame.shape[0] // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3,
                )
                cv2.imshow("ynov-baby-vision", frame)
                cv2.waitKey(3000)
            break

        # 4. Affichage debug
        if DEBUG:
            frame = tracker.draw(frame)
            frame = detector.draw(frame)

            cv2.putText(
                frame, "ynov-baby-vision | q = quitter", (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1,
            )
            cv2.imshow("ynov-baby-vision", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                logger.info("Arrêt demandé par l'utilisateur.")
                break

    cap.release()
    cv2.destroyAllWindows()
    logger.info("ynov-baby-vision arrêté.")


if __name__ == "__main__":
    main()
