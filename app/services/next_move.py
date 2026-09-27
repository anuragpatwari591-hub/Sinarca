"""
"Your Next Move" - the platform's signature recommendation card (spec section 47)
and the engine behind "What should I learn next?" (spec section 13).
"""

from app.extensions import db
from app.models import (
    Career,
    LearningProgress,
    Project,
    Roadmap,
    RoadmapStage,
    UserRoadmapProgress,
)
from app.recommendation.engine import score_resource, RecommendationFeedback, Recommendation


def _career_for_user(user):
    if not user.learning_dna or not user.learning_dna.career_goal:
        return None
    return Career.query.filter(Career.title == user.learning_dna.career_goal).first()


def _completed_resource_ids(user):
    rows = LearningProgress.query.filter_by(user_id=user.id, status="completed").all()
    return {r.resource_id for r in rows}


def get_next_move(user):
    """
    Returns a dict describing the single best next action for this student,
    or None if the user has not completed onboarding.
    """
    if not user.learning_dna:
        return None

    career = _career_for_user(user)
    completed_ids = _completed_resource_ids(user)

    stage = None
    roadmap = None
    if career and career.roadmap_id:
        roadmap = db.session.get(Roadmap, career.roadmap_id)
        if roadmap:
            progress = UserRoadmapProgress.query.filter_by(user_id=user.id, roadmap_id=roadmap.id).first()
            current_order = progress.current_stage_order if progress else 1
            stage = (
                RoadmapStage.query.filter_by(roadmap_id=roadmap.id, order=current_order).first()
                or RoadmapStage.query.filter_by(roadmap_id=roadmap.id).order_by(RoadmapStage.order).first()
            )

    candidate_resources = []
    if stage:
        candidate_resources = [rr.resource for rr in stage.resources if rr.resource_id not in completed_ids]

    feedback_history = (
        RecommendationFeedback.query.join(Recommendation).filter(Recommendation.user_id == user.id).all()
    )

    best = None
    best_score = -1
    best_reasons = []
    pool = candidate_resources if candidate_resources else None

    if pool is None:
        from app.models import Resource

        pool = Resource.query.filter(Resource.status == "active", ~Resource.id.in_(completed_ids or [-1])).all()

    for resource in pool:
        score, reasons = score_resource(
            resource,
            learning_dna=user.learning_dna,
            user_skills=user.skills,
            career=career,
            feedback_history=feedback_history,
        )
        if score > best_score:
            best_score, best, best_reasons = score, resource, reasons

    if not best:
        return None

    after_project = None
    if stage and stage.milestone_project:
        after_project = stage.milestone_project
    else:
        tags = set(best.skill_tags)
        after_project = (
            Project.query.filter(Project.difficulty == best.difficulty).first()
            if tags
            else None
        )

    return {
        "resource": best,
        "score": best_score,
        "reasons": best_reasons,
        "stage": stage,
        "roadmap": roadmap,
        "after_project": after_project,
        "estimated_minutes": best.duration_minutes or 45,
    }
