import os

from flask import Flask, render_template

from config import config_by_name
from app.extensions import db, login_manager, csrf


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    register_blueprints(app)
    register_error_handlers(app)
    register_context_processors(app)

    return app


def register_blueprints(app):
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.onboarding import onboarding_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.resources import resources_bp
    from app.routes.roadmap import roadmap_bp
    from app.routes.projects import projects_bp
    from app.routes.skillgap import skillgap_bp
    from app.routes.career import career_bp
    from app.routes.chatbot import chatbot_bp
    from app.routes.bookmarks import bookmarks_bp
    from app.routes.compare import compare_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    from app.routes.semester import semester_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(onboarding_bp, url_prefix="/onboarding")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(resources_bp, url_prefix="/resources")
    app.register_blueprint(roadmap_bp, url_prefix="/roadmaps")
    app.register_blueprint(projects_bp, url_prefix="/projects")
    app.register_blueprint(skillgap_bp, url_prefix="/skill-gap")
    app.register_blueprint(career_bp, url_prefix="/careers")
    app.register_blueprint(chatbot_bp, url_prefix="/mentor")
    app.register_blueprint(bookmarks_bp, url_prefix="/bookmarks")
    app.register_blueprint(compare_bp, url_prefix="/compare")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(semester_bp, url_prefix="/semester")


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500


def register_context_processors(app):
    @app.context_processor
    def inject_globals():
        return {
            "platform_name": app.config["PLATFORM_NAME"],
            "platform_tagline": app.config["PLATFORM_TAGLINE"],
        }
