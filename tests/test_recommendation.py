from app.models import Resource, Career, LearningDNA, User, UserSkill, Skill
from app.recommendation.engine import score_resource, recommend_for_user
from app.extensions import db


def _make_user_with_dna(interests=None, career_goal=None, style=None, time_availability="1_hour_per_day",
                         budget="mostly_free", free_first=True):
    user = User(name="Scorer", email=f"scorer{id(object())}@example.com", role="student")
    user.set_password("Password123")
    db.session.add(user)
    db.session.commit()

    dna = LearningDNA(user_id=user.id)
    dna.interests = interests or []
    dna.career_goal = career_goal
    dna.learning_style = style or []
    dna.time_availability = time_availability
    dna.budget_preference = budget
    dna.free_first_mode = free_first
    dna.language = "English"
    db.session.add(dna)
    db.session.commit()
    return user


def test_free_resource_scores_higher_when_budget_is_completely_free(app):
    with app.app_context():
        free_res = Resource.query.filter_by(url="https://example.com/python").first()
        paid_res = Resource.query.filter_by(url="https://example.com/networking").first()
        user = _make_user_with_dna(budget="completely_free", free_first=True)

        free_score, _ = score_resource(free_res, learning_dna=user.learning_dna, user_skills=[])
        paid_score, _ = score_resource(paid_res, learning_dna=user.learning_dna, user_skills=[])
        assert free_score > paid_score


def test_career_relevance_adds_explanation_reason(app):
    with app.app_context():
        resource = Resource.query.filter_by(url="https://example.com/networking").first()
        career = Career.query.filter_by(slug="cybersecurity-analyst").first()
        user = _make_user_with_dna(career_goal="Cybersecurity Analyst")

        score, reasons = score_resource(resource, learning_dna=user.learning_dna, user_skills=[], career=career)
        assert any("Cybersecurity Analyst" in r for r in reasons)


def test_skill_level_fit_prefers_matching_difficulty(app):
    with app.app_context():
        beginner_res = Resource.query.filter_by(url="https://example.com/python").first()
        user = _make_user_with_dna()
        skill = Skill.query.filter_by(slug="python").first()
        us = UserSkill(user_id=user.id, skill_id=skill.id, level="beginner")
        db.session.add(us)
        db.session.commit()

        matched_score, _ = score_resource(beginner_res, learning_dna=user.learning_dna, user_skills=[us])
        mismatched_score, _ = score_resource(
            beginner_res, learning_dna=user.learning_dna,
            user_skills=[UserSkill(user_id=user.id, skill_id=skill.id, level="advanced")],
        )
        assert matched_score >= mismatched_score


def test_recommend_for_user_returns_ranked_list_excluding_ids(app):
    with app.app_context():
        user = _make_user_with_dna(career_goal="Cybersecurity Analyst")
        results = recommend_for_user(user, limit=5)
        assert len(results) > 0
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

        excluded_id = results[0]["resource"].id
        results2 = recommend_for_user(user, limit=5, exclude_resource_ids={excluded_id})
        assert all(r["resource"].id != excluded_id for r in results2)


def test_every_recommendation_has_at_least_one_reason(app):
    with app.app_context():
        user = _make_user_with_dna()
        results = recommend_for_user(user, limit=5)
        for r in results:
            assert len(r["reasons"]) >= 1
