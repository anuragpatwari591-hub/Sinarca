from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Stream, Skill, Career, EducationProfile, LearningDNA, UserSkill
from app.constants import (
    INTEREST_AREAS, CAREER_GOAL_SUGGESTIONS, LEARNING_STYLES, TIME_AVAILABILITY,
    LANGUAGES, BUDGET_PREFERENCES, DEGREES, STUDENT_YEARS,
)

onboarding_bp = Blueprint("onboarding", __name__)

TOTAL_STEPS = 7
SESSION_KEY = "onboarding_data"


def _data():
    return session.setdefault(SESSION_KEY, {})


@onboarding_bp.route("/step/<int:step_number>", methods=["GET", "POST"])
@login_required
def step(step_number):
    if current_user.is_admin:
        return redirect(url_for("admin.dashboard"))
    if step_number < 1 or step_number > TOTAL_STEPS:
        return redirect(url_for("onboarding.step", step_number=1))

    data = _data()

    if request.method == "POST":
        _save_step(step_number, data, request.form)
        session[SESSION_KEY] = data
        session.modified = True
        if step_number == TOTAL_STEPS:
            _commit(data)
            session.pop(SESSION_KEY, None)
            flash("Your Learning DNA is ready. Here's your personalized dashboard.", "success")
            return redirect(url_for("dashboard.home"))
        return redirect(url_for("onboarding.step", step_number=step_number + 1))

    context = {
        "step_number": step_number,
        "total_steps": TOTAL_STEPS,
        "data": data,
        "streams": Stream.query.order_by(Stream.name).all(),
        "degrees": DEGREES,
        "years": STUDENT_YEARS,
        "interests": INTEREST_AREAS,
        "career_suggestions": CAREER_GOAL_SUGGESTIONS,
        "careers": Career.query.order_by(Career.title).all(),
        "learning_styles": LEARNING_STYLES,
        "time_options": TIME_AVAILABILITY,
        "languages": LANGUAGES,
        "budgets": BUDGET_PREFERENCES,
        "skills": _skills_for_interests(data.get("interests", [])),
    }
    return render_template(f"onboarding/step{step_number}.html", **context)


def _skills_for_interests(interests):
    if not interests:
        return Skill.query.order_by(Skill.name).limit(8).all()
    category_map = {
        "Software Development": "programming", "Artificial Intelligence": "ai",
        "Cybersecurity": "security", "Finance": "finance", "Marketing": "marketing",
        "Management": "management", "Design": "design", "Data Analytics": "data",
        "Entrepreneurship": "business", "Consulting": "business", "Research": "research",
        "Government Exams": "aptitude", "Accounting": "finance", "Law": "law",
    }
    categories = {category_map.get(i) for i in interests if category_map.get(i)}
    if not categories:
        return Skill.query.order_by(Skill.name).limit(8).all()
    return Skill.query.filter(Skill.category.in_(categories)).order_by(Skill.name).limit(12).all()


def _save_step(step_number, data, form):
    if step_number == 1:
        data["stream_id"] = form.get("stream_id", type=int)
        data["degree"] = form.get("degree", "")
        data["specialization"] = form.get("specialization", "")
        data["college"] = form.get("college", "")
        data["year"] = form.get("year", type=int)
        data["semester"] = form.get("semester", type=int)
    elif step_number == 2:
        data["interests"] = form.getlist("interests")
    elif step_number == 3:
        skill_levels = {}
        for key, value in form.items():
            if key.startswith("skill_") and value:
                skill_levels[key.replace("skill_", "")] = value
        data["skill_levels"] = skill_levels
    elif step_number == 4:
        data["career_goal"] = form.get("career_goal", "").strip()
    elif step_number == 5:
        data["learning_style"] = form.getlist("learning_style")
    elif step_number == 6:
        data["time_availability"] = form.get("time_availability", "1_hour_per_day")
        data["language"] = form.get("language", "English")
    elif step_number == 7:
        data["budget_preference"] = form.get("budget_preference", "mostly_free")
        data["free_first_mode"] = form.get("free_first_mode") == "on"


def _commit(data):
    profile = current_user.education_profile or EducationProfile(user_id=current_user.id)
    profile.stream_id = data.get("stream_id")
    profile.degree = data.get("degree")
    profile.specialization = data.get("specialization")
    profile.college = data.get("college")
    profile.year = data.get("year")
    profile.semester = data.get("semester")
    db.session.add(profile)

    dna = current_user.learning_dna or LearningDNA(user_id=current_user.id)
    dna.interests = data.get("interests", [])
    dna.career_goal = data.get("career_goal")
    dna.learning_style = data.get("learning_style", [])
    dna.time_availability = data.get("time_availability", "1_hour_per_day")
    dna.language = data.get("language", "English")
    dna.budget_preference = data.get("budget_preference", "mostly_free")
    dna.free_first_mode = bool(data.get("free_first_mode", True))
    db.session.add(dna)

    for slug, level in data.get("skill_levels", {}).items():
        skill = Skill.query.filter_by(slug=slug).first()
        if not skill:
            continue
        us = UserSkill.query.filter_by(user_id=current_user.id, skill_id=skill.id).first()
        if not us:
            us = UserSkill(user_id=current_user.id, skill_id=skill.id)
        us.level = level
        db.session.add(us)

    current_user.onboarding_complete = True
    db.session.commit()
