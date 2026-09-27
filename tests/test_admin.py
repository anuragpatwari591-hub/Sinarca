from tests.conftest import register_and_login, login, csrf_token


def test_admin_dashboard_requires_login(client):
    resp = client.get("/admin/")
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]


def test_student_cannot_access_admin_dashboard(client):
    register_and_login(client, email="student.noadmin@example.com")
    resp = client.get("/admin/")
    assert resp.status_code == 403


def test_admin_can_access_dashboard(client):
    login(client, "admin@navora.app", "AdminPass123")
    resp = client.get("/admin/")
    assert resp.status_code == 200
    assert b"Admin Dashboard" in resp.data


def test_admin_can_create_resource(client, app):
    login(client, "admin@navora.app", "AdminPass123")
    token = csrf_token(client, "/admin/resources/new")
    resp = client.post("/admin/resources/new", data={
        "csrf_token": token, "title": "New Test Resource", "provider": "Provider",
        "url": "https://example.com/new-test-resource", "category": "technology", "topic": "Testing",
        "skill_tags": "python", "difficulty": "beginner", "duration_minutes": "20",
        "language": "English", "resource_type": "article", "status": "active",
    })
    assert resp.status_code == 302
    with app.app_context():
        from app.models import Resource
        assert Resource.query.filter_by(url="https://example.com/new-test-resource").first() is not None


def test_admin_can_delete_resource(client, app):
    login(client, "admin@navora.app", "AdminPass123")
    with app.app_context():
        from app.models import Resource
        resource_id = Resource.query.filter_by(url="https://example.com/python").first().id

    token = csrf_token(client, f"/admin/resources/{resource_id}/edit")
    resp = client.post(f"/admin/resources/{resource_id}/delete", data={"csrf_token": token})
    assert resp.status_code == 302
    with app.app_context():
        from app.models import Resource
        assert Resource.query.get(resource_id) is None


def test_student_cannot_delete_resource(client, app):
    register_and_login(client, email="cannot.delete@example.com")
    with app.app_context():
        from app.models import Resource
        resource_id = Resource.query.filter_by(url="https://example.com/python").first().id

    resp = client.post(f"/admin/resources/{resource_id}/delete", data={})
    assert resp.status_code == 403
    with app.app_context():
        from app.models import Resource
        assert Resource.query.get(resource_id) is not None


def test_admin_can_toggle_user_active(client, app):
    register_and_login(client, email="toggle.me@example.com")
    client.get("/auth/logout")
    login(client, "admin@navora.app", "AdminPass123")

    with app.app_context():
        from app.models import User
        target = User.query.filter_by(email="toggle.me@example.com").first()
        assert target.is_active_account is True
        target_id = target.id

    token = csrf_token(client, "/admin/users")
    resp = client.post(f"/admin/users/{target_id}/toggle-active", data={"csrf_token": token})
    assert resp.status_code == 302
    with app.app_context():
        from app.models import User
        target = User.query.get(target_id)
        assert target.is_active_account is False
