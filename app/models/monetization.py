from datetime import datetime

from app.extensions import db


class AffiliateClick(db.Model):
    """Tracks outbound clicks to resources so future affiliate revenue can be
    attributed. No real affiliate network is connected yet (see docs/business-model.md)."""

    __tablename__ = "affiliate_clicks"

    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
    was_affiliate = db.Column(db.Boolean, default=False)

    resource = db.relationship("Resource")


class SponsoredContent(db.Model):
    """Clearly-labeled sponsored placements (spec section 16)."""

    __tablename__ = "sponsored_content"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    sponsor_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(80))
    is_active = db.Column(db.Boolean, default=True)
    starts_at = db.Column(db.DateTime, default=datetime.utcnow)
    ends_at = db.Column(db.DateTime, nullable=True)
