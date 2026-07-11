# Rewind progress handoff (repo snapshot)

Date: 2026-07-10
Audience: another AI assistant resuming implementation
Scope: current code + tests + docs present in repo

## Implemented

### Backend foundations

- FastAPI app wiring is in place with versioned routes under /api/v1 for auth, tapes, tracks, spotify.
- Health check exists: GET /health.
- Global error handling exists with domain exception mapping and validation error shaping.
- Async SQLAlchemy setup exists with PostgreSQL, session dependency, models, and Alembic migrations.
- Implemented models and migrations: users, tapes, tracks.

### Auth (backend)

- Implemented routes: POST /auth/register, POST /auth/login, POST /auth/logout, GET /auth/me.
- Password hashing/verification uses Argon2.
- JWT cookie auth is implemented (httpOnly access_token cookie).
- CSRF token cookie + middleware validation is implemented for authenticated state-changing requests.

### Tape domain (backend)

- Implemented routes: POST /tapes, GET /tapes/{tape_id}.
- Draft -> ready transition implemented: PATCH /tapes/{tape_id}/ready (requires at least one track).
- Send flow implemented: POST /tapes/{tape_id}/send.
- Public tape read implemented: GET /tapes/public/{public_token} (no auth).

### Track domain (backend)

- Implemented routes: POST /tapes/{tape_id}/tracks, DELETE /tapes/{tape_id}/tracks/{track_id}.
- Business rules implemented:
- ownership checks
- tape must be draft for add/remove
- side duration cap enforced (half of tape length)

### Spotify search (backend)

- Implemented route: GET /spotify/search (auth required).
- Spotify client credentials flow implemented with token caching.
- Spotify integration error handling is implemented.

### Email sending (backend)

- EmailService exists and is called during tape send.
- Uses Resend client and public tape URL from config.

### Frontend implemented

- React + TypeScript + React Query + Zustand + React Router setup is present.
- Auth UI and flow implemented:
- login page
- register page
- session restore via /auth/me on app load
- protected routes
- logout action
- Tape creation + builder flow implemented:
- create tape page
- tape builder page loads tape details
- spotify search (debounced)
- add/remove tracks on side A/B
- side remaining time display
- mark-as-ready button
- send tape flow (recipient email + optional message, success link, copy button)
- Cassette visual component exists and updates label text from tracks.
- Basic app-level and tape-builder-level error boundaries exist.

### Tests implemented

- Backend integration tests exist for auth, tapes, tracks, spotify search.
- Backend unit tests exist for auth_service, tape_service, track_service.
- Test setup includes DB lifecycle fixture and fake spotify/email fixtures.

## Appears unfinished or not yet implemented

### Backend/API gaps relative to roadmap docs

- No inbox/outbox/archive endpoints found.
- No email verification/claim flow found.
- No spotify OAuth/export endpoints found.
- No observability endpoints/integration found (/metrics, Sentry wiring, CI workflow details not found in app code).

### Frontend gaps relative to roadmap docs

- No public tape page route/component found.
- No inbox/outbox pages found.
- No spotify connect/export UI found.
- No email verification UI flow found.

### Documentation/consistency gaps

- backend/README.md exists but is empty.
- Planning docs describe many future phases not yet present in code.
- Some tests/comments indicate earlier assumptions (e.g., historical note saying PATCH /ready did not exist), but route now exists.

## Resume hints for next chat

- Treat backend phases through core tape building as mostly implemented (auth + tape create/get + tracks + mark ready + send + public read + spotify search).
- Prioritize next feature slice from current gaps:

1. Public tape frontend page.
2. Inbox/outbox backend + frontend.

- Keep tests-first for new service logic, matching existing test style and fixtures.
