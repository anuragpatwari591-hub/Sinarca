"""
The explainable personalization & recommendation engine (spec sections 5, 33, 34).

This is NOT a black box. Every resource is scored on named factors, each
factor produces a human-readable reason when it contributes positively,
and the final list of reasons is what the UI shows under "Why this
resource?" / "Why recommended?". The engine works entirely from data
already in the database -- it never calls an external AI service, so the
product keeps functioning if such a service is unavailable (spec section 5).
"""

from datetime import datetime

from app.models import Resource, RecommendationFeedback, Recommendation
from app.recommendation.weights import WEIGHTS, DIFFICULTY_ORDER, TIME_BUCKET_MINUTES


def _difficulty_distance(resource_difficulty, user_level):
    try:
        r = DIFFICULTY_ORDER.index(resource_difficulty)
        u = DIFFICULTY_ORDER.index(user_level)
    except ValueError:
        return 1
    return abs(r - u)


def _skill_level_map(user_skills):
    return {us.skill.slug: us.level for us in user_skills if us.skill}


def score_resource(resource, *, learning_dna, user_skills, career=None, feedback_history=None):
    """
    Score a single resource for a user.

    Returns (score: float 0-100, reasons: list[str]).
    """
    reasons = []
    points = 0.0
    max_points = 0.0

    skill_levels = _skill_level_map(user_skills)
    interests = learning_dna.interests if learning_dna else []
    style = learning_dna.learning_style if learning_dna else []
    language = learning_dna.language if learning_dna else "English"
    budget = learning_dna.budget_preference if learning_dna else "mostly_free"
    free_first = learning_dna.free_first_mode if learning_dna else True
    career_goal = learning_dna.career_goal if learning_dna else None

    resource_tags = set(resource.skill_tags)

    # --- Career relevance ---
    w = WEIGHTS["career_relevance"]
    max_points += w
    if career:
        required = set(career.required_skills)
        overlap = resource_tags & required
        if overlap:
            # Prioritize skills the user hasn't reached "advanced" in yet.
            unmastered = {s for s in overlap if skill_levels.get(s, "beginner") != "advanced"}
            target = unmastered or overlap
            points += w
            reasons.append(
                f"Builds toward your goal of becoming a {career.title}: covers "
                f"{', '.join(sorted(target))}."
            )
    elif career_goal:
        # No structured career match found, but a goal string was supplied.
        max_points -= w * 0.5  # reduce this factor's weight rather than penalize

    # --- Interest relevance ---
    w = WEIGHTS["interest_relevance"]
    max_points += w
    if interests and (resource.topic in interests or resource_tags.intersection(interests)):
        points += w
        reasons.append(f"Matches your stated interest in {resource.topic}.")

    # --- Skill level fit ---
    w = WEIGHTS["skill_level_fit"]
    max_points += w
    if resource_tags:
        levels = [skill_levels.get(tag, "beginner") for tag in resource_tags]
        avg_distance = sum(_difficulty_distance(resource.difficulty, lvl) for lvl in levels) / len(levels)
        if avg_distance == 0:
            points += w
            reasons.append(
                f"Difficulty ({resource.difficulty}) matches your current self-rated level."
            )
        elif avg_distance == 1:
            points += w * 0.5
        # distance >= 2: no points, resource is a poor difficulty fit
    else:
        points += w * 0.5  # neutral resource, no penalty

    # --- Prerequisite fit ---
    w = WEIGHTS["prerequisite_fit"]
    max_points += w
    prereq_ok = True
    for tag in resource_tags:
        skill = next((us.skill for us in user_skills if us.skill and us.skill.slug == tag), None)
        if skill and skill.prerequisite:
            prereq_level = skill_levels.get(skill.prerequisite.slug)
            if prereq_level is None:
                prereq_ok = False
    if prereq_ok:
        points += w
        if resource_tags:
            reasons.append("You already meet the prerequisites for this topic.")

    # --- Learning style fit ---
    w = WEIGHTS["learning_style_fit"]
    max_points += w
    format_tags = set(resource.format_tags)
    if style and format_tags.intersection(style):
        points += w
        matched = ", ".join(sorted(format_tags.intersection(style)))
        reasons.append(f"Delivered as {matched}, matching your preferred learning style.")

    # --- Language fit ---
    w = WEIGHTS["language_fit"]
    max_points += w
    if resource.language.lower() == (language or "English").lower():
        points += w
        if language and language != "English":
            reasons.append(f"Available in {resource.language}.")

    # --- Time fit ---
    w = WEIGHTS["time_fit"]
    max_points += w
    budget_minutes = TIME_BUCKET_MINUTES.get(
        learning_dna.time_availability if learning_dna else None, 60
    )
    if resource.duration_minutes and resource.duration_minutes <= budget_minutes * 3:
        points += w
        if resource.duration_minutes <= budget_minutes:
            reasons.append(f"Fits within your available study time ({resource.duration_minutes} min).")
    elif not resource.duration_minutes:
        points += w * 0.5

    # --- Quality score ---
    w = WEIGHTS["quality_score"]
    max_points += w
    if resource.has_real_rating:
        points += w * min(resource.rating / 5.0, 1.0)
        if resource.rating >= 4.3:
            reasons.append(f"Highly rated ({resource.rating}/5 from {resource.rating_count} learners).")
    else:
        points += w * 0.4  # neutral, unrated resources aren't penalized heavily

    # --- Freshness ---
    w = WEIGHTS["freshness"]
    max_points += w
    if resource.last_verified_at:
        age_days = (datetime.utcnow() - resource.last_verified_at).days
        if age_days <= 180:
            points += w
        elif age_days <= 365:
            points += w * 0.5

    # --- Budget / Free-First fit ---
    w = WEIGHTS["budget_fit"]
    max_points += w
    if resource.is_free:
        points += w
        if free_first or budget == "completely_free":
            reasons.append("Free resource, prioritized by your Free-First preference.")
    else:
        if budget in ("open_to_paid", "premium_ok"):
            points += w * 0.6
        elif budget == "mostly_free":
            points += w * 0.2
        # completely_free budget + paid resource => 0 points, naturally deprioritized

    # --- Feedback adjustment (personalization learning loop) ---
    adjustment = 0.0
    if feedback_history:
        similar = [
            fb for fb in feedback_history
            if fb.recommendation and fb.recommendation.resource
            and set(fb.recommendation.resource.skill_tags) & resource_tags
        ]
        if similar:
            useful_ratio = sum(1 for fb in similar if fb.useful) / len(similar)
            adjustment = (useful_ratio - 0.5) * 2 * WEIGHTS["feedback_adjustment"]
            if useful_ratio >= 0.75:
                reasons.append("You found similar recommendations useful before.")
            elif useful_ratio <= 0.25:
                reasons.append("Ranked lower: you marked similar recommendations as not useful.")

    base_score = (points / max_points * 100) if max_points else 50.0
    final_score = max(0.0, min(100.0, base_score + adjustment))

    if not reasons:
        reasons.append("Broadly relevant to your learning profile.")

    return round(final_score, 1), reasons


def recommend_for_user(user, limit=5, exclude_resource_ids=None, career=None):
    """
    Returns a ranked list of dicts: {resource, score, reasons}.
    """
    exclude_resource_ids = exclude_resource_ids or set()
    learning_dna = user.learning_dna
    user_skills = user.skills

    feedback_history = (
        RecommendationFeedback.query
        .join(Recommendation)
        .filter(Recommendation.user_id == user.id)
        .all()
    )

    candidates = Resource.query.filter(Resource.status == "active").all()

    results = []
    for resource in candidates:
        if resource.id in exclude_resource_ids:
            continue
        score, reasons = score_resource(
            resource,
            learning_dna=learning_dna,
            user_skills=user_skills,
            career=career,
            feedback_history=feedback_history,
        )
        results.append({"resource": resource, "score": score, "reasons": reasons})

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:limit]
