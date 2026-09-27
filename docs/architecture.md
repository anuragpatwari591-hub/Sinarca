# Architecture

## Overview

NAVORA is a server-rendered Flask application following a fairly classic
MVC-ish shape, chosen specifically so it can be explained end-to-end in a
viva:

```
Browser
  │  HTTP (forms, GET/POST)
  ▼
Flask app (app/__init__.py: create_app factory)
  │
  ├── Blueprints (app/routes/*.py)      — HTTP layer: parse request, call services, render template
  ├── Services (app/services/*.py)      — business logic: skill gap, next move, chatbot fallback
  ├── Recommendation engine (app/recommendation/*.py) — explainable scoring
  ├── Models (app/models/*.py)          — SQLAlchemy ORM, one file per domain area
  └── Templates (app/templates/*)       — Jinja2, extending base.html
  │
  ▼
SQLite (dev) / MySQL (prod) via SQLAlchemy
```

## Why a monolith, not microservices

The product brief explicitly asks for a B.Tech-defensible system. A single
Flask app with clear internal module boundaries (routes / services /
recommendation / models) gets the same separation of concerns a
microservice architecture would provide, without the operational
complexity of service discovery, network calls, or container orchestration
— none of which would add explanatory value in a viva.

## Application factory

`app/__init__.py` exposes `create_app(config_name)`, which:

1. Loads configuration from `config.py` (`DevelopmentConfig` /
   `TestingConfig` / `ProductionConfig`).
2. Initializes extensions (`SQLAlchemy`, `Flask-Login`, `Flask-WTF`'s
   `CSRFProtect`).
3. Registers a `user_loader` for Flask-Login.
4. Registers all blueprints (`register_blueprints`).
5. Registers 404/403/500 error handlers that render branded pages instead
   of leaking stack traces.
6. Injects `platform_name` / `platform_tagline` into every template via a
   context processor.

Using a factory (rather than a module-level `app = Flask(__name__)`) is
what lets `tests/conftest.py` spin up a fresh, isolated app per test with
an in-memory SQLite database (`config.TestingConfig`).

## Request lifecycle example: viewing a resource

1. `GET /resources/<id>` hits `resources_bp.detail` (`app/routes/resources.py`).
2. The view loads the `Resource` row, and — if the visitor is a logged-in
   student — calls `app.recommendation.engine.score_resource()` to compute
   a personalized score and a list of human-readable reasons.
3. It also checks `LearningProgress` and `Bookmark` to know whether to show
   "mark complete" vs. "in progress", and "save" vs. "remove bookmark".
4. Everything is passed into `resources/detail.html`, which renders the
   "Why this resource?" box directly from the `reasons` list — there is no
   separate "explanation service"; the same data structure that produced
   the ranking also produces the explanation, which is what keeps the
   engine honest (see `docs/recommendation-engine.md`).

## The "Your Next Move" pipeline

`app/services/next_move.py::get_next_move(user)`:

1. Resolves the student's career goal to a `Career` row (if one matches).
2. Resolves that career's linked `Roadmap` and the student's current
   `UserRoadmapProgress` stage.
3. Scores every not-yet-completed resource in that stage (or, if no stage
   applies, every active resource site-wide) with the same
   `score_resource()` function used everywhere else.
4. Returns the single highest-scoring resource, its reasons, and a
   suggested "after this" project pulled from the stage's milestone
   project.

This is deliberately the *same* scoring function as the resource list and
the dashboard's "Recommended next" section — one engine, several views,
never three different notions of "relevance".

## AI/LLM integration seam

`app/services/ai_adapter.py` is the single point where an external LLM
would be called. Every caller (currently only the AI Study Mentor) tries
the adapter first and falls back to `app/services/chatbot_fallback.py` — a
deterministic, database-driven engine — if `AIAdapterNotConfigured` is
raised (which it always is, since no provider key is configured by
default). This guarantees the product never breaks or degrades silently
if an external AI vendor is unavailable or unaffordable. See
`docs/future-ai.md`.

## Module map

| Module | Responsibility |
|---|---|
| `app/routes/main.py` | Landing page, discover, legal pages, demo login |
| `app/routes/auth.py` | Registration, login, logout |
| `app/routes/onboarding.py` | 7-step Learning DNA wizard (session-backed until final commit) |
| `app/routes/dashboard.py` | Personalized dashboard aggregation |
| `app/routes/resources.py` | Search/filter, detail, progress, bookmarks, reports, feedback, click-through |
| `app/routes/roadmap.py` | Roadmap listing/detail, stage progress |
| `app/routes/projects.py` | Project listing/detail, status tracking |
| `app/routes/skillgap.py` | Skill Gap Analysis view |
| `app/routes/career.py` | Career Explorer |
| `app/routes/chatbot.py` | AI Study Mentor UI + message handling |
| `app/routes/bookmarks.py` | Bookmark folders |
| `app/routes/compare.py` | Resource comparison table |
| `app/routes/semester.py` | Semester Mode planner |
| `app/routes/admin.py` | Admin dashboard, CRUD, reports, analytics |
| `app/routes/api.py` | JSON REST-style endpoints |
| `app/recommendation/engine.py` | Explainable scoring |
| `app/services/skill_gap.py` | Career vs. current-skills gap analysis |
| `app/services/next_move.py` | "Your Next Move" signature feature |
| `app/services/chatbot_fallback.py` | Deterministic AI Study Mentor logic |
| `app/services/ai_adapter.py` | External LLM integration seam (unconfigured by default) |
