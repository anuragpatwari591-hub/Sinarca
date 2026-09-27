from app.extensions import db
from app.models import UserSkill, Skill, User, Career
from app.services.skill_gap import analyze_skill_gap


def test_skill_gap_identifies_missing_skills(app):
    with app.app_context():
        user = User(name="Gap Test", email="gap@example.com", role="student")
        user.set_password("Password123")
        db.session.add(user)
        db.session.commit()

        python_skill = Skill.query.filter_by(slug="python").first()
        db.session.add(UserSkill(user_id=user.id, skill_id=python_skill.id, level="intermediate"))
        db.session.commit()

        career = Career.query.filter_by(slug="cybersecurity-analyst").first()
        gap = analyze_skill_gap(user, career)

        have_slugs = {h["skill"].slug for h in gap["have"]}
        missing_slugs = {s.slug for s in gap["missing"]}

        assert "python" in have_slugs
        assert "networking" in missing_slugs
        assert 0 < gap["readiness_pct"] < 100


def test_skill_gap_full_readiness_when_all_skills_present(app):
    with app.app_context():
        user = User(name="Ready", email="ready@example.com", role="student")
        user.set_password("Password123")
        db.session.add(user)
        db.session.commit()

        career = Career.query.filter_by(slug="cybersecurity-analyst").first()
        for slug in career.required_skills:
            skill = Skill.query.filter_by(slug=slug).first()
            db.session.add(UserSkill(user_id=user.id, skill_id=skill.id, level="advanced"))
        db.session.commit()

        gap = analyze_skill_gap(user, career)
        assert gap["readiness_pct"] == 100
        assert gap["missing"] == []
