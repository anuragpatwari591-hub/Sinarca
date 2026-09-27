from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user

from app.models import User, Stream, Career, Resource, Roadmap

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def landing():
    stats = {
        "streams": Stream.query.count(),
        "resources": Resource.query.filter_by(status="active").count(),
        "careers": Career.query.count(),
        "roadmaps": Roadmap.query.count(),
    }
    streams = Stream.query.order_by(Stream.name).limit(12).all()
    featured_roadmaps = Roadmap.query.limit(3).all()
    return render_template("main/landing.html", stats=stats, streams=streams, featured_roadmaps=featured_roadmaps)


@main_bp.route("/demo")
def demo_login():
    """Logs the reviewer straight into the pre-populated Demo Student account
    (spec section 50). Clearly a demo account, seeded with demo data only."""
    demo = User.query.filter_by(email="demo.student@navora.app").first()
    if not demo:
        flash("Demo account not found. Run the seed script first (see README).", "warning")
        return redirect(url_for("main.landing"))
    login_user(demo)
    flash("You're viewing the NAVORA Demo Student account — all data here is demo data.", "info")
    return redirect(url_for("dashboard.home"))


@main_bp.route("/discover")
def discover():
    """'I don't know what to learn' entry point (spec section 48)."""
    careers = Career.query.limit(8).all()
    return render_template("main/discover.html", careers=careers)


@main_bp.route("/privacy")
def privacy():
    return render_template("main/privacy.html")


@main_bp.route("/terms")
def terms():
    return render_template("main/terms.html")


@main_bp.route("/disclosures")
def disclosures():
    return render_template("main/disclosures.html")


@main_bp.route("/about")
def about():
    return render_template("main/about.html")
