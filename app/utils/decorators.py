from functools import wraps

from flask import abort
from flask_login import current_user


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped


def onboarding_required(view_func):
    """Redirects a logged-in student to onboarding if their Learning DNA is incomplete."""
    from flask import redirect, url_for

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if current_user.is_authenticated and not current_user.is_admin and not current_user.onboarding_complete:
            return redirect(url_for("onboarding.step", step_number=1))
        return view_func(*args, **kwargs)

    return wrapped
