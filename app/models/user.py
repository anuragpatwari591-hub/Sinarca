import json
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")  # student | admin
    is_active_account = db.Column(db.Boolean, default=True, nullable=False)
    onboarding_complete = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    education_profile = db.relationship(
        "EducationProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    learning_dna = db.relationship(
        "LearningDNA", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    skills = db.relationship("UserSkill", backref="user", cascade="all, delete-orphan")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    @property
    def is_admin(self):
        return self.role == "admin"

    # Flask-Login uses is_active; we alias to our own explicit account flag
    @property
    def is_active(self):
        return self.is_active_account

    def __repr__(self):
        return f"<User {self.email}>"


class EducationProfile(db.Model):
    __tablename__ = "education_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    stream_id = db.Column(db.Integer, db.ForeignKey("streams.id"), nullable=True)
    degree = db.Column(db.String(120))
    specialization = db.Column(db.String(120))
    college = db.Column(db.String(200))
    year = db.Column(db.Integer)
    semester = db.Column(db.Integer)

    stream = db.relationship("Stream")


class LearningDNA(db.Model):
    """The captured 'Learning DNA' profile from onboarding (spec section 7)."""

    __tablename__ = "learning_dna"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    interests_json = db.Column(db.Text, default="[]")
    career_goal = db.Column(db.String(150))
    learning_style_json = db.Column(db.Text, default="[]")  # video, reading, project-first, etc.
    time_availability = db.Column(db.String(40))  # e.g. "1_hour_per_day"
    language = db.Column(db.String(40), default="English")
    budget_preference = db.Column(db.String(40), default="mostly_free")
    free_first_mode = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def interests(self):
        return json.loads(self.interests_json or "[]")

    @interests.setter
    def interests(self, value):
        self.interests_json = json.dumps(value)

    @property
    def learning_style(self):
        return json.loads(self.learning_style_json or "[]")

    @learning_style.setter
    def learning_style(self, value):
        self.learning_style_json = json.dumps(value)
