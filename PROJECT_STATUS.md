# PROJECT_STATUS

Last updated: this session (initial build). The repository had no prior
commits — this is a from-scratch build of NAVORA on branch
`claude/trusting-brown-g0gqgk`.

## Current state: functional, tested, documented MVP

The application boots, the seed script populates a realistic multi-stream
dataset plus a working Demo Student and Admin account, and the full
student-facing loop (register → onboard → dashboard → discover →
roadmap → skill gap → career → project → AI mentor → bookmarks →
semester planner) and the full admin loop (dashboard → users → resources
CRUD → reports → skills/careers/roadmaps/projects listings → sponsored →
analytics) have been exercised end-to-end via scripted HTTP requests
against a running instance, in addition to 31 passing pytest tests.

## Completed features (built and verified)

### User-facing
- [x] Registration / login / logout (server-side validation, hashed passwords)
- [x] 7-step onboarding building a "Learning DNA" profile
- [x] Personalized dashboard: "Your Next Move", continue learning,
      roadmap progress, skill progress, recommended next, weekly goal,
      streak, upcoming projects, notifications
- [x] Explainable recommendation engine ("Why this resource?" everywhere)
- [x] Resource discovery / search with filters (free/paid, difficulty,
      type, language, topic, text search)
- [x] Resource detail page: progress tracking, bookmarking, feedback,
      reporting, outbound click tracking
- [x] Structured roadmaps with stages, resources, and milestone projects
- [x] Project directory with difficulty filter, required skills, GitHub
      checklist, status tracking (planned/in progress/completed)
- [x] Skill Gap Analysis against any career, with prerequisite-ordered
      missing-skill list
- [x] Career Explorer (required skills, degree backgrounds, portfolio
      requirements, interview prep, linked roadmap, matching resources
      and projects)
- [x] AI Study Mentor with 7 deterministic modes (Explain, Quiz Me, Plan
      My Day, Find Resources, Project Ideas, Revision, Career Guidance),
      with a clean seam for a future external LLM
- [x] Bookmarks with folders (Learn Later / Projects / Interview /
      Semester / Career)
- [x] Resource comparison table (multi-select from search results)
- [x] Semester Mode planner (separate from career-skill roadmaps)
- [x] Free-First mode toggle affecting recommendation scoring
- [x] "I don't know what to learn" discovery entry point
- [x] Demo Student account, fully pre-populated
- [x] Legal pages: Privacy Policy, Terms of Use, Affiliate/Sponsorship
      Disclosure, About

### Admin-facing
- [x] Admin dashboard with real counts (users, resources, reports, clicks)
      and popular-stream/topic breakdowns
- [x] User management (search, view, activate/deactivate)
- [x] Resource CRUD (create/edit/delete, all fields including rating —
      which is left blank/"unavailable" unless a real source is entered)
- [x] Report review queue with status workflow
- [x] Skills management (add)
- [x] Read-only Careers / Roadmaps / Projects listings (content managed
      via the seed script in this build — see "Known limitations" below)
- [x] Sponsored content listing (honest "Coming Soon" empty state)
- [x] Basic analytics (resource starts, completions, bookmarks)
- [x] Every admin action writes an `AdminAuditLog` row

### Engineering
- [x] Normalized-enough relational schema (see `docs/database.md`) with
      FKs and unique constraints
- [x] Flask-Login authentication + Flask-WTF CSRF protection on every form
- [x] Role-based authorization (`@admin_required`), verified by tests to
      reject students with 403 and anonymous users with a login redirect
- [x] Input validation on registration; parameterized queries throughout
      (SQLAlchemy ORM); Jinja2 auto-escaping (no `|safe` on user content)
- [x] Branded 404 / 403 / 500 error pages
- [x] Responsive CSS design system (NAVORA brand: indigo/amber, Inter
      typeface, cards/badges/progress bars/chat bubbles/skeleton states)
- [x] 31 passing pytest tests (`tests/`)
- [x] Full documentation set (`docs/`, this file, `README.md`)
- [x] `.env.example`, `.gitignore` — no secrets committed

## Explicitly deferred / "Coming Soon" (never faked)

These are honestly labeled in the product itself, not silently missing:

- [ ] **Live affiliate network integration** — clicks are tracked
      (`affiliate_clicks`), `Resource.affiliate_url` is a real field, but
      no actual affiliate program is connected. Disclosed on `/disclosures`.
- [ ] **Live sponsorship marketplace** — schema + admin page exist and
      correctly render "No sponsors are connected in this build."
- [ ] **External LLM / AI integration** — `app/services/ai_adapter.py` is a
      real, working seam (`is_configured()` / `generate()`), unconfigured
      by default. See `docs/future-ai.md`.
- [ ] **Multi-language content** — the schema and onboarding fully support
      Hindi/Bengali as a `language` value; seeded resource content itself
      is English-only (translating real resource metadata was out of
      scope for this session).
- [ ] **Admin UI for Careers/Roadmaps/Projects editing** — currently
      read-only in the admin panel; content is managed via
      `seed/seed_data.py`. Both pages say so explicitly rather than
      presenting broken "Edit" buttons.
- [ ] **Community features** (discussions, peer reviews, study groups) —
      intentionally out of scope per the product brief's own guidance not
      to build a large social network unless it clearly improves the core
      guidance product.
- [ ] **Rate limiting, email verification, password reset** — see
      `docs/security.md`'s explicit "out of scope" section.
- [ ] **Flask-Migrate / Alembic** — schema is created via `db.create_all()`
      from the seed script; fine for this build's stage, flagged as the
      first thing to add before evolving the schema against real user data.
- [ ] **MySQL verification** — developed and tested against SQLite only;
      the ORM layer should be MySQL-compatible but this was not verified
      live in this session (no MySQL instance was available).
- [ ] **Actual deployment** — not deployed to a public URL in this session
      (no hosting credentials/target provided). `docs/deployment.md`
      documents exactly what's required.

## Architecture at a glance

See `docs/architecture.md` for the full write-up. Summary: Flask
application-factory pattern, blueprints per feature area, a single
explainable recommendation engine (`app/recommendation/engine.py`) used
consistently by the dashboard, search, resource detail, and "Your Next
Move", and a deterministic services layer (`app/services/`) for skill gap,
next-move computation, and the AI mentor's fallback logic.

## How to verify this yourself

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m seed.seed_data
python -m pytest tests/ -v   # 31 passed
python run.py                # visit http://localhost:5000, try /demo
```

## Continuation notes (if a future session picks this up)

Nothing was left mid-implementation — every task below was carried to a
tested, working state in this session:

1. Models → 2. App factory/infra → 3. Recommendation engine + services →
4. Routes (all blueprints) → 5. Templates + CSS/JS → 6. Seed data & demo
account → 7. Tests (written + all passing) → 8. Documentation → 9. Commit
& push.

If continuing this project, the highest-leverage next steps (in priority
order) are: (1) real affiliate network integration, (2) Flask-Migrate,
(3) an admin UI for careers/roadmaps/projects instead of seed-script-only
editing, (4) a real external LLM behind `ai_adapter.py`, (5) rate limiting
on auth routes.
