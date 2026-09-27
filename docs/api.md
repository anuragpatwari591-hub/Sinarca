# API Reference

NAVORA is primarily server-rendered, but exposes a small set of
REST-style JSON endpoints under `/api/` for programmatic access (and as
the seam a future mobile app would use — spec section 59). All endpoints
require an authenticated session (`Flask-Login`) and a valid CSRF token,
exactly like the rest of the app.

## Authentication

There is no separate token-based API auth in this build — endpoints reuse
the same session cookie as the web UI. A production mobile client would
need a token-based auth layer (e.g. Flask-JWT) added here; this is called
out as future work in `PROJECT_STATUS.md`.

## Endpoints

### `POST /api/recommendation-feedback`

Records whether a recommendation was useful (spec section 34's
personalization loop), usable from a JSON client instead of the built-in
resource-detail form.

**Body** (JSON or form-encoded):
```json
{ "resource_id": 12, "useful": "true", "reason": "too_difficult" }
```

**Response:**
```json
{ "ok": true }
```

`reason` is optional and should be one of: `too_difficult`, `too_long`,
`boring`, `wrong_topic`, `already_knew`, `wrong_style`, `not_relevant`.

### `POST /api/study-session`

Logs a study session, contributing to the weekly goal bar and streak.

**Body** (form-encoded): `minutes` (int, required), `topic` (string, optional).

**Response:** `{ "ok": true, "minutes": 45 }`

### `POST /api/notifications/<id>/read`

Marks a notification as read. Returns `{ "ok": true }` or 404 if the
notification doesn't belong to the current user.

## Non-JSON, form-based equivalents

Most write actions in NAVORA (bookmarking, marking progress, reporting a
resource, submitting recommendation feedback from the resource page,
updating a project's status, completing a roadmap stage) are implemented
as plain HTML form POSTs directly in `app/routes/resources.py`,
`app/routes/roadmap.py`, and `app/routes/projects.py` rather than through
`/api/`. This was a deliberate choice: it keeps every core interaction
working with JavaScript disabled, and keeps the CSRF story simple (a
hidden `csrf_token` field on every form, checked by `Flask-WTF`'s
`CSRFProtect`). The `/api/` blueprint exists specifically for the cases
that benefit from a JSON contract (feedback logging, study-session
logging from a future timer widget, notifications).

## CSRF

Every state-changing request (whether a classic form POST or a JSON POST
to `/api/`) is protected by Flask-WTF's `CSRFProtect`. Server-rendered
forms include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`;
a JSON API client should instead send the same token from the meta tag
rendered in `base.html` (`<meta name="csrf-token" content="...">`) as an
`X-CSRFToken` header.
