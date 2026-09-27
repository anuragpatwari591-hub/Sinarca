from datetime import date, timedelta

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.extensions import db
from app.models import (
    LearningProgress, StudySession, UserProject, UserRoadmapProgress,
    Roadmap, Notification,
)
from app.recommendation.engine import recommend_for_user
from app.services.next_move import get_next_move, _career_for_user
from app.utils.decorators import onboarding_required
from app.recommendation.weights import TIME_BUCKET_MINUTES

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
@onboarding_required
def home():
    career = _career_for_user(current_user)
    next_move = get_next_move(current_user)

    continue_learning = (
        LearningProgress.query.filter_by(user_id=current_user.id, status="in_progress")
        .order_by(LearningProgress.updated_at.desc()).limit(3).all()
    )

    roadmap_progress = None
    if career and career.roadmap_id:
        roadmap = db.session.get(Roadmap, career.roadmap_id)
        progress = UserRoadmapProgress.query.filter_by(
            user_id=current_user.id, roadmap_id=career.roadmap_id
        ).first()
        if roadmap:
            total_stages = len(roadmap.stages) or 1
            done = len(progress.completed_stage_orders) if progress else 0
            roadmap_progress = {
                "roadmap": roadmap,
                "pct": round(done / total_stages * 100),
                "current_stage_order": progress.current_stage_order if progress else 1,
            }

    skill_progress = []
    for us in current_user.skills:
        pct = {"beginner": 33, "intermediate": 66, "advanced": 90}.get(us.level, 33)
        skill_progress.append({"skill": us.skill, "pct": pct, "level": us.level})

    exclude_ids = {lp.resource_id for lp in LearningProgress.query.filter_by(
        user_id=current_user.id, status="completed"
    ).all()}
    recommendations = recommend_for_user(current_user, limit=5, exclude_resource_ids=exclude_ids, career=career)

    week_start = date.today() - timedelta(days=date.today().weekday())
    week_minutes = db.session.query(db.func.sum(StudySession.minutes)).filter(
        StudySession.user_id == current_user.id, StudySession.date >= week_start
    ).scalar() or 0
    daily_minutes = TIME_BUCKET_MINUTES.get(
        current_user.learning_dna.time_availability if current_user.learning_dna else None, 60
    )
    weekly_goal_minutes = daily_minutes * 6

    streak = _current_streak(current_user.id)

    upcoming_projects = UserProject.query.filter_by(
        user_id=current_user.id, status="planned"
    ).limit(3).all()

    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(
        Notification.created_at.desc()
    ).limit(5).all()

    return render_template(
        "dashboard/home.html",
        career=career,
        next_move=next_move,
        continue_learning=continue_learning,
        roadmap_progress=roadmap_progress,
        skill_progress=skill_progress,
        recommendations=recommendations,
        week_minutes=week_minutes,
        weekly_goal_minutes=weekly_goal_minutes,
        streak=streak,
        upcoming_projects=upcoming_projects,
        notifications=notifications,
    )


def _current_streak(user_id):
    sessions = (
        StudySession.query.filter_by(user_id=user_id)
        .with_entities(StudySession.date).distinct().order_by(StudySession.date.desc()).all()
    )
    days = {s[0] for s in sessions}
    streak = 0
    cursor = date.today()
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak
