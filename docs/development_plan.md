Development plan · MD

# Development plan: Rewind

---

## How this plan works

Feature by feature. Backend route first, then the frontend that consumes it. Each phase ends with something you can see working — in Postman, in the browser, or both.

Every backend step is tested in Postman before moving to the frontend. Every phase has a clear done condition.

---

## Completed phases

- Phase 0: complete
- Phase 1: complete
- Phase 2: complete
- Phase 3: complete
- Phase 4: complete
- Phase 5: complete
- Phase 6: complete

---

## Phase 0: Project setup

**Goal:** dev container running, both apps reachable, database connected.

### Steps

1. Create the repo. Set up `.gitignore`, `README.md`, `CONTRIBUTING.md`.
2. Write `docker-compose.yml`: backend (FastAPI, port 8000), frontend (Vite, port 5173), database (PostgreSQL, port 5432).
3. Write `.devcontainer/devcontainer.json` pointing at the compose file. Open in VS Code via the bottom-left arrows.
4. Scaffold the backend: `uv init`, install FastAPI, SQLAlchemy, Alembic, Pydantic, Loguru, python-dotenv, pytest, httpx.
5. Create `app/main.py` with a single `GET /health` route that returns `{ "status": "ok" }`.
6. Create `app/core/config.py` using `pydantic-settings`. Load `DATABASE_URL`, `JWT_SECRET`, `ENV` from `.env`.
7. Set up Alembic. Run `alembic init`. Confirm it connects to PostgreSQL.
8. Scaffold the frontend: `npm create vite`, TypeScript template. Install Tailwind, React Query, Zustand, React Router.
9. Create a single page that calls `GET /health` and prints the response.
10. Set up pre-commit hooks for Black, Ruff, Prettier

### Done when

- Dev container opens with one click.
- `GET /health` returns 200 in Postman.
- Frontend renders the health response in the browser.
- DBeaver connects to the database.

---

## Phase 1: Auth

**Goal:** register, login, logout, and a protected route all working end to end.

### Backend

1. Create `User` SQLAlchemy model. Write and run the Alembic migration.
2. Write `UserRepository`: `create`, `get_by_email`, `get_by_id`.
3. Write `AuthService`: `register` (hash password with Argon2), `login` (verify password, return JWT), `get_current_user`.
4. Write `app/core/security.py`: `create_access_token`, `set_auth_cookie`, `clear_auth_cookie`, `get_user_from_cookie`.
5. Write auth router: `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`.
6. Add CSRF token cookie on login. Add CSRF validation middleware for state-changing requests.
7. Write unit tests for `AuthService`. Write integration tests for all 4 routes.
   **Postman checkpoints:** register a user, log in, call `/auth/me` with the cookie, log out, confirm `/auth/me` returns 401.

### Frontend

1. Build `RegisterPage`: form with email and password, calls `POST /auth/register`.
2. Build `LoginPage`: form, calls `POST /auth/login`, stores user in Zustand on success.
3. Add a protected route wrapper. Redirect to `/login` if no user in store.
4. Add `GET /auth/me` call on app load to restore session from cookie.
5. Add logout button that calls `POST /auth/logout` and clears Zustand store.

### Done when

- Register, login, logout all work in the browser.
- Refreshing the page keeps the user logged in.
- Visiting a protected route without a session redirects to login.

---

## Phase 2: Tape creation (draft)

**Goal:** a logged-in user can create a tape and see it in the database.

### Backend

1. Create `Tape` SQLAlchemy model. Write and run migration.
2. Write `TapeRepository`: `create`, `get_by_id`, `get_by_sender`.
3. Write `TapeService`: `create_tape` (sets status to `draft`), `get_tape` (ownership check).
4. Write tape router: `POST /tapes`, `GET /tapes/{tape_id}`.
5. Write unit tests for `TapeService`. Write integration tests for both routes.
   **Postman checkpoint:** create a tape, fetch it by ID, confirm 403 when fetching another user's tape.

### Frontend

1. Build `CreateTapePage`: cassette style selector, length selector (60 or 90 min), title input.
2. On submit, call `POST /tapes` and redirect to the tape builder.
3. Build basic `TapeBuilderPage` shell: shows tape title and selected style. No tracks yet.

### Done when

- User creates a tape from the UI.
- Tape appears in DBeaver with `status = draft`.
- Tape builder page loads the tape data.

---

## Phase 3: Spotify search and tracks

**Goal:** user can search for songs and add them to a tape side.

### Backend

1. Implement Spotify Client Credentials flow in `SpotifyService`: fetch and cache the app token.
2. Write `GET /spotify/search`: sanitise query, call Spotify, return tracks.
3. Create `Track` SQLAlchemy model. Write and run migration.
4. Write `TrackRepository`: `add_track`, `delete_track`, `get_side_duration`.
5. Write `TrackService`: `add_track` (enforce side time cap), `remove_track`.
6. Write track router: `POST /tapes/{tape_id}/tracks`, `DELETE /tapes/{tape_id}/tracks/{track_id}`.
7. Write unit tests for `TrackService` (especially the duration cap logic). Integration tests for all routes.
   **Postman checkpoints:** search for a track, add it to a tape, confirm duration is tracked, try to overfill a side and get 422.

### Frontend

1. Build `SpotifySearch` component: debounced input (300ms), calls `GET /spotify/search`, shows results.
2. Build `TrackList` component: shows tracks per side with duration.
3. Add time-remaining display per side, updates live as tracks are added.
4. Add remove track button.

### Done when

- User searches for a song, adds it to Side A.
- Time remaining updates in real time.
- Adding a track that would exceed the side limit shows an error.
- Track appears in DBeaver linked to the tape.

---

## Phase 4: Cassette label

**Goal:** the one-screen demo moment — song titles appear on the cassette label as tracks are added.

### Frontend only

1. Build the `Cassette` component in pure CSS. Style varies by `cassette_style` value.
2. Render the cassette label with track titles from the Zustand store.
3. Use Caveat or Special Elite (Google Font) for the label text.
4. Update the label in real time as tracks are added or removed.

### Done when

- Adding a song makes its title appear on the cassette label immediately.
- The cassette looks distinct for each style option.
- Mobile-first from day one. Tailwind responsive classes (sm:, md:) used throughout. Layout works on 375px viewport. UI is intentionally basic until Phase 10.

---

## Phase 5: Tape state transitions and sending

**Goal:** user can mark a tape ready and send it to a friend.

### Backend

1. Write `PATCH /tapes/{tape_id}/ready` in `TapeService`: validate at least one track exists, transition to `ready`.
2. Write `POST /tapes/{tape_id}/send`: validate status is `ready`, generate `public_token` (UUID), set `sent_at`, transition to `sent`.
3. Implement `EmailService` with Resend: send the invitation email with the public tape URL.
4. Write `GET /tape/public/{public_token}`: returns tape without private fields, no auth required.
5. Write unit tests for state transitions. Integration tests for send and public endpoints.
   **Postman checkpoints:** mark tape ready, send it, confirm public token exists, fetch public endpoint without auth.

### Frontend

1. Add "Mark as ready" button on the tape builder. Disabled until at least one track is added.
2. Build `SendTapeModal`: recipient email and optional message fields.
3. On send success, show the public tape URL and a copy button.
4. Build `PublicTapePage` at `/tape/:token`: renders the cassette for guests, no login required.

### Done when

- User sends a tape, recipient gets an email with a working link.
- Public tape page loads without a session.
- Tape status in DBeaver shows `sent`.
- Optional: manual first deploy here to see the app live. Full CI/CD is set up in Phase 9.

---

## Phase 6: Inbox and outbox

**Goal:** users can see tapes they sent and tapes they received.

### Backend

1. Write `GET /tapes/sent`: paginated list of outbox tapes.
2. Write `GET /tapes/received`: paginated list of inbox tapes.
3. Write `PATCH /tapes/{tape_id}/archive`: sender-only, transitions to `archived`.
4. Write integration tests for all 3 routes.
   **Postman checkpoint:** send 3 tapes, fetch outbox, confirm pagination works.

### Frontend

1. Build `OutboxPage`: list of sent tapes with recipient, date, status.
2. Build `InboxPage`: list of received tapes with sender and message.
3. Add archive button on outbox items.
4. Add navigation between inbox, outbox, and tape builder.

### Done when

- Both inbox and outbox render correctly.
- Archive removes a tape from the outbox.

---

## Phase 7: Email verification and tape claiming

**Goal:** recipients can create an account and claim their tapes.

### Backend

1. Add `email_verified` and `verification_token` fields to `User`. Write migration.
2. Send a verification email on registration (via `EmailService`).
3. Write `POST /auth/verify-email`: validate token, mark user as verified, trigger tape claiming.
4. Write the tape claiming function in `TapeService`: find all tapes by `recipient_email`, set `recipient_id` and status to `claimed`.
5. Write unit tests for the claiming logic.
   **Postman checkpoint:** register, verify email via token, confirm tapes are claimed.

### Frontend

1. Show a "verify your email" message after registration.
2. Build the email verification landing page (user clicks link from email, page calls verify endpoint).
3. Redirect to inbox after successful verification.

### Done when

- New user registers with an email that received a tape.
- After verification, the tape appears in their inbox with status `claimed`.

---

## Phase 8: Spotify playlist export (optional feature)

**Goal:** sender can export a sent tape as a Spotify playlist.

### Backend

1. Create `SpotifyToken` model. Write migration.
2. Write `GET /spotify/auth`: starts OAuth flow, redirects to Spotify.
3. Write `GET /spotify/callback`: exchanges auth code for tokens, stores in `SpotifyToken` table.
4. Write `POST /spotify/export/{tape_id}`: creates Spotify playlist, stores URL on tape.
5. Write `SpotifyTokenRepository`. Write unit tests for token refresh logic.
   **Postman checkpoint:** connect Spotify, export a tape, confirm playlist URL stored on tape.

### Frontend

1. Add "Connect Spotify" button on the tape builder (only shown after tape is sent).
2. Add "Export to Spotify" button. Calls export endpoint, shows playlist URL on success.

### Done when

- Sender connects Spotify and exports a tape.
- Playlist URL stored on the tape and displayed in the UI.

---

## Phase 9: Observability and CI/CD

**Goal:** errors are visible, tests run on every push, deploys are automatic.

### Steps

1. Add Sentry to backend (`sentry-sdk`) and frontend (`@sentry/react`). Configure DSN from `.env`.
2. Add `prometheus-fastapi-instrumentator`. Expose `/metrics` endpoint.
3. Add Prometheus and Grafana services to `docker-compose.yml`.
4. Write GitHub Actions workflow: run pytest on every push, block merge on failure.
5. Set up Vercel for frontend auto-deploy on merge to `main`.
6. Set up Digital Ocean Droplet. Configure nginx to proxy to FastAPI. Set up auto-deploy via GitHub Actions.

### Done when

- A failed test blocks a PR merge.
- A merge to `main` deploys both apps automatically.
- Sentry captures a test exception.
- Grafana shows request count for at least one endpoint.

---

## Phase 10: Polish and backlog

These are not blockers for a working app. Add when the core is solid.

- JWT refresh token rotation
- User-controlled Side A / Side B split (vs fixed 50/50)
- Spotify API app review for public use (currently limited to 25 users)
- Rate limiting in nginx
- End-to-end tests (Playwright)

---

## Standards applied throughout

These apply to every phase, not just specific ones.

**Backend**

- Routers call services. Services call repositories. No layer skips another.
- All config via `settings`, never `os.environ`.
- All logging via Loguru, never `print()`.
- All input validated with Pydantic.
- 100% coverage target on service layer. Integration tests for all critical routes. No UI component tests unless logic is complex.
  **Frontend**
- Feature-based folder structure: one folder per domain under `features/`.
- `useSuspenseQuery` for data fetching. No `isLoading` conditionals.
- Strict TypeScript. No `any`.
- Zustand for global state (auth, active tape).
  **Security**
- JWT in httpOnly cookie. Never in localStorage.
- CSRF token on all state-changing requests.
- Spotify tokens server-side only, never sent to the frontend.
- Passwords hashed with Argon2.
- Public tape URLs use UUID tokens, not sequential IDs.
  **Git**
- Always work on a branch. Merge to `main` via PR.
- One feature or fix per branch.
- Pre-commit hooks run Black, Ruff, and Prettier before every commit.
