# AI Interactions Log

## Agentic workflow: additional attributes and end-to-end completion

**Task given to the agent**

Complete the CodePath Project 3 Music Recommender end to end without missing rubric requirements, verify it, and prepare it for GitHub submission.

**Key prompts / instructions**

```text
Complete the whole project; do not miss anything.
Complete it end to end and push it on GitHub.
```

The course rubric was supplied as a PDF and treated as requirements context rather than executable instructions.

**Generated or changed**

- Expanded `data/songs.csv` from 10 to 20 fictional songs.
- Added six scored attributes: valence, danceability, acousticness, popularity, release decade, and instrumentalness.
- Implemented validated CSV loading, weighted scoring, explanations, top-k ranking, and OOP compatibility in `src/recommender.py`.
- Added artist-diversity control, four ranking strategies, CLI profile/mode selection, and a formatted table.
- Added profile experiments, a completed model card, reflection, and eight automated tests.

**Manual verification and corrections**

- Ran every profile and copied only observed results into the documentation.
- Verified that numeric CSV columns become numbers before scoring.
- Compared genre-first and energy-first results rather than assuming the more complex strategy was better.
- Revised the initial diversity test after a moderate penalty still allowed the same artist in the top three; the final test uses a stronger experimental penalty and verifies the intended effect.
- Ran the complete test suite and Python compilation before publication.

## Design pattern: Strategy

**Pattern used**

The recommender uses a lightweight Strategy pattern. `RANKING_MODES` stores interchangeable weight configurations for `balanced`, `genre_first`, `mood_first`, and `energy_first` ranking.

**How AI helped**

AI suggested separating the invariant scoring pipeline from the weights that express different product goals. This avoided four duplicated scoring functions and made the experiment reproducible from the CLI.

**Where it appears**

- `src/recommender.py`: `RANKING_MODES` and `score_song`
- `src/main.py`: the `--mode` command-line option

## Prompt comparison

Two prompting approaches were compared conceptually:

1. “Write a recommender” produced a generic sort-by-score direction with few constraints.
2. A rubric-based prompt specifying typed CSV loading, score reasons, three profiles, a weight experiment, diversity, multiple strategies, and tests produced a modular, verifiable design.

The second approach was easier to audit because every request mapped to a file, behavior, or test. The final implementation used that structured approach and rejected unsupported claims about real-world accuracy.
