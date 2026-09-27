from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from app.extensions import db
from app.models import ChatMessage
from app.constants import CHATBOT_MODES
from app.services import chatbot_fallback
from app.services.ai_adapter import generate as ai_generate, is_configured, AIAdapterNotConfigured

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/", methods=["GET", "POST"])
@login_required
def mentor():
    mode = request.values.get("mode", "explain")

    if request.method == "POST":
        message = request.form.get("message", "").strip()
        if message:
            db.session.add(ChatMessage(user_id=current_user.id, role="user", mode=mode, content=message))
            try:
                reply = ai_generate(message, context={"user_id": current_user.id, "mode": mode})
            except AIAdapterNotConfigured:
                reply = chatbot_fallback.handle_message(current_user, mode, message)
            db.session.add(ChatMessage(user_id=current_user.id, role="assistant", mode=mode, content=reply))
            db.session.commit()
        return redirect(url_for("chatbot.mentor", mode=mode))

    history = (
        ChatMessage.query.filter_by(user_id=current_user.id)
        .order_by(ChatMessage.created_at.desc()).limit(20).all()
    )
    history.reverse()
    return render_template(
        "chatbot/mentor.html", history=history, modes=CHATBOT_MODES, mode=mode,
        ai_configured=is_configured(),
    )
