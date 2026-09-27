from datetime import date

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Recommendation, RecommendationFeedback, StudySession, Notification

api_bp = Blueprint("api", __name__)


@api_bp.route("/recommendation-feedback", methods=["POST"])
@login_required
def recommendation_feedback():
    data = request.get_json(silent=True) or request.form
    raw_resource_id = data.get("resource_id")
    useful = str(data.get("useful")).lower() in ("true", "1", "yes")
    reason = data.get("reason")

    try:
        resource_id = int(raw_resource_id)
    except (TypeError, ValueError):
        return jsonify({"error": "resource_id is required"}), 400

    rec = Recommendation.query.filter_by(user_id=current_user.id, resource_id=resource_id).order_by(
        Recommendation.created_at.desc()
    ).first()
    if not rec:
        rec = Recommendation(user_id=current_user.id, resource_id=resource_id, score=0, reasons=[])
        db.session.add(rec)
        db.session.flush()

    feedback = RecommendationFeedback.query.filter_by(recommendation_id=rec.id).first()
    if not feedback:
        feedback = RecommendationFeedback(recommendation_id=rec.id, useful=useful, reason=reason)
        db.session.add(feedback)
    else:
        feedback.useful = useful
        feedback.reason = reason
    db.session.commit()
    return jsonify({"ok": True})


@api_bp.route("/study-session", methods=["POST"])
@login_required
def log_study_session():
    minutes = request.form.get("minutes", type=int) or 0
    topic = request.form.get("topic", "")
    if minutes > 0:
        db.session.add(StudySession(user_id=current_user.id, date=date.today(), minutes=minutes, topic=topic))
        db.session.commit()
    return jsonify({"ok": True, "minutes": minutes})


@api_bp.route("/notifications/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    n = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    n.is_read = True
    db.session.commit()
    return jsonify({"ok": True})
