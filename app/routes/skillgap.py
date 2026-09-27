from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from app.models import Career, Roadmap
from app.services.skill_gap import analyze_skill_gap
from app.services.next_move import _career_for_user

skillgap_bp = Blueprint("skillgap", __name__)


@skillgap_bp.route("/")
@login_required
def index():
    careers = Career.query.order_by(Career.title).all()
    career_id = request.args.get("career_id", type=int)

    default_career = _career_for_user(current_user)
    career = Career.query.get(career_id) if career_id else default_career

    gap = analyze_skill_gap(current_user, career) if career else None
    roadmap = Roadmap.query.get(career.roadmap_id) if career and career.roadmap_id else None
    return render_template("skillgap/index.html", careers=careers, career=career, gap=gap, roadmap=roadmap)
