# VibeFinder 1.0 - Music Recommender Simulation

VibeFinder is a transparent, content-based music recommender built for the CodePath AI110 Project 3 assignment. It loads a 20-song CSV catalog, compares song features with a listener profile, ranks every song, applies an artist-diversity penalty, and prints the top results with score-based explanations.

## How recommendation systems work

Real streaming platforms can combine **collaborative filtering** (patterns from likes, skips, replays, and playlists across many users) with **content-based filtering** (attributes such as genre, mood, tempo, and audio characteristics). Those observations are input data. A listener's history or chosen targets represent preferences. A ranking algorithm turns the inputs and preferences into scores, sorts eligible songs, and selects the highest-ranked results.

VibeFinder simulates only the content-based part. It does not learn from real people or claim to reproduce Spotify or YouTube. Each song has genre, mood, energy, tempo, valence, danceability, acousticness, popularity, release decade, and instrumentalness. A profile stores target values for the same features.

## Algorithm recipe

For every song, the balanced strategy:

- awards `+2.0` for an exact genre match and `+1.5` for an exact mood match;
- rewards closeness to energy, tempo, valence, danceability, acousticness, popularity, decade, and instrumentalness targets;
- sorts all songs by their combined score;
- subtracts `0.75` when an artist has already appeared, reducing repetitive top results;
- returns the requested top-k with every contribution shown as a reason.

The `genre_first`, `mood_first`, and `energy_first` strategies use the same features but change their weights. They implement a Strategy-style design through the `RANKING_MODES` configuration, and users select a strategy with `--mode`.

```text
CSV catalog -> validate and convert features -> score every song
            -> apply artist-diversity penalty -> sort -> explained top-k table
```

## Dataset

`data/songs.csv` contains 20 fictional songs across pop, lofi, rock, ambient, jazz, synthwave, indie pop, EDM, folk, hip-hop, disco, and world music. The six enriched attributes beyond the core genre/mood/energy/tempo features are valence, danceability, acousticness, popularity, release decade, and instrumentalness. They are all loaded as numeric data and used by the scoring function.

## Setup and commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
pytest -q
```

Try different profiles and strategies:

```bash
python -m src.main --profile happy-pop --mode balanced --k 5
python -m src.main --profile chill-lofi --mode mood_first --k 5
python -m src.main --profile intense-rock --mode genre_first --k 5
python -m src.main --profile sad-workout --mode energy_first --k 5
```

## Sample recommendation output

The CLI uses a formatted ASCII table; these compact excerpts preserve the actual ranked results and reasons.

### Happy Pop

```text
Loaded songs: 20
Profile: happy-pop | Ranking mode: balanced
1. Sunrise City      | 9.31 | genre match +2.0; mood match +1.5; energy similarity +2.00
2. Golden Hour Drive | 8.32 | genre match +2.0; mood match +1.5; artist diversity -0.75
3. Gym Hero          | 7.30 | genre match +2.0; energy similarity +1.78
```

### Chill Lofi

```text
Loaded songs: 20
Profile: chill-lofi | Ranking mode: balanced
1. Library Rain       | 9.04 | genre match +2.0; mood match +1.5; energy similarity +2.00
2. Midnight Coding    | 8.81 | genre match +2.0; mood match +1.5; acousticness similarity +0.52
3. Spacewalk Thoughts | 6.63 | mood match +1.5; energy similarity +1.86
```

### Intense Rock

```text
Loaded songs: 20
Profile: intense-rock | Ranking mode: balanced
1. Storm Runner | 9.24 | genre match +2.0; mood match +1.5; energy similarity +1.98
2. Fireline     | 8.26 | genre match +2.0; mood match +1.5; artist diversity -0.75
3. Gym Hero     | 6.57 | mood match +1.5; energy similarity +1.98
```

The profile comparison behaves as expected: Happy Pop selects bright pop tracks, Chill Lofi shifts toward low-energy acoustic/instrumental tracks, and Intense Rock favors fast, high-energy rock. Storm Runner ranks first for Intense Rock because it matches both categorical preferences and is almost exactly at the energy and tempo targets.

## Experiments

I tested an adversarial `sad-workout` profile with high energy, low valence, and an EDM preference. In `energy_first` mode, Afterglow Signal ranked first because it combines sad mood, EDM genre, 0.88 energy, and 138 BPM. This shows that apparently conflicting preferences can still be represented when features are scored independently.

I also shifted the Happy Pop profile from `genre_first` to `energy_first`. Genre-first kept three pop songs in the top three. Energy-first moved the non-pop but similarly energetic Rooftop Lights into third place. The change made the list more exploratory but less strict about genre, demonstrating that weights change what “relevant” means rather than making results universally better.

## Tests

The tests cover CSV loading and numeric conversion, preference-sensitive scoring, sorted OOP output, explanations, ranking strategies, artist diversity, invalid inputs, and table formatting.

```text
........                                                                 [100%]
8 passed
```

## Limitations and risks

- The catalog is small, fictional, and manually balanced rather than representative of real listening behavior.
- Exact genre and mood labels can create filter bubbles and miss cross-genre songs.
- Popularity is a synthetic feature and can reinforce mainstream preferences if overweighted.
- The artist penalty improves variety but does not measure fairness across cultures, languages, or creators.
- The system has no listening history, collaborative signals, lyrics, context, or learned ground truth.

See the complete [Model Card](model_card.md) and [AI Interactions Log](ai_interactions.md).

## Reflection

My biggest learning was that ranking is a design choice, not an objective truth. A simple weighted formula can feel personalized, but the result depends on which features exist and how strongly each one is valued. Explanations and multiple strategies made those assumptions visible.

AI assistance accelerated the data expansion, implementation, edge-case brainstorming, and documentation audit. I still had to verify numeric conversions, compare actual outputs, correct overly strong diversity-test assumptions, and reject the idea that a more complex or more energetic ranking is automatically better. If I continued, I would evaluate with real listener feedback and measure catalog coverage alongside relevance.
