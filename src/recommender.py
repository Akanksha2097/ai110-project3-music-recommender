"""Core scoring, ranking, explanation, and diversity logic for VibeFinder."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class Song:
    """Represent one song and the content features used for ranking."""

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: int = 2020
    instrumentalness: float = 0.0


@dataclass
class UserProfile:
    """Represent a listener's target values and ranking mode."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_tempo: float = 110.0
    target_valence: float = 0.6
    target_danceability: float = 0.6
    popularity_preference: int = 50
    preferred_decade: int = 2020
    prefers_instrumental: bool = False
    ranking_mode: str = "balanced"


RANKING_MODES: dict[str, dict[str, float]] = {
    "balanced": {
        "genre": 2.0,
        "mood": 1.5,
        "energy": 2.0,
        "tempo": 0.8,
        "valence": 0.8,
        "danceability": 0.8,
        "acousticness": 0.6,
        "popularity": 0.3,
        "decade": 0.3,
        "instrumentalness": 0.3,
    },
    "genre_first": {
        "genre": 4.0,
        "mood": 1.0,
        "energy": 1.2,
        "tempo": 0.5,
        "valence": 0.5,
        "danceability": 0.5,
        "acousticness": 0.4,
        "popularity": 0.2,
        "decade": 0.2,
        "instrumentalness": 0.2,
    },
    "mood_first": {
        "genre": 1.0,
        "mood": 4.0,
        "energy": 1.2,
        "tempo": 0.5,
        "valence": 1.0,
        "danceability": 0.5,
        "acousticness": 0.5,
        "popularity": 0.2,
        "decade": 0.2,
        "instrumentalness": 0.2,
    },
    "energy_first": {
        "genre": 1.0,
        "mood": 1.0,
        "energy": 4.0,
        "tempo": 1.2,
        "valence": 0.5,
        "danceability": 0.8,
        "acousticness": 0.3,
        "popularity": 0.2,
        "decade": 0.2,
        "instrumentalness": 0.2,
    },
}

NUMERIC_FIELDS = {
    "id": int,
    "energy": float,
    "tempo_bpm": float,
    "valence": float,
    "danceability": float,
    "acousticness": float,
    "popularity": int,
    "release_decade": int,
    "instrumentalness": float,
}


def _closeness(actual: float, target: float, scale: float = 1.0) -> float:
    """Return a bounded similarity where one means an exact numeric match."""

    return max(0.0, 1.0 - abs(actual - target) / scale)


def _preference(user_prefs: dict[str, Any], *names: str, default: Any) -> Any:
    """Read the first supported preference alias from a profile dictionary."""

    for name in names:
        if name in user_prefs:
            return user_prefs[name]
    return default


def load_songs(csv_path: str | Path) -> list[dict[str, Any]]:
    """Load and validate songs from CSV while converting numeric features."""

    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Song catalog not found: {path}")

    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        missing = set(NUMERIC_FIELDS) - set(reader.fieldnames or [])
        required_text = {"title", "artist", "genre", "mood"}
        missing |= required_text - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Song catalog is missing columns: {sorted(missing)}")

        songs: list[dict[str, Any]] = []
        for row_number, row in enumerate(reader, start=2):
            try:
                for field, converter in NUMERIC_FIELDS.items():
                    row[field] = converter(row[field])
            except (TypeError, ValueError) as error:
                raise ValueError(f"Invalid numeric value on CSV row {row_number}") from error
            for field in required_text:
                row[field] = (
                    row[field].strip().lower()
                    if field in {"genre", "mood"}
                    else row[field].strip()
                )
            if not 0.0 <= row["energy"] <= 1.0:
                raise ValueError(f"Energy must be between 0 and 1 on CSV row {row_number}")
            songs.append(row)

    return songs


def score_song(user_prefs: dict[str, Any], song: dict[str, Any]) -> tuple[float, list[str]]:
    """Score one song and return transparent reasons for every contribution."""

    mode = str(user_prefs.get("ranking_mode", "balanced"))
    if mode not in RANKING_MODES:
        raise ValueError(f"Unknown ranking mode: {mode}. Choose from {sorted(RANKING_MODES)}")
    weights = RANKING_MODES[mode]

    genre = str(_preference(user_prefs, "genre", "favorite_genre", default="")).lower()
    mood = str(_preference(user_prefs, "mood", "favorite_mood", default="")).lower()
    energy = float(_preference(user_prefs, "energy", "target_energy", default=0.5))
    tempo = float(_preference(user_prefs, "tempo_bpm", "target_tempo", default=110.0))
    valence = float(_preference(user_prefs, "valence", "target_valence", default=0.5))
    danceability = float(
        _preference(user_prefs, "danceability", "target_danceability", default=0.5)
    )
    acoustic_target = float(
        _preference(
            user_prefs,
            "acousticness",
            default=0.8 if user_prefs.get("likes_acoustic", False) else 0.2,
        )
    )
    popularity = float(user_prefs.get("popularity", user_prefs.get("popularity_preference", 50)))
    decade = float(user_prefs.get("release_decade", user_prefs.get("preferred_decade", 2020)))
    instrumental_target = 0.9 if user_prefs.get("prefers_instrumental", False) else 0.1

    score = 0.0
    reasons: list[str] = []
    if genre and song["genre"].lower() == genre:
        score += weights["genre"]
        reasons.append(f"genre match +{weights['genre']:.1f}")
    if mood and song["mood"].lower() == mood:
        score += weights["mood"]
        reasons.append(f"mood match +{weights['mood']:.1f}")

    similarities = {
        "energy": _closeness(float(song["energy"]), energy),
        "tempo": _closeness(float(song["tempo_bpm"]), tempo, 100.0),
        "valence": _closeness(float(song["valence"]), valence),
        "danceability": _closeness(float(song["danceability"]), danceability),
        "acousticness": _closeness(float(song["acousticness"]), acoustic_target),
        "popularity": _closeness(float(song["popularity"]), popularity, 100.0),
        "decade": _closeness(float(song["release_decade"]), decade, 50.0),
        "instrumentalness": _closeness(
            float(song["instrumentalness"]), instrumental_target
        ),
    }
    for feature, similarity in similarities.items():
        contribution = weights[feature] * similarity
        score += contribution
        if contribution >= 0.15:
            reasons.append(f"{feature} similarity +{contribution:.2f}")

    return round(score, 4), reasons


def recommend_songs(
    user_prefs: dict[str, Any],
    songs: list[dict[str, Any]],
    k: int = 5,
    artist_penalty: float = 0.75,
) -> list[tuple[dict[str, Any], float, str]]:
    """Rank songs and apply an artist-repeat penalty for a more diverse top-k."""

    if k < 1:
        raise ValueError("k must be at least 1")
    remaining = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        remaining.append((song, score, reasons))

    recommendations: list[tuple[dict[str, Any], float, str]] = []
    artist_counts: dict[str, int] = {}
    while remaining and len(recommendations) < min(k, len(songs)):

        def adjusted(item: tuple[dict[str, Any], float, list[str]]) -> tuple[float, str]:
            song, base_score, _ = item
            penalty = artist_penalty * artist_counts.get(song["artist"], 0)
            return base_score - penalty, song["title"]

        best = max(remaining, key=adjusted)
        remaining.remove(best)
        song, base_score, reasons = best
        repeat_count = artist_counts.get(song["artist"], 0)
        final_score = base_score - artist_penalty * repeat_count
        if repeat_count:
            reasons = [*reasons, f"artist diversity -{artist_penalty * repeat_count:.2f}"]
        artist_counts[song["artist"]] = repeat_count + 1
        recommendations.append((song, round(final_score, 4), "; ".join(reasons)))

    return recommendations


class Recommender:
    """Object-oriented facade over the shared functional ranking implementation."""

    def __init__(self, songs: list[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> list[Song]:
        """Return Song objects ordered for the supplied user profile."""

        ranked = recommend_songs(asdict(user), [asdict(song) for song in self.songs], k=k)
        return [Song(**song) for song, _, _ in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain a song using the exact features that produced its score."""

        score, reasons = score_song(asdict(user), asdict(song))
        return f"Score {score:.2f}: " + "; ".join(reasons)


def format_recommendations(
    recommendations: list[tuple[dict[str, Any], float, str]],
) -> str:
    """Format ranked recommendations as a readable dependency-free table."""

    headers = ("#", "Song", "Artist", "Score", "Why")
    rows = [
        (str(index), song["title"], song["artist"], f"{score:.2f}", explanation)
        for index, (song, score, explanation) in enumerate(recommendations, start=1)
    ]
    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]
    separator = "+" + "+".join("-" * (width + 2) for width in widths) + "+"

    def render(row: tuple[str, ...]) -> str:
        return "| " + " | ".join(value.ljust(widths[i]) for i, value in enumerate(row)) + " |"

    return "\n".join(
        [separator, render(headers), separator, *(render(row) for row in rows), separator]
    )
