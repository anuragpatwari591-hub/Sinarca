"""
AI / LLM Integration Adapter (spec section 5).

This is the single seam where a future production build would plug in an
external LLM (e.g. the Claude API) to power richer explanations or a more
flexible AI Study Mentor. The rest of the application never calls an LLM
directly -- it only ever calls functions in this module, or the deterministic
fallback in `app.services.chatbot_fallback`.

Today, AI_PROVIDER_API_KEY is unset by default, so `is_configured()` returns
False and every caller falls back to the deterministic, explainable engine.
This is a deliberate product decision (spec section 5): the platform must
stay fully functional -- and fully explainable -- without depending on a
paid external API.
"""

from flask import current_app


class AIAdapterNotConfigured(Exception):
    pass


def is_configured():
    return bool(current_app.config.get("AI_PROVIDER_API_KEY"))


def generate(prompt: str, context: dict | None = None) -> str:
    """
    Would call the configured external LLM provider (e.g. Claude API) with
    `prompt` and structured `context` (user's Learning DNA, roadmap position,
    recent activity). Not implemented in this build -- no external AI vendor
    credentials are configured for this project -- so it always raises
    AIAdapterNotConfigured, and callers are expected to catch this and use
    the deterministic fallback so the feature never breaks for the student.
    """
    if not is_configured():
        raise AIAdapterNotConfigured(
            "No AI_PROVIDER_API_KEY configured. Using the deterministic fallback engine."
        )
    raise NotImplementedError(
        "External LLM integration is not wired up in this build. "
        "See docs/future-ai.md for the planned integration."
    )
