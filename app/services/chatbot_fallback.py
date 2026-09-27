"""
Deterministic fallback engine for the AI Study Mentor (spec section 17).

Every mode here works purely from data already in the database -- it never
invents facts, statistics, or capabilities the platform doesn't have. If an
external LLM is configured later (see app.services.ai_adapter), it can layer
on top of this for more natural phrasing, but the underlying facts (which
resource, which skill, which project) should still come from here so the
mentor never hallucinates a course or a rating.
"""

import re

from app.models import Skill, Resource, Project, LearningProgress
from app.services.skill_gap import analyze_skill_gap
from app.services.next_move import get_next_move, _career_for_user


def _extract_skill(message):
    words = re.findall(r"[a-zA-Z\+\#\.]+", message.lower())
    all_skills = Skill.query.all()
    for skill in all_skills:
        if skill.name.lower() in message.lower() or skill.slug in words:
            return skill
    return None


def handle_message(user, mode, message):
    mode = mode or "explain"
    handler = _HANDLERS.get(mode, _handle_explain)
    return handler(user, message)


def _handle_explain(user, message):
    skill = _extract_skill(message)
    if not skill:
        return (
            "Tell me a specific topic (e.g. \"Explain recursion\" or \"Explain SQL joins\") "
            "and I'll break it down using what's in your roadmap."
        )
    resource = (
        Resource.query.filter(Resource.status == "active")
        .filter(Resource.skill_tags_json.contains(f'"{skill.slug}"'))
        .order_by(Resource.difficulty.asc())
        .first()
    )
    text = f"**{skill.name}**\n\n{skill.description or 'No summary is recorded for this skill yet.'}"
    if resource:
        text += f"\n\nTo go deeper: *{resource.title}* ({resource.provider}, {'free' if resource.is_free else f'₹{resource.price_inr}'})."
    return text


def _handle_quiz(user, message):
    skill = _extract_skill(message)
    if not skill:
        in_progress = (
            LearningProgress.query.filter_by(user_id=user.id, status="in_progress").first()
        )
        skill_name = in_progress.resource.topic if in_progress else "your current topic"
    else:
        skill_name = skill.name
    questions = [
        f"In your own words, what problem does {skill_name} solve?",
        f"Give one real example of {skill_name} you could build or apply this week.",
        f"What would you get wrong as a beginner learning {skill_name}, and why?",
    ]
    return "Quiz me mode -- try answering these:\n\n" + "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))


def _handle_plan_day(user, message):
    hours_match = re.search(r"(\d+(\.\d+)?)\s*hour", message.lower())
    minutes_match = re.search(r"(\d+)\s*min", message.lower())
    if hours_match:
        minutes = int(float(hours_match.group(1)) * 60)
    elif minutes_match:
        minutes = int(minutes_match.group(1))
    else:
        minutes = 60

    move = get_next_move(user)
    if not move:
        return "Complete onboarding first so I know your goals and available time."

    plan = [f"Here's a plan for your ~{minutes} minutes today:"]
    remaining = minutes
    est = move["estimated_minutes"]
    plan.append(f"1. ({min(est, remaining)} min) {move['resource'].title} -- {move['reasons'][0]}")
    remaining -= est
    if remaining > 15 and move.get("after_project"):
        plan.append(f"2. ({min(remaining, 20)} min) Sketch a plan for the project: {move['after_project'].title}.")
    elif remaining > 10:
        plan.append("2. Spend the rest reviewing your notes from your last session.")
    return "\n".join(plan)


def _handle_find_resources(user, message):
    skill = _extract_skill(message)
    query = Resource.query.filter(Resource.status == "active")
    if skill:
        query = query.filter(Resource.skill_tags_json.contains(f'"{skill.slug}"'))
    else:
        words = message.split()
        if words:
            query = query.filter(Resource.topic.ilike(f"%{words[-1]}%"))
    results = query.order_by(Resource.rating.desc().nullslast()).limit(3).all()
    if not results:
        return "I couldn't find a matching resource yet. Try the full Resource Search page for more filters."
    lines = ["Here's what I found:"]
    for r in results:
        price = "Free" if r.is_free else f"₹{r.price_inr}"
        lines.append(f"- {r.title} ({r.provider}, {price}) -> {r.url}")
    return "\n".join(lines)


def _handle_project_ideas(user, message):
    skill = _extract_skill(message)
    query = Project.query
    if skill:
        query = query.filter(Project.required_skills_json.contains(f'"{skill.slug}"'))
    projects = query.limit(3).all()
    if not projects:
        projects = Project.query.limit(3).all()
    lines = ["Project ideas based on your current skills:"]
    for p in projects:
        lines.append(f"- **{p.title}** ({p.difficulty}, ~{p.estimated_hours}h) -- {p.description}")
    return "\n".join(lines)


def _handle_revision(user, message):
    in_progress = LearningProgress.query.filter_by(user_id=user.id, status="in_progress").all()
    if not in_progress:
        return "You have no in-progress resources to revise. Start something from your roadmap first."
    lines = ["Here's a quick revision plan for what you've started:"]
    for lp in in_progress:
        lines.append(f"- Revisit *{lp.resource.title}* ({lp.progress_pct}% complete).")
    return "\n".join(lines)


def _handle_career_guidance(user, message):
    career = _career_for_user(user)
    if not career:
        return "Set a career goal during onboarding (or update it in your profile) so I can map a path for you."
    gap = analyze_skill_gap(user, career)
    lines = [f"Path toward **{career.title}** -- you're {gap['readiness_pct']}% ready on required skills."]
    if gap["missing"]:
        lines.append("Focus next on: " + ", ".join(s.name for s in gap["missing"][:3]))
    else:
        lines.append("You've covered every required skill at some level -- focus on projects and portfolio now.")
    return "\n".join(lines)


_HANDLERS = {
    "explain": _handle_explain,
    "quiz": _handle_quiz,
    "plan_day": _handle_plan_day,
    "find_resources": _handle_find_resources,
    "project_ideas": _handle_project_ideas,
    "revision": _handle_revision,
    "career_guidance": _handle_career_guidance,
}
