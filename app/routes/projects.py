from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Project, UserProject
from app.constants import DIFFICULTIES

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/")
def index():
    difficulty = request.args.get("difficulty", "")
    query = Project.query
    if difficulty:
        query = query.filter(Project.difficulty == difficulty)
    projects = query.order_by(Project.difficulty).all()

    user_status = {}
    if current_user.is_authenticated and not current_user.is_admin:
        for up in UserProject.query.filter_by(user_id=current_user.id).all():
            user_status[up.project_id] = up.status

    return render_template(
        "projects/index.html", projects=projects, difficulty=difficulty,
        difficulties=DIFFICULTIES, user_status=user_status,
    )


@projects_bp.route("/<int:project_id>")
def detail(project_id):
    project = Project.query.get_or_404(project_id)
    user_project = None
    if current_user.is_authenticated and not current_user.is_admin:
        user_project = UserProject.query.filter_by(user_id=current_user.id, project_id=project.id).first()
    return render_template("projects/detail.html", project=project, user_project=user_project)


@projects_bp.route("/<int:project_id>/status", methods=["POST"])
@login_required
def update_status(project_id):
    project = Project.query.get_or_404(project_id)
    status = request.form.get("status", "planned")
    repo_url = request.form.get("repo_url", "").strip()

    up = UserProject.query.filter_by(user_id=current_user.id, project_id=project.id).first()
    if not up:
        up = UserProject(user_id=current_user.id, project_id=project.id)
        db.session.add(up)
    up.status = status
    if repo_url:
        up.repo_url = repo_url
    if status == "in_progress" and not up.started_at:
        up.started_at = datetime.utcnow()
    if status == "completed":
        up.completed_at = datetime.utcnow()
    db.session.commit()
    flash("Project status updated.", "success")
    return redirect(url_for("projects.detail", project_id=project.id))
