from datetime import datetime

from app.extensions import db


class Roadmap(db.Model):
    __tablename__ = "roadmaps"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text)

    stages = db.relationship(
        "RoadmapStage", backref="roadmap", order_by="RoadmapStage.order",
        cascade="all, delete-orphan",
    )


class RoadmapStage(db.Model):
    __tablename__ = "roadmap_stages"

    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey("roadmaps.id"), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=1)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    estimated_hours = db.Column(db.Integer, default=10)
    milestone_project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True)

    resources = db.relationship(
        "RoadmapResource", backref="stage", order_by="RoadmapResource.order",
        cascade="all, delete-orphan",
    )
    milestone_project = db.relationship("Project")


class RoadmapResource(db.Model):
    __tablename__ = "roadmap_resources"

    id = db.Column(db.Integer, primary_key=True)
    stage_id = db.Column(db.Integer, db.ForeignKey("roadmap_stages.id"), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)
    order = db.Column(db.Integer, default=1)

    resource = db.relationship("Resource")


class UserRoadmapProgress(db.Model):
    """Tracks which stage a user has reached in a roadmap."""

    __tablename__ = "user_roadmap_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    roadmap_id = db.Column(db.Integer, db.ForeignKey("roadmaps.id"), nullable=False)
    current_stage_order = db.Column(db.Integer, default=1)
    completed_stage_orders_json = db.Column(db.Text, default="[]")
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roadmap = db.relationship("Roadmap")

    __table_args__ = (db.UniqueConstraint("user_id", "roadmap_id", name="uq_user_roadmap"),)

    @property
    def completed_stage_orders(self):
        import json
        return json.loads(self.completed_stage_orders_json or "[]")

    def mark_stage_complete(self, order):
        import json
        done = set(self.completed_stage_orders)
        done.add(order)
        self.completed_stage_orders_json = json.dumps(sorted(done))
        self.current_stage_order = max(self.current_stage_order or 1, order + 1)
