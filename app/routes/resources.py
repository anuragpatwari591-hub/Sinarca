from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Resource, LearningProgress, Bookmark, Report, AffiliateClick
from app.constants import DIFFICULTIES, RESOURCE_TYPES, LANGUAGES, REPORT_TYPES, FEEDBACK_REASONS
from app.recommendation.engine import score_resource
from app.services.next_move import _career_for_user
from app.models import Recommendation, RecommendationFeedback

resources_bp = Blueprint("resources", __name__)


@resources_bp.route("/")
def search():
    q = request.args.get("q", "").strip()
    difficulty = request.args.get("difficulty", "")
    resource_type = request.args.get("resource_type", "")
    language = request.args.get("language", "")
    free_only = request.args.get("free_only", "")
    topic = request.args.get("topic", "")

    query = Resource.query.filter(Resource.status == "active")
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Resource.title.ilike(like), Resource.topic.ilike(like), Resource.provider.ilike(like)))
    if difficulty:
        query = query.filter(Resource.difficulty == difficulty)
    if resource_type:
        query = query.filter(Resource.resource_type == resource_type)
    if language:
        query = query.filter(Resource.language == language)
    if free_only == "1":
        query = query.filter(Resource.is_free.is_(True))
    if topic:
        query = query.filter(Resource.topic == topic)

    results = query.order_by(Resource.rating.desc().nullslast()).limit(60).all()
    topics = [t[0] for t in db.session.query(Resource.topic).distinct().order_by(Resource.topic).all() if t[0]]

    scored = {}
    if current_user.is_authenticated and not current_user.is_admin:
        career = _career_for_user(current_user)
        for r in results:
            score, reasons = score_resource(
                r, learning_dna=current_user.learning_dna, user_skills=current_user.skills, career=career
            )
            scored[r.id] = {"score": score, "reasons": reasons}

    return render_template(
        "resources/search.html",
        results=results, q=q, difficulty=difficulty, resource_type=resource_type,
        language=language, free_only=free_only, topic=topic, topics=topics,
        difficulties=DIFFICULTIES, resource_types=RESOURCE_TYPES, languages=LANGUAGES,
        scored=scored,
    )


@resources_bp.route("/<int:resource_id>")
def detail(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    score, reasons = (None, [])
    progress = None
    is_bookmarked = False
    if current_user.is_authenticated and not current_user.is_admin:
        career = _career_for_user(current_user)
        score, reasons = score_resource(
            resource, learning_dna=current_user.learning_dna, user_skills=current_user.skills, career=career
        )
        progress = LearningProgress.query.filter_by(user_id=current_user.id, resource_id=resource.id).first()
        is_bookmarked = Bookmark.query.filter_by(
            user_id=current_user.id, target_type="resource", target_id=resource.id
        ).first() is not None

    similar = Resource.query.filter(
        Resource.topic == resource.topic, Resource.id != resource.id, Resource.status == "active"
    ).limit(3).all()

    return render_template(
        "resources/detail.html", resource=resource, score=score, reasons=reasons,
        progress=progress, is_bookmarked=is_bookmarked, similar=similar,
        report_types=REPORT_TYPES, feedback_reasons=FEEDBACK_REASONS,
    )


@resources_bp.route("/<int:resource_id>/go")
def go(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    click = AffiliateClick(
        resource_id=resource.id,
        user_id=current_user.id if current_user.is_authenticated else None,
        was_affiliate=bool(resource.affiliate_url),
    )
    db.session.add(click)

    if current_user.is_authenticated and not current_user.is_admin:
        progress = LearningProgress.query.filter_by(user_id=current_user.id, resource_id=resource.id).first()
        if not progress:
            progress = LearningProgress(
                user_id=current_user.id, resource_id=resource.id, status="in_progress",
                started_at=datetime.utcnow(), progress_pct=5,
            )
            db.session.add(progress)
    db.session.commit()
    return redirect(resource.click_url)


@resources_bp.route("/<int:resource_id>/progress", methods=["POST"])
@login_required
def update_progress(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    status = request.form.get("status", "in_progress")
    progress = LearningProgress.query.filter_by(user_id=current_user.id, resource_id=resource.id).first()
    if not progress:
        progress = LearningProgress(user_id=current_user.id, resource_id=resource.id)
        db.session.add(progress)
    progress.status = status
    progress.progress_pct = 100 if status == "completed" else max(progress.progress_pct or 0, 10)
    if status == "in_progress" and not progress.started_at:
        progress.started_at = datetime.utcnow()
    if status == "completed":
        progress.completed_at = datetime.utcnow()
    db.session.commit()
    flash("Progress updated.", "success")
    return redirect(url_for("resources.detail", resource_id=resource.id))


@resources_bp.route("/<int:resource_id>/bookmark", methods=["POST"])
@login_required
def toggle_bookmark(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    folder = request.form.get("folder", "Learn Later")
    existing = Bookmark.query.filter_by(
        user_id=current_user.id, target_type="resource", target_id=resource.id
    ).first()
    if existing:
        db.session.delete(existing)
        flash("Removed from bookmarks.", "info")
    else:
        db.session.add(Bookmark(user_id=current_user.id, target_type="resource", target_id=resource.id, folder=folder))
        flash("Saved to bookmarks.", "success")
    db.session.commit()
    return redirect(request.referrer or url_for("resources.detail", resource_id=resource.id))


@resources_bp.route("/<int:resource_id>/report", methods=["POST"])
@login_required
def report(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    report_type = request.form.get("report_type")
    details = request.form.get("details", "")
    if not report_type:
        flash("Please choose a report reason.", "error")
        return redirect(url_for("resources.detail", resource_id=resource.id))
    db.session.add(Report(resource_id=resource.id, user_id=current_user.id, report_type=report_type, details=details))
    db.session.commit()
    flash("Thanks — our admin team will review this report.", "success")
    return redirect(url_for("resources.detail", resource_id=resource.id))


@resources_bp.route("/<int:resource_id>/feedback", methods=["POST"])
@login_required
def feedback(resource_id):
    """The personalization learning loop (spec section 34), reachable without JS."""
    resource = Resource.query.get_or_404(resource_id)
    useful = request.form.get("useful") == "yes"
    reason = request.form.get("reason") or None

    rec = Recommendation.query.filter_by(user_id=current_user.id, resource_id=resource.id).order_by(
        Recommendation.created_at.desc()
    ).first()
    if not rec:
        rec = Recommendation(user_id=current_user.id, resource_id=resource.id, score=0, reasons=[])
        db.session.add(rec)
        db.session.flush()

    existing = RecommendationFeedback.query.filter_by(recommendation_id=rec.id).first()
    if existing:
        existing.useful = useful
        existing.reason = reason
    else:
        db.session.add(RecommendationFeedback(recommendation_id=rec.id, useful=useful, reason=reason))
    db.session.commit()
    flash("Thanks — this helps NAVORA personalize your future recommendations.", "success")
    return redirect(request.referrer or url_for("resources.detail", resource_id=resource.id))
