from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Bookmark, Resource, Project, Roadmap, Career
from app.constants import BOOKMARK_FOLDERS

bookmarks_bp = Blueprint("bookmarks", __name__)

_TARGET_MODELS = {"resource": Resource, "project": Project, "roadmap": Roadmap, "career": Career}


@bookmarks_bp.route("/")
@login_required
def index():
    folder = request.args.get("folder", "")
    query = Bookmark.query.filter_by(user_id=current_user.id)
    if folder:
        query = query.filter_by(folder=folder)
    bookmarks = query.order_by(Bookmark.created_at.desc()).all()

    items = []
    for b in bookmarks:
        model = _TARGET_MODELS.get(b.target_type)
        target = model.query.get(b.target_id) if model else None
        if target:
            items.append({"bookmark": b, "target": target})

    return render_template("bookmarks/index.html", items=items, folders=BOOKMARK_FOLDERS, current_folder=folder)


@bookmarks_bp.route("/<int:bookmark_id>/remove", methods=["POST"])
@login_required
def remove(bookmark_id):
    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=current_user.id).first_or_404()
    db.session.delete(bookmark)
    db.session.commit()
    flash("Removed from bookmarks.", "info")
    return redirect(url_for("bookmarks.index"))
