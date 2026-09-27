import json
from datetime import datetime

from app.extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(300), nullable=False)
    category = db.Column(db.String(40), default="general")  # milestone|reminder|new_resource|broken_resource|project
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AdminAuditLog(db.Model):
    __tablename__ = "admin_audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(120), nullable=False)
    target = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admin = db.relationship("User")


class ChatMessage(db.Model):
    """History for the AI Study Mentor (spec section 17)."""

    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # user|assistant
    mode = db.Column(db.String(30), default="explain")
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SemesterPlan(db.Model):
    """Academic semester planning (spec section 25), kept separate from
    career-skill roadmaps so students don't lose sight of their degree."""

    __tablename__ = "semester_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    semester = db.Column(db.Integer)
    subjects_json = db.Column(db.Text, default="[]")
    weak_subjects_json = db.Column(db.Text, default="[]")
    exam_date = db.Column(db.Date, nullable=True)
    target_hours_per_week = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def subjects(self):
        return json.loads(self.subjects_json or "[]")

    @subjects.setter
    def subjects(self, value):
        self.subjects_json = json.dumps(value)

    @property
    def weak_subjects(self):
        return json.loads(self.weak_subjects_json or "[]")

    @weak_subjects.setter
    def weak_subjects(self, value):
        self.weak_subjects_json = json.dumps(value)
