# Database Design

Relational schema via SQLAlchemy, SQLite by default (`instance/navora.db`),
MySQL-ready by changing `DATABASE_URL` (see README).

## Entity groups

### Identity & profile
- **users** — id, name, email (unique), password_hash, role (student/admin),
  is_active_account, onboarding_complete, created_at.
- **education_profiles** (1:1 with users) — stream_id (FK), degree,
  specialization, college, year, semester.
- **learning_dna** (1:1 with users) — interests (JSON list), career_goal,
  learning_style (JSON list), time_availability, language,
  budget_preference, free_first_mode. This is the "Learning DNA" from
  onboarding (spec section 7).

### Taxonomy
- **streams** — name, slug, category (technology/commerce/management/…).
- **skills** — name, slug, category, prerequisite_skill_id (self-referential FK,
  used for skill-gap ordering and the recommendation engine's prerequisite check).
- **user_skills** — user_id, skill_id, level (beginner/intermediate/advanced),
  self_rated. Unique on (user_id, skill_id).
- **careers** — title, slug, description, required_skills (JSON list of skill
  slugs), degree_backgrounds (JSON list of stream slugs),
  portfolio_requirements, interview_prep_notes, roadmap_id (FK).

### Content
- **resources** — title, provider, url, category, topic, skill_tags (JSON),
  difficulty, duration_minutes, language, is_free, price_inr, rating
  (nullable — **null means "Rating unavailable", never fabricated**),
  rating_count, rating_source, description, prerequisites, resource_type,
  format_tags (JSON), last_verified_at, status (active/broken/under_review/removed),
  verification_notes, is_sponsored, affiliate_url.
- **reports** — resource_id, user_id, report_type, details, status.
  Student-submitted quality reports (spec section 29).
- **roadmaps** — title, slug, description.
- **roadmap_stages** — roadmap_id, order, title, description, estimated_hours,
  milestone_project_id (FK to projects).
- **roadmap_resources** — stage_id, resource_id, order (join table).
- **user_roadmap_progress** — user_id, roadmap_id, current_stage_order,
  completed_stage_orders (JSON). Unique on (user_id, roadmap_id).
- **projects** — title, difficulty, description, estimated_hours,
  required_skills (JSON), technologies (JSON), learning_outcomes (JSON),
  github_checklist (JSON), portfolio_description.
- **user_projects** — user_id, project_id, status, started_at, completed_at,
  repo_url. Unique on (user_id, project_id).

### Learning activity
- **learning_progress** — user_id, resource_id, status, progress_pct,
  time_spent_minutes, started_at, completed_at. Unique on (user_id, resource_id).
- **study_sessions** — user_id, date, minutes, topic. Powers the weekly-goal
  bar and the learning streak.
- **bookmarks** — user_id, target_type (resource/project/roadmap/career),
  target_id, folder. Unique on (user_id, target_type, target_id).
- **semester_plans** — user_id, semester, subjects (JSON), weak_subjects
  (JSON), exam_date, target_hours_per_week.

### Personalization loop
- **recommendations** — user_id, resource_id, score, reasons (JSON), created_at.
  A lightweight log of what was shown, so feedback can be tied back to a
  specific ranked recommendation.
- **recommendation_feedback** — recommendation_id (unique), useful (bool),
  reason (too_difficult/too_long/boring/wrong_topic/already_knew/wrong_style/not_relevant).
  This is what `app/recommendation/engine.py` reads back in to adjust future
  scores for resources sharing skill tags (spec section 34).

### Monetization (architecture only — see docs/business-model.md)
- **affiliate_clicks** — resource_id, user_id, clicked_at, was_affiliate.
  Every outbound resource click is logged here, whether or not an affiliate
  URL is actually configured.
- **sponsored_content** — title, sponsor_name, description, url, category,
  is_active, starts_at, ends_at. Empty by default in this build.

### Admin & misc
- **notifications** — user_id, message, category, is_read.
- **admin_audit_logs** — admin_id, action, target, created_at. Every
  resource save/delete and report resolution is logged here.
- **chat_messages** — user_id, role (user/assistant), mode, content. History
  for the AI Study Mentor.

## Why JSON columns instead of more join tables

Several many-valued attributes (interests, learning styles, skill tags,
required skills, checklists) are stored as JSON text columns rather than
fully normalized join tables. This is a deliberate simplicity trade-off for
a system of this size: these lists are read far more often than queried
against (`WHERE skill_tags CONTAINS X` is only used in a couple of chatbot
lookups, via `LIKE`), and full normalization would add five more join
tables without changing anything a viva examiner would consider a design
strength. If NAVORA grew past this scope, `resource_skill_tags` and
`career_required_skills` join tables would be the first normalization step
(noted in `PROJECT_STATUS.md`'s future-work section).

## Referential integrity

Foreign keys are declared throughout (e.g. `education_profiles.user_id →
users.id`, `roadmap_resources.resource_id → resources.id`). SQLite enforces
foreign keys only when `PRAGMA foreign_keys=ON` is set per-connection,
which Flask-SQLAlchemy does not enable by default — acceptable for this
build's scope, and irrelevant once deployed against MySQL (which enforces
FKs by default with InnoDB).

## Indexes

`users.email` is indexed (and unique) for fast login lookups. Slug columns
on `streams`, `skills`, `careers`, `roadmaps` are unique, which SQLAlchemy
backs with an index automatically — used for every human-readable URL in
the app (e.g. `/careers/cybersecurity-analyst`).
