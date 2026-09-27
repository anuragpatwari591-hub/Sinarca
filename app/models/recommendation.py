import json
from datetime import datetime

from app.extensions import db


class Recommendation(db.Model):
    """A stored, explainable recommendation shown to a user."""

    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)
    score = db.Column(db.Float, nullable=False)
    reasons_json = db.Column(db.Text, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    resource = db.relationship("Resource")
    feedback = db.relationship("RecommendationFeedback", backref="recommendation", uselist=False)

    @property
    def reasons(self):
        return json.loads(self.reasons_json or "[]")

    @reasons.setter
    def reasons(self, value):
        self.reasons_json = json.dumps(value)


class RecommendationFeedback(db.Model):
    """The personalization learning loop (spec section 34)."""

    __tablename__ = "recommendation_feedback"

    id = db.Column(db.Integer, primary_key=True)
    recommendation_id = db.Column(db.Integer, db.ForeignKey("recommendations.id"), nullable=False, unique=True)
    useful = db.Column(db.Boolean, nullable=False)
    reason = db.Column(db.String(60), nullable=True)  # too_difficult|too_long|boring|wrong_topic|already_knew|wrong_style|not_relevant
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
