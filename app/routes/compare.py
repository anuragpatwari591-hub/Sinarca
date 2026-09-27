from flask import Blueprint, render_template, request

from app.models import Resource

compare_bp = Blueprint("compare", __name__)


@compare_bp.route("/")
def index():
    ids = request.args.getlist("id", type=int)[:3]
    resources = Resource.query.filter(Resource.id.in_(ids)).all() if ids else []
    ordered = sorted(resources, key=lambda r: ids.index(r.id))

    suggestions = []
    if ordered:
        topic = ordered[0].topic
        suggestions = (
            Resource.query.filter(Resource.topic == topic, ~Resource.id.in_(ids), Resource.status == "active")
            .limit(6).all()
        )
    return render_template("compare/index.html", resources=ordered, suggestions=suggestions)
