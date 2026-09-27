from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models import SemesterPlan

semester_bp = Blueprint("semester", __name__)


@semester_bp.route("/", methods=["GET", "POST"])
@login_required
def planner():
    plan = SemesterPlan.query.filter_by(user_id=current_user.id).order_by(SemesterPlan.created_at.desc()).first()

    if request.method == "POST":
        subjects = [s.strip() for s in request.form.get("subjects", "").split(",") if s.strip()]
        weak_subjects = request.form.getlist("weak_subjects")
        exam_date_str = request.form.get("exam_date", "")
        exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d").date() if exam_date_str else None

        if not plan:
            plan = SemesterPlan(user_id=current_user.id)
            db.session.add(plan)
        plan.semester = request.form.get("semester", type=int)
        plan.subjects = subjects
        plan.weak_subjects = [s for s in weak_subjects if s in subjects]
        plan.exam_date = exam_date
        plan.target_hours_per_week = request.form.get("target_hours_per_week", type=int) or 10
        db.session.commit()
        flash("Semester plan saved.", "success")
        return redirect(url_for("semester.planner"))

    weekly_plan = None
    if plan and plan.subjects:
        weak = set(plan.weak_subjects) or set(plan.subjects[:1])
        strong = [s for s in plan.subjects if s not in weak]
        per_weak_hours = round(plan.target_hours_per_week * 0.6 / max(len(weak), 1), 1)
        per_strong_hours = round(plan.target_hours_per_week * 0.4 / max(len(strong), 1), 1) if strong else 0
        weekly_plan = (
            [{"subject": s, "hours": per_weak_hours, "priority": "Weak topic — prioritized"} for s in weak]
            + [{"subject": s, "hours": per_strong_hours, "priority": "Maintenance revision"} for s in strong]
        )

    return render_template("semester/planner.html", plan=plan, weekly_plan=weekly_plan)
