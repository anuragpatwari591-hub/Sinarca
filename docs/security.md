# Security

## Authentication

- Passwords are hashed with Werkzeug's `generate_password_hash` (PBKDF2 by
  default) — never stored or logged in plaintext.
- Session management uses Flask-Login with a signed, `HttpOnly`,
  `SameSite=Lax` session cookie (`config.py`). `SESSION_COOKIE_SECURE` is
  enabled in `ProductionConfig` so the cookie is only sent over HTTPS in
  production.
- `User.is_active` (used internally by Flask-Login) is backed by an
  explicit `is_active_account` column, so an admin-deactivated account is
  immediately logged out on its next request.

## Authorization

- `@login_required` (Flask-Login) gates every route that touches
  per-student data.
- `@admin_required` (`app/utils/decorators.py`) aborts with 403 for any
  non-admin, checked *after* `@login_required`, so an unauthenticated
  request is redirected to login (not leaked as "403 exists at this URL").
  See `tests/test_admin.py` for verification of both boundaries.
- `@onboarding_required` redirects a logged-in student with an incomplete
  Learning DNA back into the onboarding wizard, so no page can render a
  half-built profile inconsistently.

## CSRF protection

Flask-WTF's `CSRFProtect` is initialized globally (`app/extensions.py`,
wired in `create_app`). Every POST form in every template includes:

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

`tests/` confirms this is enforced: any test issuing a POST without a
valid token (in a non-testing config) receives a 400. `TestingConfig`
disables CSRF only inside the test suite itself, so test code doesn't need
to scrape tokens for internal application-logic tests — the token-based
flow is separately exercised in `tests/test_auth.py`,
`tests/test_admin.py`, and `tests/test_onboarding.py` against a live
config where CSRF is enabled.

## Input validation

- Registration validates: name length, an RFC-ish email regex, minimum
  password length (8 chars), password confirmation match, and email
  uniqueness — all server-side (`app/routes/auth.py`), never trusting
  client-side validation alone.
- All database writes use SQLAlchemy's ORM with parameterized queries —
  no raw string-interpolated SQL exists anywhere in the codebase, which is
  the primary SQL-injection defense.
- Jinja2 auto-escapes all template output by default, which is the primary
  XSS defense; no template uses the `|safe` filter on user-supplied content.

## What's explicitly out of scope for this build

- **Rate limiting** — not implemented. A production deployment should add
  Flask-Limiter on `/auth/login` and `/auth/register` to slow down
  credential stuffing / registration spam.
- **Email verification** — accounts are usable immediately after
  registration; a production build would add a verification step.
- **Password reset flow** — not implemented; would require email delivery
  infrastructure, which is out of scope for this environment.
- **Token-based API auth** — the `/api/` endpoints reuse the web session;
  a real mobile client would need OAuth2/JWT (see `docs/api.md`).

These are named explicitly (per the project's "no fabrication" principle)
rather than silently absent — see `PROJECT_STATUS.md`.

## Secrets management

`SECRET_KEY`, `DATABASE_URL`, `AI_PROVIDER_API_KEY` and the seed script's
`ADMIN_EMAIL`/`ADMIN_PASSWORD` are all read from environment variables via
`.env` (loaded through `python-dotenv`/the shell environment), never
hard-coded. `.env` itself, `instance/`, and `*.db` are all in `.gitignore`
— no secret or local database has been committed to this repository.
