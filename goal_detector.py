import cv2
import numpy as np
import time
import logging
from config import GOAL_LEFT, GOAL_RIGHT, WIN_SCORE

logger = logging.getLogger(__name__)

# Délai minimum entre deux buts (évite les double-détections)
GOAL_COOLDOWN_SEC = 3.0


class GoalDetector:
    """
    Détecte quand la balle franchit une ligne de but.

    Convention :
      - Equipe Rouge marque quand la balle passe la ligne DROITE
      - Equipe Bleue marque quand la balle passe la ligne GAUCHE
    """

    def __init__(self):
        self.red_score = 0
        self.blue_score = 0
        self._last_goal_time = 0.0
        self._prev_position: tuple[int, int] | None = None

    def _crosses_line(
        self,
        prev: tuple[int, int],
        curr: tuple[int, int],
        line: tuple[int, int, int, int],
    ) -> bool:
        """
        Vérifie si le segment prev→curr croise la ligne de but (segment vertical).
        Utilise le produit vectoriel pour détecter l'intersection.
        """
        x1, y1, x2, y2 = line
        px, py = prev
        cx, cy = curr

        # Produit vectoriel pour tester l'intersection
        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        d1 = cross((x1, y1), (x2, y2), (px, py))
        d2 = cross((x1, y1), (x2, y2), (cx, cy))

        if (d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0):
            d3 = cross((px, py), (cx, cy), (x1, y1))
            d4 = cross((px, py), (cx, cy), (x2, y2))
            if (d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0):
                return True

        return False

    def update(self, ball_pos: tuple[int, int] | None) -> str | None:
        """
        Met à jour le détecteur avec la nouvelle position de la balle.
        Retourne "red", "blue", ou None selon qui a marqué.
        """
        if ball_pos is None:
            self._prev_position = None
            return None

        if self._prev_position is None:
            self._prev_position = ball_pos
            return None

        now = time.time()
        if now - self._last_goal_time < GOAL_COOLDOWN_SEC:
            self._prev_position = ball_pos
            return None

        scorer = None

        if self._crosses_line(self._prev_position, ball_pos, GOAL_RIGHT):
            self.red_score += 1
            scorer = "red"
            logger.info(f"BUT ROUGE ! Score: {self.red_score} - {self.blue_score}")

        elif self._crosses_line(self._prev_position, ball_pos, GOAL_LEFT):
            self.blue_score += 1
            scorer = "blue"
            logger.info(f"BUT BLEU ! Score: {self.red_score} - {self.blue_score}")

        if scorer:
            self._last_goal_time = now

        self._prev_position = ball_pos
        return scorer

    def is_match_over(self) -> str | None:
        """Retourne le gagnant si le score max est atteint, sinon None."""
        if self.red_score >= WIN_SCORE:
            return "red"
        if self.blue_score >= WIN_SCORE:
            return "blue"
        return None

    def draw(self, frame: np.ndarray) -> np.ndarray:
        """Dessine les lignes de but et le score sur le frame."""
        # Ligne gauche (Bleu marque ici)
        x1, y1, x2, y2 = GOAL_LEFT
        cv2.line(frame, (x1, y1), (x2, y2), (255, 100, 100), 2)
        cv2.putText(frame, "BUT BLEU", (x1 + 5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 100), 1)

        # Ligne droite (Rouge marque ici)
        x1, y1, x2, y2 = GOAL_RIGHT
        cv2.line(frame, (x1, y1), (x2, y2), (100, 100, 255), 2)
        cv2.putText(frame, "BUT ROUGE", (x1 - 90, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 1)

        # Score en haut au centre
        score_text = f"ROUGE {self.red_score}  -  {self.blue_score} BLEU"
        h, w = frame.shape[:2]
        cv2.rectangle(frame, (w // 2 - 140, 5), (w // 2 + 140, 35), (0, 0, 0), -1)
        cv2.putText(frame, score_text, (w // 2 - 130, 27),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return frame
