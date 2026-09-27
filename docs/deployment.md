# Deployment

This build has **not** been deployed to a live public URL as part of this
session — no hosting credentials or target platform were provided. This
document describes exactly what deployment requires, so it needs minimal
manual configuration when credentials are available (per the project
brief's Phase 8 instruction to never claim deployment succeeded without
verifying it).

## Minimum requirements for any deployment target

1. A WSGI server in front of Flask — **do not use `python run.py`'s
   development server in production.** Use `gunicorn`:
   ```bash
   pip install gunicorn
   gunicorn "run:app" --bind 0.0.0.0:8000 --workers 3
   ```
2. Environment variables set on the host (see `.env.example`):
   - `SECRET_KEY` — a long, random value, different from the dev default.
   - `DATABASE_URL` — for anything beyond a single-instance demo, point
     this at a managed MySQL/PostgreSQL instance rather than SQLite (SQLite
     does not handle concurrent writers well).
   - `FLASK_ENV=production`.
3. Run the seed script once against the production database if starting
   fresh: `python -m seed.seed_data` (idempotent — safe to re-run).
4. Serve `app/static/` via the WSGI server or a CDN/reverse proxy in front
   of it for better performance (not required for correctness).

## Suggested platforms (not configured in this repo)

- **Render / Railway / PythonAnywhere** — simplest path for a Flask +
  MySQL app; add a `Procfile` with `web: gunicorn run:app` if the platform
  expects one.
- **A university/college server** — since this is a B.Tech capstone,
  running behind `nginx` + `gunicorn` on a small Linux VM is a common and
  fully explainable setup for a viva demo.

## Database migration note

This build uses `db.create_all()` (called from the seed script) rather
than a migration tool like Alembic, appropriate for a project at this
stage where the schema is defined once and seeded fresh. If the schema
needs to evolve after real user data exists, introduce Flask-Migrate
before making further model changes — this is flagged as future work in
`PROJECT_STATUS.md` rather than silently deferred.

## Checklist before any real deployment

- [ ] Change `SECRET_KEY` from the dev default.
- [ ] Change the admin password from `.env.example`'s placeholder.
- [ ] Set `DATABASE_URL` to a real, backed-up database — not local SQLite.
- [ ] Confirm `SESSION_COOKIE_SECURE=True` is in effect (it is, via
      `ProductionConfig`) and that the deployment is served over HTTPS.
- [ ] Review `docs/security.md`'s "explicitly out of scope" list (rate
      limiting, email verification, password reset) and decide whether any
      are required before going live with real users.
