import json

from app.extensions import db


class Stream(db.Model):
    __tablename__ = "streams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(60))  # technology / commerce / management / professional / arts / science / law
    description = db.Column(db.Text)


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(60))
    description = db.Column(db.Text)
    prerequisite_skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=True)

    prerequisite = db.relationship("Skill", remote_side=[id])


class UserSkill(db.Model):
    __tablename__ = "user_skills"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    level = db.Column(db.String(20), default="beginner")  # beginner | intermediate | advanced
    self_rated = db.Column(db.Boolean, default=True)

    skill = db.relationship("Skill")

    __table_args__ = (db.UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),)


class Career(db.Model):
    __tablename__ = "careers"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text)
    required_skills_json = db.Column(db.Text, default="[]")  # list of skill slugs
    degree_backgrounds_json = db.Column(db.Text, default="[]")  # list of stream slugs
    portfolio_requirements = db.Column(db.Text)
    interview_prep_notes = db.Column(db.Text)
    roadmap_id = db.Column(db.Integer, db.ForeignKey("roadmaps.id"), nullable=True)

    @property
    def required_skills(self):
        return json.loads(self.required_skills_json or "[]")

    @required_skills.setter
    def required_skills(self, value):
        self.required_skills_json = json.dumps(value)

    @property
    def degree_backgrounds(self):
        return json.loads(self.degree_backgrounds_json or "[]")

    @degree_backgrounds.setter
    def degree_backgrounds(self, value):
        self.degree_backgrounds_json = json.dumps(value)
