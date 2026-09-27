# NAVORA

**Stop searching. Start knowing what to learn next.**

NAVORA is a personal learning navigator for students across every stream —
B.Tech, BCA, MCA, BBA, MBA, B.Com, CA, CS, CMA, BA, B.Sc, Law, Design,
Pharmacy and more. Instead of another course marketplace, it turns a
student's profile (stream, goals, learning style, time and budget) into an
explainable, personalized next action: the right resource, in the right
order, with a reason attached.

Built as a B.Tech Information Technology capstone project, designed to the
product bar of an early-stage ed-tech startup.

---

## Table of contents

- [Product overview](#product-overview)
- [Feature list](#feature-list)
- [Technology stack](#technology-stack)
- [Project structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database setup](#database-setup)
- [Running locally](#running-locally)
- [Demo account](#demo-account)
- [Testing](#testing)
- [Documentation index](#documentation-index)
- [What is NOT built yet](#what-is-not-built-yet)

## Product overview

The core loop: **Discover → Understand → Plan → Learn → Practice → Build →
Measure → Improve.**

A student completes a 7-step onboarding ("Learning DNA"), then gets:

- A personalized dashboard with a **"Your Next Move"** card — the single
  best next action, always with a plain-language reason.
- An **explainable recommendation engine** — every "why this resource?"
  explanation is generated from real, inspectable scoring factors, never a
  black box.
- **Structured roadmaps** broken into stages, each ending in a real project.
- A **Skill Gap** analysis against any target career.
- A **Career Explorer** with required skills, free/paid resources and
  interview prep notes.
- A **Free-First** discovery mode that prioritizes free resources unless a
  student explicitly opts into paid content.
- A deterministic **AI Study Mentor** (Explain / Quiz Me / Plan My Day /
  Find Resources / Project Ideas / Revision / Career Guidance) that works
  fully offline from an external AI API.
- A **Semester Mode** planner kept separate from career-skill roadmaps.
- **Bookmarks**, a **Comparison** tool, resource **reporting**, and a
  **personalization feedback loop** ("was this useful?").
- A full **admin panel** for users, resources, reports, and analytics.

## Feature list

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the authoritative, checked
list of what is built, partially built, or intentionally deferred.

## Technology stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python 3.11, Flask 3 | Simple, explainable, viva-friendly |
| ORM / DB | SQLAlchemy, SQLite (dev) / MySQL-ready (prod) | Relational integrity, easy to demo |
| Auth | Flask-Login + Werkzeug password hashing | Standard, well-understood session auth |
| Forms/CSRF | Flask-WTF (CSRFProtect) | CSRF protection on every state-changing form |
| Frontend | Server-rendered Jinja2, hand-written CSS/JS | No build step, fully explainable, fast |
| Tests | pytest | 30+ tests across auth, recommendations, search, admin, onboarding, skill gap |

No React, Node.js, MongoDB, Firebase, Docker/Kubernetes, blockchain, or
IoT — by design (see the project brief). The product can *look* advanced
while staying fully explainable in a viva.

## Project structure

```text
Sinarca/
├── app/
│   ├── routes/            # Flask blueprints (one per feature area)
│   ├── models/            # SQLAlchemy models
│   ├── recommendation/    # Explainable scoring engine + configurable weights
│   ├── services/          # skill gap, next-move, chatbot fallback, AI adapter
│   ├── templates/         # Jinja2 templates (NAVORA design system)
│   ├── static/            # CSS, JS, favicon
│   ├── utils/             # decorators (admin_required, onboarding_required)
│   └── constants.py       # shared choice-lists
├── seed/
│   └── seed_data.py       # streams, skills, careers, roadmaps, resources, demo account
├── tests/                 # pytest suite
├── docs/                  # architecture, database, API, security, business model, viva prep
├── config.py
├── run.py
├── requirements.txt
├── .env.example
└── PROJECT_STATUS.md
```

## Installation

```bash
git clone <this-repo-url>
cd Sinarca
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then edit .env if needed
```

## Configuration

All configuration is via environment variables (see `.env.example`):

- `SECRET_KEY` — Flask session signing key. **Change this for any real deployment.**
- `DATABASE_URL` — defaults to a local SQLite file. Set to a `mysql+pymysql://...`
  URL to run against MySQL in production (add `PyMySQL` to `requirements.txt` if so).
- `AI_PROVIDER_API_KEY` / `AI_PROVIDER_NAME` — optional. Leave blank; the
  platform is fully functional without them (see `docs/future-ai.md`).
- `ADMIN_EMAIL` / `ADMIN_PASSWORD` — used only by the seed script to create
  the admin account.

No secrets are committed to this repository. `.env` is git-ignored.

## Database setup

```bash
# Creates tables and populates streams, skills, careers, roadmaps,
# resources, projects, plus the demo student and admin accounts.
python -m seed.seed_data
```

This is idempotent — safe to re-run. See `docs/database.md` for the full schema.

## Running locally

```bash
source .venv/bin/activate
export FLASK_ENV=development   # Windows: set FLASK_ENV=development
python run.py
```

Visit `http://localhost:5000`.

## Demo account

For a fast, fully-populated walkthrough (spec section 50), either:

- Click **"See a live demo dashboard"** on the landing page (logs you into
  the Demo Student account instantly), or
- Log in manually with `demo.student@navora.app` / `DemoStudent123!`.

The demo account is a B.Tech IT, 2nd-year student targeting **Cybersecurity
Analyst**, with skills, roadmap progress, bookmarks and a study streak
already populated. **All of its data is demo data.**

Admin login: `admin@navora.app` / whatever `ADMIN_PASSWORD` was set to (default `ChangeMe123!` — change this before any real deployment).

## Testing

```bash
python -m pytest tests/ -v
```

31 tests cover registration/login, the full onboarding flow, the
recommendation engine's scoring logic, resource search/filtering, and admin
permission boundaries (students cannot reach admin routes; admins can CRUD
resources and manage users). See `docs/testing.md` for the full test plan
and what was manually verified in-browser.

## Documentation index

| Doc | Contents |
|---|---|
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | What's built vs. deferred, right now |
| [docs/architecture.md](docs/architecture.md) | System architecture, request lifecycle, module map |
| [docs/database.md](docs/database.md) | ER model and table-by-table notes |
| [docs/api.md](docs/api.md) | REST-style JSON endpoints |
| [docs/recommendation-engine.md](docs/recommendation-engine.md) | How scoring + explanations work |
| [docs/security.md](docs/security.md) | Auth, CSRF, input validation, what's out of scope |
| [docs/testing.md](docs/testing.md) | Test plan and manual verification checklist |
| [docs/deployment.md](docs/deployment.md) | How to deploy, what's required |
| [docs/business-model.md](docs/business-model.md) | Potential vs. actual revenue |
| [docs/future-ai.md](docs/future-ai.md) | The AI/LLM integration seam and what a v2 could add |
| [docs/viva-questions.md](docs/viva-questions.md) | B.Tech viva question bank with answers |
| [docs/presentation-outline.md](docs/presentation-outline.md) | 12-slide presentation outline |

## What is NOT built yet

Per the "no fabrication" principle, these are explicitly labeled **Coming
Soon** in the product rather than faked:

- Live affiliate network integration (clicks are tracked; no real network is connected).
- Real external LLM integration (a clean adapter seam exists; see `docs/future-ai.md`).
- Multi-language *content* (the schema and onboarding support Hindi/Bengali;
  seeded content is English-only).
- Community features (discussions, peer reviews) — intentionally out of
  scope per the product brief's "don't build a giant social network" guidance.
- A live sponsorship marketplace (the data model and disclosure UI exist; no sponsors are connected).

See `PROJECT_STATUS.md` for the complete, itemized list.
