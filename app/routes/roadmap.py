from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Roadmap, UserRoadmapProgress, LearningProgress

roadmap_bp = Blueprint("roadmap", __name__)


@roadmap_bp.route("/")
def index():
    roadmaps = Roadmap.query.order_by(Roadmap.title).all()
    return render_template("roadmap/index.html", roadmaps=roadmaps)


@roadmap_bp.route("/<slug>")
def detail(slug):
    roadmap = Roadmap.query.filter_by(slug=slug).first_or_404()
    progress = None
    completed_ids = set()
    if current_user.is_authenticated and not current_user.is_admin:
        progress = UserRoadmapProgress.query.filter_by(user_id=current_user.id, roadmap_id=roadmap.id).first()
        completed_ids = {lp.resource_id for lp in LearningProgress.query.filter_by(
            user_id=current_user.id, status="completed"
        ).all()}
    completed_stage_orders = progress.completed_stage_orders if progress else []
    current_order = progress.current_stage_order if progress else 1
    return render_template(
        "roadmap/detail.html", roadmap=roadmap, progress=progress,
        completed_stage_orders=completed_stage_orders, current_order=current_order,
        completed_resource_ids=completed_ids,
    )


@roadmap_bp.route("/<slug>/start", methods=["POST"])
@login_required
def start(slug):
    roadmap = Roadmap.query.filter_by(slug=slug).first_or_404()
    existing = UserRoadmapProgress.query.filter_by(user_id=current_user.id, roadmap_id=roadmap.id).first()
    if not existing:
        db.session.add(UserRoadmapProgress(user_id=current_user.id, roadmap_id=roadmap.id))
        db.session.commit()
        flash(f"You're on your way with {roadmap.title}.", "success")
    return redirect(url_for("roadmap.detail", slug=slug))


@roadmap_bp.route("/<slug>/stage/<int:order>/complete", methods=["POST"])
@login_required
def complete_stage(slug, order):
    roadmap = Roadmap.query.filter_by(slug=slug).first_or_404()
    progress = UserRoadmapProgress.query.filter_by(user_id=current_user.id, roadmap_id=roadmap.id).first()
    if not progress:
        progress = UserRoadmapProgress(user_id=current_user.id, roadmap_id=roadmap.id)
        db.session.add(progress)
    progress.mark_stage_complete(order)
    db.session.commit()
    flash("Stage marked complete. Onward!", "success")
    return redirect(url_for("roadmap.detail", slug=slug))
