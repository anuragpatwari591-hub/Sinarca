from tests.conftest import register_and_login, csrf_token


def _complete_onboarding(client, stream_id=1):
    steps = [
        (1, {"stream_id": str(stream_id), "degree": "B.Tech", "specialization": "IT",
             "college": "Test College", "year": "2", "semester": "3"}),
        (2, {"interests": ["Cybersecurity"]}),
        (3, {}),
        (4, {"career_goal": "Cybersecurity Analyst"}),
        (5, {"learning_style": ["video"]}),
        (6, {"time_availability": "1_hour_per_day", "language": "English"}),
        (7, {"budget_preference": "mostly_free", "free_first_mode": "on"}),
    ]
    last_resp = None
    for step, form in steps:
        token = csrf_token(client, f"/onboarding/step/{step}")
        form["csrf_token"] = token
        last_resp = client.post(f"/onboarding/step/{step}", data=form)
    return last_resp


def test_full_onboarding_flow_sets_learning_dna(client, app):
    register_and_login(client, email="onboard@example.com")
    resp = _complete_onboarding(client)
    assert resp.status_code == 302
    assert "/dashboard" in resp.headers["Location"]

    with app.app_context():
        from app.models import User
        user = User.query.filter_by(email="onboard@example.com").first()
        assert user.onboarding_complete is True
        assert user.learning_dna.career_goal == "Cybersecurity Analyst"
        assert "Cybersecurity" in user.learning_dna.interests


def test_dashboard_redirects_to_onboarding_if_incomplete(client):
    register_and_login(client, email="incomplete@example.com")
    resp = client.get("/dashboard/")
    assert resp.status_code == 302
    assert "/onboarding/step/1" in resp.headers["Location"]


def test_dashboard_accessible_after_onboarding(client):
    register_and_login(client, email="complete@example.com")
    _complete_onboarding(client)
    resp = client.get("/dashboard/")
    assert resp.status_code == 200
    assert b"Your Next Move" in resp.data or b"YOUR NEXT MOVE" in resp.data
