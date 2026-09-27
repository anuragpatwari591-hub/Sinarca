"""Skill gap analysis (spec section 19): current skills vs a target career."""

from app.models import Skill, Career


def analyze_skill_gap(user, career: Career):
    user_levels = {us.skill.slug: us.level for us in user.skills if us.skill}
    required_slugs = career.required_skills

    required_skills = Skill.query.filter(Skill.slug.in_(required_slugs)).all() if required_slugs else []
    by_slug = {s.slug: s for s in required_skills}

    have = []
    missing = []

    for slug in required_slugs:
        skill = by_slug.get(slug)
        if not skill:
            continue
        level = user_levels.get(slug)
        if level:
            have.append({"skill": skill, "level": level})
        else:
            missing.append(skill)

    # Recommended learning order: prerequisite-free skills first, then chains.
    def sort_key(skill):
        depth = 0
        cursor = skill
        seen = set()
        while cursor.prerequisite and cursor.prerequisite.id not in seen:
            seen.add(cursor.id)
            depth += 1
            cursor = cursor.prerequisite
        return depth

    missing_ordered = sorted(missing, key=sort_key)

    total_required = len(required_slugs) or 1
    readiness_pct = round(len(have) / total_required * 100)

    return {
        "career": career,
        "have": have,
        "missing": missing_ordered,
        "readiness_pct": readiness_pct,
    }
