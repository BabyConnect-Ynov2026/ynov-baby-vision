import requests
import logging
from config import API_BASE_URL, MATCH_ID

logger = logging.getLogger(__name__)


def get_current_score() -> tuple[int, int]:
    """Récupère le score actuel du match depuis l'API."""
    try:
        res = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}", timeout=3)
        res.raise_for_status()
        match = res.json().get("match", {})
        return match.get("red_score", 0), match.get("blue_score", 0)
    except Exception as e:
        logger.error(f"Erreur récupération score: {e}")
        return 0, 0


def update_score(red: int, blue: int) -> bool:
    """Envoie le nouveau score à l'API BabyConnect."""
    try:
        res = requests.patch(
            f"{API_BASE_URL}/matches/{MATCH_ID}/score",
            json={"red_score": red, "blue_score": blue},
            timeout=3,
        )
        res.raise_for_status()
        logger.info(f"Score mis à jour: Rouge {red} - Bleu {blue}")
        return True
    except Exception as e:
        logger.error(f"Erreur mise à jour score: {e}")
        return False


def finish_match() -> bool:
    """Termine le match via l'API (calcule l'ELO)."""
    try:
        res = requests.post(
            f"{API_BASE_URL}/matches/{MATCH_ID}/finish",
            timeout=3,
        )
        res.raise_for_status()
        logger.info("Match terminé via API")
        return True
    except Exception as e:
        logger.error(f"Erreur fin de match: {e}")
        return False
