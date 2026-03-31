"""Client HTTP pour communiquer avec l'API BabyConnect."""

import logging

import requests

from config import API_BASE_URL, MATCH_ID

logger = logging.getLogger(__name__)


def get_current_score() -> tuple[int, int]:
    """Récupère le score actuel du match depuis l'API."""
    try:
        res = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}", timeout=3)
        res.raise_for_status()
        match = res.json().get("match", {})
        return match.get("red_score", 0), match.get("blue_score", 0)
    except requests.exceptions.RequestException as e:
        logger.error("Erreur récupération score: %s", e)
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
        logger.info("Score mis à jour: Rouge %s - Bleu %s", red, blue)
        return True
    except requests.exceptions.RequestException as e:
        logger.error("Erreur mise à jour score: %s", e)
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
    except requests.exceptions.RequestException as e:
        logger.error("Erreur fin de match: %s", e)
        return False
