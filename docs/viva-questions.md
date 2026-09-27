# B.Tech Viva Question Bank

## Problem statement & motivation

**Q: What problem does this project actually solve?**
A: Students have access to more free/paid educational content than ever,
but no reliable way to decide *what to learn next, in what order, and
why*. NAVORA replaces open-ended searching with one explainable next
action, personalized to the student's stream, goals, learning style, time
and budget.

**Q: Why not just use Google or YouTube search?**
A: Search engines optimize for relevance to a *query*, not to a *person's
learning trajectory*. NAVORA tracks prerequisites, current skill level,
career goals and past feedback to sequence learning, and explains every
suggestion — something a search results page does not do.

**Q: What's your existing-system analysis?**
A: Course marketplaces (Coursera, Udemy) sell courses; aggregators
(YouTube, blogs) list content without sequencing; career sites (LinkedIn
Learning) map skills to jobs but don't build a personalized roadmap from a
student's actual current level. NAVORA's gap-fill is combining
profile-aware sequencing + explainability + a Free-First bias in one
product.

## Architecture

**Q: Why Flask instead of Django or a JS framework?**
A: Flask keeps the codebase small and fully traceable for a viva — every
route, model and template is explicit, with no framework "magic" (no
auto-generated admin, no ORM migrations hidden behind commands not shown
in the code). See `docs/architecture.md`.

**Q: Why server-rendered templates instead of a React/SPA frontend?**
A: The product brief explicitly avoids introducing a build toolchain and
client-side framework the team would need to separately defend. Jinja2
templates keep the rendering logic co-located with the Flask routes that
feed them, and the app remains fully usable without JavaScript.

**Q: Walk me through what happens when a student loads their dashboard.**
A: `dashboard.home()` (`app/routes/dashboard.py`) — resolves the student's
career from their Learning DNA, calls `get_next_move()` for the signature
card, queries `LearningProgress` for "continue learning", computes
roadmap-stage completion percentage, calls `recommend_for_user()` for the
"Recommended next" grid, sums this week's `StudySession` minutes against a
target derived from the student's declared time availability, and computes
a login-streak from distinct study-session dates — all rendered into one
template.

## Database

**Q: Why JSON columns instead of full normalization for lists like
`interests` or `skill_tags`?**
A: A deliberate simplicity trade-off explained in `docs/database.md` — these
are read far more than filtered-on, and full normalization would add
several join tables without a corresponding gain in query capability at
this scale. Noted as the first normalization step if the project grew.

**Q: How do you prevent a student from having two `LearningProgress` rows
for the same resource?**
A: A `UniqueConstraint` on `(user_id, resource_id)` in the `learning_progress`
table (see `app/models/progress.py`).

**Q: How would you migrate the schema if it needed to change after
students had real data?**
A: This build uses `db.create_all()`, appropriate for a schema defined once
and seeded fresh. Before evolving the schema post-launch, Flask-Migrate
(Alembic) would be introduced — flagged as future work rather than glossed
over.

## Recommendation engine

**Q: Is this "AI"? Are you using machine learning?**
A: No — and that's intentional. It's an explainable, rules-based weighted
scoring engine (see `docs/recommendation-engine.md`). Each of ~11 factors
(career relevance, skill-level fit, learning-style fit, etc.) contributes a
capped number of points, normalized to a 0–100 score, and every positive
factor generates a specific, traceable, human-readable reason. There is no
trained model, so there's nothing that can silently drift or hallucinate.

**Q: How does the "personalization learning loop" work without machine
learning?**
A: When a student marks a recommendation useful/not-useful, that's stored
against the resource's skill tags. Future scoring for resources sharing
those tags applies a proportional adjustment (a usefulness ratio scaled
into a bonus/penalty) — simple, auditable, and effective for the stated
goal of feeling responsive without needing a training pipeline.

**Q: What happens if a resource has no rating?**
A: `Resource.has_real_rating` returns `False`, and the UI explicitly shows
"Rating unavailable" — the scoring function gives unrated resources a
small neutral credit rather than fabricating or assuming a rating.

## Security

**Q: How are passwords stored?**
A: Hashed via Werkzeug's `generate_password_hash` (PBKDF2), never in
plaintext, never logged.

**Q: How do you prevent CSRF?**
A: Flask-WTF's `CSRFProtect` is enabled globally; every form includes a
hidden `csrf_token` field, validated server-side on every POST.

**Q: How do you stop a student from reaching the admin panel?**
A: Two decorators stacked on every admin route: `@login_required` (Flask-
Login) then `@admin_required` (checks `current_user.is_admin`, aborts 403
otherwise). Verified in `tests/test_admin.py`.

## Testing

**Q: How many tests do you have, and what do they actually verify?**
A: 31 pytest tests across 6 files, covering auth, the full onboarding
wizard, recommendation-engine scoring behavior, search/filtering, and
admin authorization boundaries. See `docs/testing.md` for the full
breakdown, including a real bug found and fixed during manual verification
(a `None`-vs-`int` comparison on a freshly created, not-yet-flushed ORM row).

## Business model & monetization

**Q: How does this make money?**
A: It doesn't, today — this is a capstone project. `docs/business-model.md`
separates *potential* revenue streams the architecture supports (affiliate
clicks are logged; sponsored content has a schema and always-visible
label) from *actual* revenue (none — explicitly, so as not to overstate
the project).

## Limitations & future scope

**Q: What are the biggest limitations of the current build?**
A: No live AI/LLM integration (by design — see `docs/future-ai.md`); no
payment processing; no email verification or password reset; SQLite-only
testing (no MySQL run performed); English-only seeded content despite
Hindi/Bengali being supported in the data model; no automated resource
freshness checking (verification is manual, via the admin panel).

**Q: If you had another semester, what would you build next?**
A: Flask-Migrate for schema evolution, an actual affiliate network
integration, Alembic-backed multi-language content, rate limiting on auth
routes, and — carefully, without breaking the explainability guarantee —
an LLM layer on top of (not replacing) the existing scoring engine for
more natural AI Study Mentor conversations.
