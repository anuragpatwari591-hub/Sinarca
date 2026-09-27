from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models import (
    User, Resource, Skill, Career, Roadmap, Project, Report,
    AffiliateClick, SponsoredContent, AdminAuditLog, Stream, LearningProgress,
    Bookmark,
)
from app.constants import DIFFICULTIES, RESOURCE_TYPES, LANGUAGES
from app.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


def _log(action, target=""):
    db.session.add(AdminAuditLog(admin_id=current_user.id, action=action, target=target))


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    total_users = User.query.filter_by(role="student").count()
    active_users = User.query.filter_by(role="student", is_active_account=True).count()
    total_resources = Resource.query.count()
    broken_resources = Resource.query.filter_by(status="broken").count()
    open_reports = Report.query.filter_by(status="open").count()
    affiliate_clicks = AffiliateClick.query.count()
    free_clicks = (
        AffiliateClick.query.join(Resource).filter(Resource.is_free.is_(True)).count()
    )
    paid_clicks = affiliate_clicks - free_clicks

    from app.models import EducationProfile

    popular_streams = (
        db.session.query(Stream.name, db.func.count(EducationProfile.id))
        .join(EducationProfile, EducationProfile.stream_id == Stream.id)
        .group_by(Stream.name).order_by(db.func.count(EducationProfile.id).desc()).limit(5).all()
    )
    popular_topics = (
        db.session.query(Resource.topic, db.func.count(AffiliateClick.id))
        .join(AffiliateClick, AffiliateClick.resource_id == Resource.id)
        .group_by(Resource.topic).order_by(db.func.count(AffiliateClick.id).desc()).limit(5).all()
    )

    return render_template(
        "admin/dashboard.html",
        total_users=total_users, active_users=active_users, total_resources=total_resources,
        broken_resources=broken_resources, open_reports=open_reports,
        affiliate_clicks=affiliate_clicks, free_clicks=free_clicks, paid_clicks=paid_clicks,
        popular_streams=popular_streams, popular_topics=popular_topics,
    )


# --- Users ---

@admin_bp.route("/users")
@login_required
@admin_required
def users():
    q = request.args.get("q", "")
    query = User.query.filter_by(role="student")
    if q:
        query = query.filter(db.or_(User.name.ilike(f"%{q}%"), User.email.ilike(f"%{q}%")))
    student_list = query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=student_list, q=q)


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["POST"])
@login_required
@admin_required
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active_account = not user.is_active_account
    _log("toggle_user_active", f"user:{user.email}")
    db.session.commit()
    flash(f"{user.email} is now {'active' if user.is_active_account else 'deactivated'}.", "success")
    return redirect(url_for("admin.users"))


# --- Resources ---

@admin_bp.route("/resources")
@login_required
@admin_required
def resources():
    status = request.args.get("status", "")
    query = Resource.query
    if status:
        query = query.filter_by(status=status)
    resource_list = query.order_by(Resource.created_at.desc()).all()
    return render_template("admin/resources.html", resources=resource_list, status=status)


@admin_bp.route("/resources/new", methods=["GET", "POST"])
@admin_bp.route("/resources/<int:resource_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def resource_form(resource_id=None):
    resource = Resource.query.get_or_404(resource_id) if resource_id else Resource()

    if request.method == "POST":
        resource.title = request.form.get("title")
        resource.provider = request.form.get("provider")
        resource.url = request.form.get("url")
        resource.category = request.form.get("category")
        resource.topic = request.form.get("topic")
        resource.skill_tags = [s.strip() for s in request.form.get("skill_tags", "").split(",") if s.strip()]
        resource.difficulty = request.form.get("difficulty", "beginner")
        resource.duration_minutes = request.form.get("duration_minutes", type=int)
        resource.language = request.form.get("language", "English")
        resource.is_free = request.form.get("is_free") == "on"
        resource.price_inr = request.form.get("price_inr", type=int) or 0
        rating = request.form.get("rating", type=float)
        resource.rating = rating
        resource.rating_count = request.form.get("rating_count", type=int) if rating else None
        resource.rating_source = request.form.get("rating_source") if rating else None
        resource.description = request.form.get("description")
        resource.prerequisites = request.form.get("prerequisites")
        resource.resource_type = request.form.get("resource_type", "video")
        resource.format_tags = [s.strip() for s in request.form.get("format_tags", "").split(",") if s.strip()]
        resource.status = request.form.get("status", "active")
        resource.is_sponsored = request.form.get("is_sponsored") == "on"
        resource.affiliate_url = request.form.get("affiliate_url") or None
        resource.last_verified_at = datetime.utcnow()

        if not resource_id:
            db.session.add(resource)
        _log("save_resource", resource.title or "")
        db.session.commit()
        flash("Resource saved and marked verified today.", "success")
        return redirect(url_for("admin.resources"))

    return render_template(
        "admin/resource_form.html", resource=resource, difficulties=DIFFICULTIES,
        resource_types=RESOURCE_TYPES, languages=LANGUAGES,
    )


@admin_bp.route("/resources/<int:resource_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    _log("delete_resource", resource.title)
    db.session.delete(resource)
    db.session.commit()
    flash("Resource deleted.", "info")
    return redirect(url_for("admin.resources"))


# --- Reports ---

@admin_bp.route("/reports")
@login_required
@admin_required
def reports():
    status = request.args.get("status", "open")
    query = Report.query
    if status:
        query = query.filter_by(status=status)
    report_list = query.order_by(Report.created_at.desc()).all()
    return render_template("admin/reports.html", reports=report_list, status=status)


@admin_bp.route("/reports/<int:report_id>/resolve", methods=["POST"])
@login_required
@admin_required
def resolve_report(report_id):
    report = Report.query.get_or_404(report_id)
    report.status = request.form.get("status", "resolved")
    _log("resolve_report", f"report:{report.id}")
    db.session.commit()
    flash("Report updated.", "success")
    return redirect(url_for("admin.reports"))


# --- Skills / Careers / Roadmaps / Projects (lightweight CRUD) ---

@admin_bp.route("/skills", methods=["GET", "POST"])
@login_required
@admin_required
def skills():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        if name:
            slug = name.lower().replace(" ", "-")
            if not Skill.query.filter_by(slug=slug).first():
                db.session.add(Skill(name=name, slug=slug, category=category))
                db.session.commit()
                flash("Skill added.", "success")
        return redirect(url_for("admin.skills"))
    return render_template("admin/skills.html", skills=Skill.query.order_by(Skill.name).all())


@admin_bp.route("/careers")
@login_required
@admin_required
def careers():
    return render_template("admin/careers.html", careers=Career.query.order_by(Career.title).all())


@admin_bp.route("/roadmaps")
@login_required
@admin_required
def roadmaps():
    return render_template("admin/roadmaps.html", roadmaps=Roadmap.query.order_by(Roadmap.title).all())


@admin_bp.route("/projects")
@login_required
@admin_required
def projects():
    return render_template("admin/projects.html", projects=Project.query.order_by(Project.title).all())


@admin_bp.route("/sponsored")
@login_required
@admin_required
def sponsored():
    return render_template("admin/sponsored.html", items=SponsoredContent.query.all())


@admin_bp.route("/analytics")
@login_required
@admin_required
def analytics():
    total_progress = LearningProgress.query.count()
    completed_progress = LearningProgress.query.filter_by(status="completed").count()
    total_bookmarks = Bookmark.query.count()
    return render_template(
        "admin/analytics.html", total_progress=total_progress,
        completed_progress=completed_progress, total_bookmarks=total_bookmarks,
    )
