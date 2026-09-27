# Testing

## Automated tests (pytest)

```bash
python -m pytest tests/ -v
```

31 tests, all passing, covering:

| File | Coverage |
|---|---|
| `tests/test_auth.py` | Registration success + validation errors (short password, duplicate email), login success/failure, logout requiring auth, that self-registration never creates an admin. |
| `tests/test_onboarding.py` | The full 7-step wizard end-to-end, that Learning DNA is correctly persisted, that the dashboard redirects to onboarding when incomplete and is reachable once complete. |
| `tests/test_recommendation.py` | Free-vs-paid scoring under a "completely free" budget, that career relevance produces a matching explanation string, that skill-level fit prefers matching difficulty, that `recommend_for_user` returns a properly ranked and exclusion-respecting list, and that every recommendation carries at least one reason. |
| `tests/test_search.py` | Default search results, free-only filter, difficulty filter, text query, empty-results state, "Rating unavailable" rendering, and 404 on a missing resource. |
| `tests/test_admin.py` | Admin routes require login; a logged-in student gets 403 on every admin route; an admin can create/delete a resource and toggle a user's active status; a student cannot delete a resource. |
| `tests/test_skill_gap.py` | Missing-skill detection and ordering, and 100% readiness when every required skill is present. |

Fixtures (`tests/conftest.py`) build a fresh in-memory SQLite database per
test via `config.TestingConfig`, seeded with a minimal but realistic
dataset (one stream, a handful of skills with a prerequisite chain, two
resources — one free/beginner, one paid/advanced — a roadmap, a career, a
project, and an admin account).

## Manual verification performed during development

Beyond the automated suite, the following were exercised directly against
a running instance with the full seed dataset (`python -m seed.seed_data`)
using a scripted browser-equivalent client (Flask's test client driving
real HTTP requests, cookies, and CSRF tokens end-to-end) before this
feature was considered done:

- **Full registration → onboarding → dashboard flow** for a brand-new
  account, confirming the dashboard's "Your Next Move" card, skill
  progress, and weekly goal all render without error on a fresh profile.
- **Demo account login** (`/demo`) → dashboard → roadmap detail → resource
  detail → bookmark → progress update → feedback submission → skill gap →
  AI mentor (all 7 modes) → semester planner — the entire student-facing
  loop, back to back.
- **Resource lifecycle**: admin creates a resource → it appears in search
  → a student views/bookmarks/progresses/reports it → admin sees the
  report → admin edits → admin deletes.
- **Roadmap lifecycle**: start a roadmap → complete a stage → dashboard's
  roadmap-progress bar updates.
- **Project lifecycle**: mark a project planned → in progress → completed
  with a repo URL.
- **Authorization boundaries**: an unauthenticated request to `/admin/` is
  redirected to login; an authenticated *student* request to any `/admin/*`
  route returns 403 (not a silent redirect that could leak the route's
  existence differently); a request to a nonexistent resource ID returns a
  branded 404 page, not a stack trace.
- **CSRF**: a POST without a token is rejected with 400 in a non-testing
  config, confirming the protection is live outside of tests (where it's
  deliberately disabled for focused unit testing).

A bug was found and fixed during this process: `LearningProgress.progress_pct`
and `UserRoadmapProgress.current_stage_order` could be `None` on a
newly-constructed (not-yet-flushed) row, causing a `TypeError` when
`max()`'d against an integer. Both call sites now guard with `or 0` / `or 1`
— see the relevant commit for the fix, and `tests` for the regression
coverage via the onboarding/progress-update flows.

## What was NOT verified

- Cross-browser/visual testing (only server responses and rendered HTML
  were checked programmatically — no screenshot-based visual regression).
- Load/performance testing under concurrent users.
- MySQL-specific behavior (developed and tested against SQLite only; the
  ORM layer is database-agnostic, but a real MySQL run before production
  deployment is recommended).

These are named explicitly rather than silently assumed to work.
