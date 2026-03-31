# ynov-baby-vision

**Arbitrage IA — Babyfoot connecté Ynov Toulouse 2026**

Caméra au-dessus du terrain de babyfoot. Script Python utilisant **YOLOv8** (OpenCV) pour tracker la balle en temps réel, détecter les buts, et envoyer automatiquement les scores à l'API [BabyConnect](https://github.com/BabyConnect-Ynov2026/babyconnect).

---

## Fonctionnement

```
Caméra
  │
  ▼
YOLOv8 — détection de la balle (classe "sports ball")
  │
  ▼
GoalDetector — franchissement de ligne de but
  │
  ▼
API BabyConnect — PATCH /matches/:id/score
                  POST  /matches/:id/finish
```

1. La caméra capte le flux vidéo au-dessus du terrain
2. YOLOv8 détecte la balle à chaque frame
3. Le `GoalDetector` surveille deux lignes de but (configurables en pixels)
4. Quand la balle franchit une ligne → score envoyé à l'API automatiquement
5. Quand le score max est atteint → le match est clôturé (ELO calculé)

---

## Installation

```bash
# 1. Cloner le repo
git clone https://github.com/BabyConnect-Ynov2026/ynov-baby-vision.git
cd ynov-baby-vision

# 2. Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer
cp .env.example .env
# → Editer .env avec les bons paramètres
```

---

## Configuration (.env)

| Variable | Défaut | Description |
|----------|--------|-------------|
| `API_BASE_URL` | `http://localhost:8080/api/v1` | URL de l'API BabyConnect |
| `MATCH_ID` | `1` | ID du match en cours |
| `CAMERA_SOURCE` | `0` | `0` = webcam, ou chemin vers une vidéo |
| `YOLO_MODEL` | `yolov8n.pt` | Modèle YOLOv8 (téléchargé automatiquement) |
| `CONFIDENCE_THRESHOLD` | `0.5` | Seuil de confiance pour la détection |
| `GOAL_LEFT` | `100,0,100,480` | Ligne de but gauche `x1,y1,x2,y2` |
| `GOAL_RIGHT` | `540,0,540,480` | Ligne de but droite `x1,y1,x2,y2` |
| `WIN_SCORE` | `10` | Buts pour gagner |
| `DEBUG` | `true` | Affiche la fenêtre OpenCV |

---

## Lancer

```bash
# BabyConnect doit tourner en parallèle
# (créer un match via l'interface et noter son ID)

python main.py
```

En mode `DEBUG=true`, une fenêtre s'affiche avec :
- La balle entourée en vert
- Sa trajectoire (trail orange)
- Les lignes de but
- Le score en temps réel

Appuie sur **`q`** pour quitter.

---

## Calibration des lignes de but

Les coordonnées `GOAL_LEFT` et `GOAL_RIGHT` sont en **pixels** et dépendent de la résolution et du placement de la caméra.

Pour les calibrer :
1. Lance en mode `DEBUG=true` avec une vidéo de test
2. Note les coordonnées x des deux cages (ex: `x=120` pour la gauche, `x=520` pour la droite)
3. Mets à jour dans `.env` : `GOAL_LEFT=120,0,120,480`

---

## Structure

```
ynov-baby-vision/
├── main.py           # Point d'entrée — boucle principale
├── tracker.py        # Détection balle via YOLOv8
├── goal_detector.py  # Détection franchissement de ligne
├── api_client.py     # Client API BabyConnect
├── config.py         # Chargement .env
├── requirements.txt
└── .env.example
```
