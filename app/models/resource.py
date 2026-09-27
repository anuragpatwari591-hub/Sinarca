import json
from datetime import datetime

from app.extensions import db


class Resource(db.Model):
    __tablename__ = "resources"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(220), nullable=False)
    provider = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(80))  # matches Stream.category loosely
    topic = db.Column(db.String(120))
    skill_tags_json = db.Column(db.Text, default="[]")  # list of skill slugs

    difficulty = db.Column(db.String(20), default="beginner")  # beginner|intermediate|advanced
    duration_minutes = db.Column(db.Integer)  # estimated total duration
    language = db.Column(db.String(40), default="English")

    is_free = db.Column(db.Boolean, default=True, nullable=False)
    price_inr = db.Column(db.Integer, default=0)

    rating = db.Column(db.Float, nullable=True)  # None => "Rating unavailable"
    rating_count = db.Column(db.Integer, nullable=True)
    rating_source = db.Column(db.String(120), nullable=True)  # e.g. "YouTube", "Platform reviews"

    description = db.Column(db.Text)
    prerequisites = db.Column(db.Text)
    resource_type = db.Column(db.String(40), default="video")  # video|article|docs|course|book|practice|project
    format_tags_json = db.Column(db.Text, default="[]")  # video, reading, interactive, project-first...

    last_verified_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="active")  # active|broken|under_review|removed
    verification_notes = db.Column(db.Text)

    is_sponsored = db.Column(db.Boolean, default=False)
    affiliate_url = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def skill_tags(self):
        return json.loads(self.skill_tags_json or "[]")

    @skill_tags.setter
    def skill_tags(self, value):
        self.skill_tags_json = json.dumps(value)

    @property
    def format_tags(self):
        return json.loads(self.format_tags_json or "[]")

    @format_tags.setter
    def format_tags(self, value):
        self.format_tags_json = json.dumps(value)

    @property
    def has_real_rating(self):
        return self.rating is not None and self.rating_count is not None and self.rating_count > 0

    @property
    def click_url(self):
        """The outbound link. Affiliate URL only if explicitly configured."""
        return self.affiliate_url or self.url


class Report(db.Model):
    """Student-submitted quality report on a resource (spec section 29)."""

    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    report_type = db.Column(db.String(40), nullable=False)  # broken_link|outdated|misleading|wrong_category|wrong_price
    details = db.Column(db.Text)
    status = db.Column(db.String(20), default="open")  # open|reviewing|resolved|dismissed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    resource = db.relationship("Resource")
