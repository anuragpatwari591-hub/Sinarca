"""
Configurable weights for the explainable recommendation engine.

Nothing here is hard-coded logic buried in routes — every factor's
contribution to the final 0-100 score is declared in one place, so the
weighting can be tuned (or exposed to an admin settings screen in a future
version) without touching the scoring algorithm itself.

See docs/recommendation-engine.md for the full write-up of this model.
"""

WEIGHTS = {
    "career_relevance": 22,
    "interest_relevance": 12,
    "skill_level_fit": 15,
    "prerequisite_fit": 10,
    "learning_style_fit": 10,
    "language_fit": 8,
    "time_fit": 8,
    "quality_score": 10,
    "freshness": 5,
    "budget_fit": 10,
    "feedback_adjustment": 10,  # applied as a bonus/penalty on top of the base 100
}

DIFFICULTY_ORDER = ["beginner", "intermediate", "advanced"]

TIME_BUCKET_MINUTES = {
    "30_min_per_day": 30,
    "1_hour_per_day": 60,
    "2_hours_per_day": 120,
    "3_plus_hours_per_day": 200,
}
