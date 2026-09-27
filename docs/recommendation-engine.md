# The Explainable Recommendation Engine

Location: `app/recommendation/engine.py` (scoring), `app/recommendation/weights.py`
(configurable weights), `app/services/next_move.py` ("Your Next Move"),
`app/services/skill_gap.py` (career-gap ordering).

## Design principle

> Every recommendation must be able to explain itself, in plain language,
> from data that actually exists in the database.

There is no black-box model, no invented confidence score, and no
"AI-generated" reasoning that can't be traced back to a concrete factor.
This was a deliberate choice for two reasons: it's honest to students (the
product brief explicitly forbids implying capabilities the platform
doesn't have), and it's fully defensible in a viva — every line of
`score_resource()` maps to one bullet on a slide.

## The scoring model

For a given `(resource, user)` pair, `score_resource()` computes a score
out of 100 by summing weighted contributions from independent factors,
each capped by its own weight, then normalizing:

| Factor | Weight | What it checks |
|---|---|---|
| Career relevance | 22 | Does the resource's skill tags overlap with the target career's required skills, prioritizing skills not yet mastered? |
| Interest relevance | 12 | Does the resource's topic/tags match the student's stated interests? |
| Skill level fit | 15 | Is the resource's difficulty close to the student's self-rated level for its skill tags? |
| Prerequisite fit | 10 | Has the student already met the prerequisite skill (via the `skills.prerequisite_skill_id` chain)? |
| Learning style fit | 10 | Does the resource's format (video/reading/project-first/…) match the student's stated learning style? |
| Language fit | 8 | Does the resource's language match the student's preferred language? |
| Time fit | 8 | Does the resource's duration fit the student's daily time budget? |
| Quality score | 10 | The resource's real rating, if one exists (never fabricated — unrated resources get a small neutral credit, not a penalty). |
| Freshness | 5 | How recently was the resource verified (`last_verified_at`)? |
| Budget / Free-First fit | 10 | Is the resource free, and does that match the student's budget preference and Free-First toggle? |
| Feedback adjustment | ±10 | Has the student previously marked similar-tagged recommendations useful or not useful? |

Weights live in one dictionary (`WEIGHTS` in `weights.py`) rather than
scattered magic numbers through the codebase — a future admin settings
screen could expose these directly.

Each factor that contributes positively appends a human-readable string to
a `reasons` list, e.g.:

> "Builds toward your goal of becoming a Cybersecurity Analyst: covers networking, security-fundamentals."
>
> "Free resource, prioritized by your Free-First preference."

The final `(score, reasons)` tuple is the **only** thing every caller uses
— the dashboard's "Recommended next" cards, the resource detail page's
"Why this resource?" box, the search page's match score, and "Your Next
Move" all call the exact same function. There is one engine, not several
inconsistent heuristics.

## The personalization loop (spec section 34)

When a student answers "Was this useful?" on a resource (with an optional
reason), it's stored as a `RecommendationFeedback` row tied to a
`Recommendation`. The next time `score_resource()` runs for that student,
it looks at feedback on resources sharing at least one skill tag with the
candidate resource, and nudges the score up or down proportional to the
historical usefulness ratio — visible to the student as a reason like:

> "Ranked lower: you marked similar recommendations as not useful."

This is intentionally simple (a ratio-based adjustment, not a trained
model) so it stays explainable and requires no training pipeline,
hyperparameter tuning, or GPU — appropriate for the stated goal of an
*explainable* engine, not a machine-learning one.

## "Your Next Move"

`get_next_move(user)` narrows the candidate pool to the student's current
roadmap stage (if they have an active roadmap tied to their career goal),
scores those resources with the same function, and returns the top one
plus the stage's milestone project as "what to build after this". If the
student has no active roadmap, it falls back to scoring every active
resource site-wide — so the feature always has something to say, even for
a brand-new account, as long as onboarding is complete.

## Skill Gap ordering

`analyze_skill_gap()` does not use the recommendation engine directly — it
compares the student's `UserSkill` rows against a career's
`required_skills`, and orders the *missing* skills by prerequisite chain
depth (skills with no prerequisite come first), so the "recommended
learning order" is structurally sound rather than alphabetical.

## What this engine is not

It is not a collaborative-filtering or matrix-factorization recommender,
and it does not call any external ranking API. That's a scope decision,
not an oversight — see `docs/future-ai.md` for what a v2 with an external
LLM/AI layer could add on top of (not instead of) this explainable core.
