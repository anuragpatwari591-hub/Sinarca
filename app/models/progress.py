from datetime import datetime

from app.extensions import db


class LearningProgress(db.Model):
    __tablename__ = "learning_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)
    status = db.Column(db.String(20), default="not_started")  # not_started|in_progress|completed
    progress_pct = db.Column(db.Integer, default=0)
    time_spent_minutes = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resource = db.relationship("Resource")

    __table_args__ = (db.UniqueConstraint("user_id", "resource_id", name="uq_user_resource_progress"),)


class StudySession(db.Model):
    __tablename__ = "study_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, default=lambda: datetime.utcnow().date())
    minutes = db.Column(db.Integer, default=0)
    topic = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Bookmark(db.Model):
    __tablename__ = "bookmarks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    target_type = db.Column(db.String(20), nullable=False)  # resource|project|roadmap|career
    target_id = db.Column(db.Integer, nullable=False)
    folder = db.Column(db.String(60), default="Learn Later")  # Learn Later|Projects|Interview|Semester|Career
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "target_type", "target_id", name="uq_bookmark"),
    )
