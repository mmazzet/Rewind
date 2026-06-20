# Architecture: Rewind

---

## Overview

Rewind is a full-stack web app. Users build virtual cassette tapes, fill them with songs from Spotify, and send them to friends via email. The backend is a Python/FastAPI REST API. The frontend is a React/TypeScript SPA. PostgreSQL is the database. The two communicate over HTTP; the frontend never touches the database directly.

---

## Architectural principles

- **Simplicity first.** Add complexity only when there is a concrete reason. No premature abstractions.
- **Modularity.** Each layer, service, and component has one job. Dependencies flow in one direction.
- **Type safety.** Pydantic on every backend endpoint. TypeScript strict mode on the frontend. No `any`.
- **Security by default.** Auth, input validation, and secret management are not afterthoughts.
- **Ease of testing.** Business logic lives in services, not routers. Services receive dependencies via injection so they can be tested without a running server or database.

---

## System components

| Component     | Technology                           | Host                      |
| ------------- | ------------------------------------ | ------------------------- |
| Frontend      | React, TypeScript, Tailwind, Zustand | Vercel                    |
| Backend API   | Python, FastAPI, nginx               | Digital Ocean Droplet     |
| Database      | PostgreSQL                           | Digital Ocean Managed DB  |
| Email         | Resend                               | SaaS (free tier)          |
| Spotify       | Spotify Web API                      | SaaS                      |
| Observability | Sentry, Prometheus, Grafana          | Docker (local); DO (prod) |

---

## Backend layer structure

The backend follows a strict 3-layer architecture. Each layer has one job.

```
backend/
├── app/
│   ├── routers/          # HTTP layer: receives requests, returns responses
│   │   ├── auth.py
│   │   ├── tapes.py
│   │   ├── tracks.py
│   │   └── spotify.py
│   ├── services/         # Business logic: rules, state transitions, orchestration
│   │   ├── auth_service.py
│   │   ├── tape_service.py
│   │   ├── track_service.py
│   │   ├── spotify_service.py
│   │   └── email_service.py
│   ├── repositories/     # Data access: all database queries live here
│   │   ├── user_repository.py
│   │   ├── tape_repository.py
│   │   ├── track_repository.py
│   │   └── spotify_token_repository.py
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request/response schemas
│   ├── core/             # Config, database session, security utilities
│   └── main.py           # App entry point, middleware, router registration
├── alembic/              # Database migrations
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml
└── .env
```

**Rule:** routers call services. Services call repositories. Repositories call the database. No layer skips another.

---

## Frontend structure

```
frontend/
├── src/
│   ├── features/         # One folder per product feature
│   │   ├── cassette/     # Cassette builder UI
│   │   ├── auth/         # Login, registration
│   │   ├── inbox/        # Received tapes
│   │   └── outbox/       # Sent tapes
│   ├── components/       # Shared UI components
│   ├── store/            # Zustand stores
│   │   └── tapeStore.ts
│   ├── api/              # API client functions (fetch wrappers)
│   ├── types/            # Shared TypeScript types
│   └── main.tsx
├── public/
└── index.html
```

Note: the feature folder is named `cassette/` because it describes the UI. The Zustand store and all backend-facing code use `tape`.

Cassette label updates
Song titles appear on the cassette label in real time using React state only. No polling, no WebSockets. When a track is added, the Zustand store updates and the cassette component re-renders automatically.

---

## Frontend error handling

`Form errors`

- Inline messages shown next to the relevant field. Returned from the API as 422 validation errors and mapped to the form field that caused them.
  `Action failures`
- Toast notifications for non-blocking failures: adding a track, sending a tape, exporting to Spotify. Toast disappears after 4 seconds. User can still interact with the app.
  `Navigation failures`
- Full error page for 404 (tape not found) and 403 (not authorised). Each has a message and a back button.
  `Session expiry`
- Axios interceptor catches every 401 response globally. On 401, the Zustand auth store is cleared and the user is redirected to /login. Axios version 1.5.0 or higher required (security).
  `React Query retry policy`
- Retries only on network errors or 5xx responses. Never retries on 4xx. Maximum 2 retries.

retry: (failureCount, error) => {
if (error.status < 500) return false
return failureCount < 2
}

`Error boundaries`

- Two levels. A top-level boundary wraps the entire app and shows a generic "something went wrong" page with a reload button. A second boundary wraps the cassette builder specifically, so a crash there doesn't take down the rest of the app.

---

## Authentication

JWT tokens stored in httpOnly cookies. The cookie is set by the backend on login and cleared on logout. The frontend never reads the token directly.

**Flow:**

1. User submits credentials to `POST /api/v1/auth/login`
2. Backend validates, returns a JWT in a `Set-Cookie` header (httpOnly, Secure, SameSite=Lax)
3. Every subsequent request sends the cookie automatically
4. Backend middleware validates the token on protected routes

**Token:** single token, longer expiry (7 days). Refresh token rotation is on the backlog.

---

## Spotify integration

Two separate flows.

**Track search (no user login required)**

- Backend holds a Client Credentials token (app-level)
- Frontend sends a search query to the Rewind API
- Backend calls Spotify, returns results
- The Spotify token never leaves the server

**Playlist export (optional, sender only)**

- Sender clicks "Export to Spotify"
- Backend redirects to Spotify OAuth consent screen
- Spotify returns an auth code to a callback endpoint
- Backend exchanges the code for access + refresh tokens
- Tokens stored in the `SpotifyToken` table, linked to the user
- Backend creates the playlist on Spotify using the stored token
  `Testing`
  SpotifyService takes a SpotifyClient in its constructor. Production wires up the real SpotifyClient (handles token caching and Spotify HTTP calls). Tests swap in a FakeSpotifyClient that returns canned data, defined in conftest.py. This keeps tests independent of the real Spotify API without any mock-mode flag in business logic

---

## Spotify token storage

Spotify OAuth tokens live in a dedicated `SpotifyToken` table, not on the `User` model. One row per user.

```
SpotifyToken
├── id
├── user_id (FK: User, unique)
├── access_token
├── refresh_token
├── expires_at
└── created_at
```

---

## Email delivery

Resend handles transactional email (free tier). The backend calls the Resend API through an abstraction layer: `EmailService` defines the interface, and the Resend-specific implementation lives in one file behind it. Switching providers means rewriting that one file, nothing else.

The email is sent after a tape transitions to `sent`. It contains a public tape URL with a random token (not a sequential ID).

---

## Public tape URLs

Format: `/tape/{public_token}`

The `public_token` is a UUID generated at send time. Anyone with the link can view the tape without an account. Recipients can create an account to claim the tape.

---

## Tape state machine

```
draft → ready → sent → claimed
                  ↓
               archived
```

- `draft`: being built
- `ready`: all tracks added, ready to send
- `sent`: email delivered, public URL active
- `claimed`: recipient created an account and saved the tape
- `archived`: sender removed it from their outbox

State transitions are enforced in the service layer, not the router.

---

## Logging

Loguru handles all backend logging. It replaces the standard `logging` module.

Every log entry includes: timestamp, level, module, and a message. Structured JSON output in production so logs are readable by external tools.

```python
from loguru import logger

logger.info("Tape sent", tape_id=tape.id, recipient=tape.recipient_email)
logger.error("Spotify token refresh failed", user_id=user.id)
```

Sentry captures exceptions automatically. Loguru and Sentry work alongside each other: Loguru for structured logs, Sentry for error alerts.

---

## Tooling and code quality

**Package management:** `uv`. Faster than pip and poetry, with a lockfile (`uv.lock`) for reproducible installs.

**Formatting and linting:**

| Tool     | Language         | Job        |
| -------- | ---------------- | ---------- |
| Black    | Python           | Formatting |
| Ruff     | Python           | Linting    |
| Prettier | TypeScript/React | Formatting |

**Pre-commit hooks** run Black, Ruff, and Prettier automatically before every commit. A commit with formatting errors or lint violations is rejected until fixed.

Setup:

```bash
pre-commit install   # run once after cloning
```

After that, every `git commit` triggers the checks automatically.

**CI:** GitHub Actions runs the full test suite on every push. A failing test blocks the merge.

---

## Local development environment

All components run in Docker via a single `docker-compose.yml`.

```
docker-compose.yml
├── backend       (FastAPI, port 8000)
├── frontend      (Vite dev server, port 5173)
├── db            (PostgreSQL, port 5432)
├── prometheus    (port 9090)
└── grafana       (port 3000)
```

A `.devcontainer/` config wraps this for VS Code Dev Containers.

---

## Observability

| Tool       | Purpose                                               |
| ---------- | ----------------------------------------------------- |
| Sentry     | Error tracking, frontend and backend                  |
| Prometheus | Metrics scraping (request count, latency, error rate) |
| Grafana    | Dashboard for Prometheus metrics                      |

FastAPI is instrumented with `prometheus-fastapi-instrumentator`. Prometheus scrapes the `/metrics` endpoint. Grafana connects to Prometheus as a data source.

Set up from day one. Errors and slow endpoints are visible immediately.

---

## Deployment

```
Vercel (frontend)
    ↓ HTTPS
Digital Ocean Droplet (nginx + FastAPI backend)
    ↓ internal network
Digital Ocean Managed PostgreSQL
```

GitHub Actions runs tests on every push. Vercel and DO deploy automatically on merge to `main`.

---

## Security summary

- Passwords hashed with Argon2 (`argon2-cffi`)
- JWT in httpOnly cookies, never in localStorage
- Spotify tokens stored server-side only
- Public tape URLs use random tokens, not sequential IDs
- All secrets in environment variables
- Input validated with Pydantic on every endpoint
- `.env.example` in repo, `.env` in `.gitignore`

---

## Open decisions (backlog)

- JWT refresh token rotation (currently: single token, 7-day expiry)
- Side A / Side B split: fixed 50/50 or user-controlled
- Spotify API approval for public use (dev mode supports 25 users)

## Migration strategy

These rules apply whenever the schema changes.

**Additive changes are safest.** Adding a new column, table, or optional field leaves existing rows unaffected.

**Never make a column required in a migration without backfilling it first.** The safe sequence is:

1. Add the column as nullable.
2. Run a backfill migration to populate existing rows with a sensible default.
3. Then make the column required.
   **One change per migration.** Keep Alembic migrations small and focused. A migration that does 3 things is harder to roll back and harder to debug.

**Never edit a migration that has already run in production.** Always add a new migration. Editing a past migration breaks Alembic's version history.

**Validation rules live in code, not the database.** Password requirements, tape length limits, and similar constraints are enforced in the service layer. Changing them does not require a migration and does not affect existing rows.

**Test migrations on a copy of production data before running them live.** A migration that works on an empty database can fail on real data.
