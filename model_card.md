# Model Card: VibeFinder 1.0

## 1. Model name

**VibeFinder 1.0**

## 2. Goal and intended use

VibeFinder suggests fictional songs whose content attributes resemble a chosen taste profile. It is intended for classroom exploration of features, scoring, ranking, explanations, bias, and evaluation. It is not intended for commercial personalization, decisions about artists, or claims about a real listener's identity or preferences.

## 3. How the model works

The system adds points for exact genre and mood matches. It also gives partial credit when a song is close to the requested energy, tempo, valence, danceability, acousticness, popularity, decade, and instrumentalness. The balanced strategy values genre most, followed by energy and mood. Three alternative strategies emphasize genre, mood, or energy. After scoring, an artist-repeat penalty encourages variety. Every recommendation lists the contributions used to produce its score.

## 4. Data

The catalog contains 20 fictional songs and 12 genres. Every row has a title, artist, genre, mood, energy, tempo, valence, danceability, acousticness, popularity, release decade, and instrumentalness. Six enriched numeric attributes are used in addition to the core genre, mood, energy, and tempo features. The catalog does not contain real listening behavior, lyrics, language labels, demographic information, or ground-truth relevance judgments.

## 5. Strengths

- Rankings respond predictably to distinct profiles.
- Numeric similarity gives partial credit instead of rewarding only exact values.
- Explanations accurately expose the features and weights used.
- Strategies make weighting choices easy to compare.
- The diversity penalty reduces repeated artists without removing them completely.
- CSV validation and automated tests make failures visible.

## 6. Limitations and bias

The small fictional catalog cannot represent the breadth of music or listener taste. Exact genre and mood matches can over-prioritize familiar categories and form a filter bubble. Manually assigned popularity may favor mainstream-style tracks, while one-label genre and mood fields flatten songs with mixed identities. The catalog has uneven coverage by era and no cultural or language metadata, so it cannot support fairness claims. Artist diversity is a useful guardrail, but it is not a full fairness metric.

## 7. Evaluation

I ran four profiles: Happy Pop, Chill Lofi, Intense Rock, and the adversarial Sad Workout profile. Happy Pop ranked Sunrise City first; Chill Lofi ranked Library Rain first; Intense Rock ranked Storm Runner first; and Sad Workout ranked Afterglow Signal first in energy-first mode.

Happy Pop versus Chill Lofi changed both category and audio characteristics: the happy list favored high valence and danceability, while the lofi list favored low energy and acousticness. Chill Lofi versus Intense Rock produced almost opposite energy and tempo ranges, which matches the profile definitions. Happy Pop versus Intense Rock shared Gym Hero because its pop genre serves one profile while its intense mood and high energy serve the other; this was a useful reminder that a song can be relevant for different reasons.

The weight-shift experiment compared genre-first and energy-first on Happy Pop. Genre-first kept three pop songs at the top. Energy-first promoted Rooftop Lights, an indie-pop track with close energy and tempo, into third place. The experiment made recommendations different and more exploratory, but not objectively more accurate because no listener labels exist.

Eight automated tests verify loading, numeric types, scoring direction, ordering, explanations, strategy changes, diversity, invalid parameters, and table output. All eight pass.

## 8. Intended and non-intended use

Use VibeFinder to learn how content features become ranked recommendations and to test weighting ideas. Do not use it to evaluate artists, infer sensitive traits, pay creators, moderate content, or deploy recommendations to real users without representative data, consent, and broader evaluation.

## 9. Future improvements

1. Collect consented feedback and create train/validation/test relevance labels.
2. Add multi-label genres, language, context, recency, and skip/replay history.
3. Measure catalog coverage, artist exposure, novelty, and performance by subgroup.
4. Learn or calibrate weights while retaining explanation and human-control features.

## 10. Personal reflection

The biggest learning was that a recommender has two separate jobs: score each item and rank the whole catalog. A correct item score is not enough if ranking repeatedly surfaces the same artist, which motivated the diversity step. AI assistance helped generate implementation options and test ideas, but I checked suggestions against actual outputs. I revised the first diversity test because its penalty was too weak to guarantee three distinct artists, and I rejected any claim that the most complex strategy must be best. Simple rules can feel personal because small changes in feature targets produce visible changes in the list, but that feeling is not proof of accuracy.
