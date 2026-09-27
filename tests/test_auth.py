from tests.conftest import register_and_login, login
from app.models import User


def test_register_creates_user_and_redirects_to_onboarding(client, app):
    resp = register_and_login(client)
    assert resp.status_code == 302
    assert "/onboarding/step/1" in resp.headers["Location"]
    with app.app_context():
        assert User.query.filter_by(email="student@example.com").first() is not None


def test_register_rejects_short_password(client):
    resp = client.post("/auth/register", data={
        "name": "Bad Pass", "email": "bad@example.com", "password": "short", "confirm_password": "short",
    })
    assert resp.status_code == 200  # re-renders form with error


def test_register_rejects_duplicate_email(client):
    register_and_login(client, email="dupe@example.com")
    client.get("/auth/logout")
    resp = client.post("/auth/register", data={
        "name": "Dupe Two", "email": "dupe@example.com", "password": "TestPass123",
        "confirm_password": "TestPass123",
    })
    assert resp.status_code == 200


def test_login_with_valid_credentials(client):
    register_and_login(client, email="login@example.com", password="TestPass123")
    client.get("/auth/logout")
    resp = login(client, "login@example.com", "TestPass123")
    assert resp.status_code == 302


def test_login_with_invalid_credentials_shows_error(client):
    resp = login(client, "nobody@example.com", "wrongpass")
    assert resp.status_code == 200
    assert b"Invalid email or password" in resp.data


def test_logout_requires_login(client):
    resp = client.get("/auth/logout")
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]


def test_admin_cannot_be_created_via_register(client, app):
    register_and_login(client, email="notadmin@example.com")
    with app.app_context():
        user = User.query.filter_by(email="notadmin@example.com").first()
        assert user.role == "student"
        assert user.is_admin is False
