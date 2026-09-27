import re

import pytest

from app import create_app
from app.extensions import db
from app.models import (
    Stream, Skill, Career, Resource, Roadmap, RoadmapStage, RoadmapResource,
    Project, User,
)


@pytest.fixture
def app():
    application = create_app("testing")
    with application.app_context():
        db.create_all()
        _seed_minimal()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def csrf_token(client, path):
    resp = client.get(path)
    m = re.search(rb'name="csrf_token" value="([^"]+)"', resp.data)
    return m.group(1).decode() if m else None


def register_and_login(client, email="student@example.com", password="TestPass123"):
    resp = client.post(
        "/auth/register",
        data={"name": "Test Student", "email": email, "password": password, "confirm_password": password},
    )
    return resp


def login(client, email, password):
    return client.post("/auth/login", data={"email": email, "password": password})


def _seed_minimal():
    stream = Stream(name="B.Tech", slug="b-tech", category="technology")
    db.session.add(stream)

    python = Skill(name="Python", slug="python", category="programming")
    networking = Skill(name="Networking", slug="networking", category="security")
    sql = Skill(name="SQL", slug="sql", category="data")
    db.session.add_all([python, networking, sql])
    db.session.commit()

    security_fundamentals = Skill(
        name="Security Fundamentals", slug="security-fundamentals", category="security",
        prerequisite_skill_id=networking.id,
    )
    db.session.add(security_fundamentals)
    db.session.commit()

    r1 = Resource(
        title="Intro to Python", provider="Test Provider", url="https://example.com/python",
        category="technology", topic="Python", difficulty="beginner", duration_minutes=60,
        language="English", is_free=True, price_inr=0, resource_type="video", status="active",
    )
    r1.skill_tags = ["python"]
    r1.format_tags = ["video"]

    r2 = Resource(
        title="Advanced Networking", provider="Test Provider", url="https://example.com/networking",
        category="technology", topic="Networking", difficulty="advanced", duration_minutes=500,
        language="English", is_free=False, price_inr=999, resource_type="course", status="active",
    )
    r2.skill_tags = ["networking"]
    r2.format_tags = ["long-form"]

    db.session.add_all([r1, r2])
    db.session.commit()

    roadmap = Roadmap(title="Cybersecurity Analyst Roadmap", slug="cybersecurity-analyst-roadmap",
                       description="Test roadmap")
    db.session.add(roadmap)
    db.session.commit()

    stage = RoadmapStage(roadmap_id=roadmap.id, order=1, title="Networking", description="Learn networking",
                          estimated_hours=10)
    db.session.add(stage)
    db.session.commit()
    db.session.add(RoadmapResource(stage_id=stage.id, resource_id=r2.id, order=1))
    db.session.commit()

    career = Career(title="Cybersecurity Analyst", slug="cybersecurity-analyst",
                     description="Protects systems.", roadmap_id=roadmap.id)
    career.required_skills = ["networking", "security-fundamentals", "python"]
    career.degree_backgrounds = ["b-tech"]
    db.session.add(career)

    project = Project(title="Command-Line Calculator", difficulty="beginner", estimated_hours=3,
                       description="A simple calculator.")
    project.required_skills = ["python"]
    project.technologies = ["Python"]
    db.session.add(project)

    admin = User(name="Admin", email="admin@navora.app", role="admin", onboarding_complete=True)
    admin.set_password("AdminPass123")
    db.session.add(admin)

    db.session.commit()
