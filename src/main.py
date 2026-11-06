"""Command-line demonstration for the VibeFinder music recommender."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.recommender import (
    RANKING_MODES,
    format_recommendations,
    load_songs,
    recommend_songs,
)

ROOT = Path(__file__).parents[1]

PROFILES = {
    "happy-pop": {
        "genre": "pop", "mood": "happy", "energy": 0.82, "tempo_bpm": 120,
        "valence": 0.85, "danceability": 0.8, "acousticness": 0.2,
        "popularity": 75, "release_decade": 2020,
    },
    "chill-lofi": {
        "genre": "lofi", "mood": "chill", "energy": 0.35, "tempo_bpm": 75,
        "valence": 0.55, "danceability": 0.5, "acousticness": 0.85,
        "popularity": 45, "release_decade": 2020,
    },
    "intense-rock": {
        "genre": "rock", "mood": "intense", "energy": 0.92, "tempo_bpm": 150,
        "valence": 0.45, "danceability": 0.6, "acousticness": 0.1,
        "popularity": 65, "release_decade": 2010,
    },
    "sad-workout": {
        "genre": "edm", "mood": "sad", "energy": 0.9, "tempo_bpm": 140,
        "valence": 0.25, "danceability": 0.85, "acousticness": 0.1,
        "popularity": 60, "release_decade": 2020,
    },
}


def parse_args() -> argparse.Namespace:
    """Parse profile, ranking mode, and result count from the command line."""

    parser = argparse.ArgumentParser(description="Run the VibeFinder music recommender")
    parser.add_argument("--profile", choices=PROFILES, default="happy-pop")
    parser.add_argument("--mode", choices=RANKING_MODES, default="balanced")
    parser.add_argument("--k", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    """Load the catalog, rank it for one profile, and print explanations."""

    args = parse_args()
    songs = load_songs(ROOT / "data/songs.csv")
    user_prefs = {**PROFILES[args.profile], "ranking_mode": args.mode}
    recommendations = recommend_songs(user_prefs, songs, k=args.k)
    print(f"Loaded songs: {len(songs)}")
    print(f"Profile: {args.profile} | Ranking mode: {args.mode}")
    print(format_recommendations(recommendations))


if __name__ == "__main__":
    main()
