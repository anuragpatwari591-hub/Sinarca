from flask import Blueprint, render_template

from app.models import Career, Resource, Project, Roadmap

career_bp = Blueprint("career", __name__)


@career_bp.route("/")
def index():
    careers = Career.query.order_by(Career.title).all()
    return render_template("career/index.html", careers=careers)


@career_bp.route("/<slug>")
def detail(slug):
    career = Career.query.filter_by(slug=slug).first_or_404()
    required = set(career.required_skills)

    resources = []
    if required:
        candidates = Resource.query.filter(Resource.status == "active").all()
        resources = [r for r in candidates if set(r.skill_tags) & required][:8]

    projects = []
    if required:
        all_projects = Project.query.all()
        projects = [p for p in all_projects if set(p.required_skills) & required][:6]

    roadmap = None
    if career.roadmap_id:
        roadmap = Roadmap.query.get(career.roadmap_id)

    return render_template(
        "career/detail.html", career=career, resources=resources, projects=projects, roadmap=roadmap
    )
