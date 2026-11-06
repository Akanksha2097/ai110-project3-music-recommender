from pathlib import Path

import pytest

from src.recommender import (
    Recommender,
    Song,
    UserProfile,
    format_recommendations,
    load_songs,
    recommend_songs,
    score_song,
)

ROOT = Path(__file__).parents[1]


def make_small_recommender() -> Recommender:
    songs = [
        Song(1, "Test Pop Track", "Artist A", "pop", "happy", 0.8, 120, 0.9, 0.8, 0.2),
        Song(2, "Chill Lofi Loop", "Artist B", "lofi", "chill", 0.4, 80, 0.6, 0.5, 0.9),
    ]
    return Recommender(songs)


def test_load_songs_converts_numbers_and_has_twenty_rows():
    songs = load_songs(ROOT / "data/songs.csv")
    assert len(songs) == 20
    assert isinstance(songs[0]["energy"], float)
    assert isinstance(songs[0]["popularity"], int)


def test_score_song_rewards_matching_preferences():
    songs = load_songs(ROOT / "data/songs.csv")
    profile = {"genre": "pop", "mood": "happy", "energy": 0.82}
    matching_score, reasons = score_song(profile, songs[0])
    other_score, _ = score_song(profile, songs[2])
    assert matching_score > other_score
    assert "genre match" in " ".join(reasons)
    assert "mood match" in " ".join(reasons)


def test_recommend_returns_songs_sorted_for_profile():
    user = UserProfile("pop", "happy", 0.8, False, target_tempo=120)
    results = make_small_recommender().recommend(user, k=2)
    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explanation_is_non_empty_and_score_based():
    user = UserProfile("pop", "happy", 0.8, False)
    recommender = make_small_recommender()
    explanation = recommender.explain_recommendation(user, recommender.songs[0])
    assert explanation.startswith("Score")
    assert "genre match" in explanation


def test_modes_change_ranking_behavior():
    songs = load_songs(ROOT / "data/songs.csv")
    base = {"genre": "rock", "mood": "happy", "energy": 0.8}
    genre_first = recommend_songs({**base, "ranking_mode": "genre_first"}, songs, k=3)
    mood_first = recommend_songs({**base, "ranking_mode": "mood_first"}, songs, k=3)
    assert genre_first[0][0]["genre"] == "rock"
    assert mood_first[0][0]["mood"] == "happy"


def test_artist_penalty_promotes_diversity():
    songs = load_songs(ROOT / "data/songs.csv")
    profile = {"genre": "pop", "mood": "happy", "energy": 0.8}
    results = recommend_songs(profile, songs, k=5, artist_penalty=5.0)
    first_three_artists = [song["artist"] for song, _, _ in results[:3]]
    assert len(set(first_three_artists)) == 3


def test_invalid_mode_and_k_are_rejected():
    song = load_songs(ROOT / "data/songs.csv")[0]
    with pytest.raises(ValueError, match="Unknown ranking mode"):
        score_song({"ranking_mode": "random"}, song)
    with pytest.raises(ValueError, match="at least 1"):
        recommend_songs({}, [song], k=0)


def test_formatted_table_contains_titles_scores_and_reasons():
    songs = load_songs(ROOT / "data/songs.csv")
    recommendations = recommend_songs({"genre": "pop"}, songs, k=2)
    table = format_recommendations(recommendations)
    assert "Song" in table
    assert "Score" in table
    assert "Why" in table
    assert recommendations[0][0]["title"] in table
