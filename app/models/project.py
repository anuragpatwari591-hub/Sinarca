import json

from app.extensions import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(20), default="beginner")
    description = db.Column(db.Text)
    estimated_hours = db.Column(db.Integer, default=5)
    required_skills_json = db.Column(db.Text, default="[]")
    technologies_json = db.Column(db.Text, default="[]")
    learning_outcomes_json = db.Column(db.Text, default="[]")
    github_checklist_json = db.Column(db.Text, default="[]")
    portfolio_description = db.Column(db.Text)

    @property
    def required_skills(self):
        return json.loads(self.required_skills_json or "[]")

    @required_skills.setter
    def required_skills(self, value):
        self.required_skills_json = json.dumps(value)

    @property
    def technologies(self):
        return json.loads(self.technologies_json or "[]")

    @technologies.setter
    def technologies(self, value):
        self.technologies_json = json.dumps(value)

    @property
    def learning_outcomes(self):
        return json.loads(self.learning_outcomes_json or "[]")

    @learning_outcomes.setter
    def learning_outcomes(self, value):
        self.learning_outcomes_json = json.dumps(value)

    @property
    def github_checklist(self):
        return json.loads(self.github_checklist_json or "[]")

    @github_checklist.setter
    def github_checklist(self, value):
        self.github_checklist_json = json.dumps(value)


class UserProject(db.Model):
    __tablename__ = "user_projects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    status = db.Column(db.String(20), default="planned")  # planned|in_progress|completed
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    repo_url = db.Column(db.String(300), nullable=True)

    project = db.relationship("Project")

    __table_args__ = (db.UniqueConstraint("user_id", "project_id", name="uq_user_project"),)
