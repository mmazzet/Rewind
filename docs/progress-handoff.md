# Rewind progress handoff (repo snapshot)

Date: 2026-09-02
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
- Email verification flow implemented: verification token generated on register, stored on User, sent via EmailService.
- POST /auth/verify-email implemented: validates token, marks user verified, triggers tape claiming, sets access_token + csrf_token cookies, returns UserResponse (auto-login on verify).
- Tape claiming implemented in TapeService: claim_tapes_for_email sets recipient_id and status to claimed for all sent tapes matching the user's email.
- Second claiming trigger implemented in send_tape: if recipient already has a verified account, tape is claimed immediately at send time.

### Tape domain (backend)

- Implemented routes: POST /tapes, GET /tapes/{tape_id}.
- Draft -> ready transition implemented: PATCH /tapes/{tape_id}/ready (requires at least one track).
- Send flow implemented: POST /tapes/{tape_id}/send.
- Public tape read implemented: GET /tapes/public/{public_token} (no auth).

### Inbox/outbox/archive (backend)

- Implemented routes: GET /tapes/sent, GET /tapes/received, PATCH /tapes/{tape_id}/archive.
- Repository methods added: get_sent_by_user, get_received_by_user.
- New exception: TapeNotSentError, registered in ERROR_MAP.
- New schemas: SentTapeListItem, ReceivedTapeListItem.
- Route order corrected in tapes.py: static paths before dynamic paths.
- Unit tests and integration tests for Phase 6 complete. One bug fixed: get_sent_by_user was including archived tapes in outbox results. Fixed by removing TapeStatus.archived from the status.in_() filter.

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
- Resend sender address updated to use verified domain em.myname.me. RESEND_FROM_EMAIL added to config and .env.example. Emails now send to any recipient.

### Spotify export (backend)

- SpotifyToken model and migration implemented.
- Implemented routes: GET /spotify/auth, GET /spotify/callback, POST /spotify/export/{tape_id}.
- OAuth flow (auth -> callback -> token storage) tested end to end.
- Playlist creation and track addition confirmed working via POST /spotify/export/{tape_id}.
- Bug fixed: create_playlist was posting tracks to POST /playlists/{id}/tracks, which Spotify
  removed in its 2026 API migration (returns 403 with no detail). Fixed by switching to
  POST /playlists/{id}/items, same request body and headers.

### Frontend implemented

- React + TypeScript + React Query + Zustand + React Router setup is present.
- Auth UI and flow implemented:
- login page
- register page
- session restore via /auth/me on app load
- protected routes
- logout action
- Email verification flow implemented:
- register page now shows a post-signup confirmation message instead of redirecting immediately
- verify-email route is wired at /verify-email
- VerifyEmailPage calls /auth/verify-email, stores returned user in auth state via setUser(), then redirects to /inbox on success
- Tape creation + builder flow implemented:
- create tape page
- tape builder page loads tape details
- spotify search (debounced)
- add/remove tracks on side A/B
- side remaining time display
- mark-as-ready button
- public tape page route/component
- send tape flow (recipient email + optional message, success link, copy button)
- Cassette visual component exists and updates label text from tracks.
- Basic app-level and tape-builder-level error boundaries exist.
- InboxPage at /inbox: lists received tapes, empty state, protected route.
- OutboxPage at /outbox: lists sent tapes, archive button, optimistic invalidation via React Query.
- PublicTapePage wrapped in ErrorBoundary — 404 on invalid token now shows error fallback.
- Both API layers use plain array responses (backend does not return paginated envelope).
- Nav component at src/components/Nav.tsx: links to inbox, outbox, new tape, logout.
- ProtectedLayout in App.tsx: wraps all protected routes, renders Nav above page content.
- / redirects to /inbox. Public tape page has no nav.
- Spotify connect/export UI implemented: Connect Spotify button in outbox, SpotifyCallbackPage handles OAuth redirect, Export to Spotify button creates playlist and shows URL.

### Deployment

- Frontend deployed on Vercel. Backend on Render. Database on Neon.
- Production is a cross-site setup (Vercel frontend → Render backend). With SameSite=lax cookies the browser does not send cookies cross-site on XHR/fetch, so cookie-based auth does not persist across page loads without a same-origin proxy.
- Local dev avoids this because the Vite dev server proxies /api to the backend on the same origin.
- Production fix: Vercel project-level routing rule required to proxy /api/* → Render backend (same-origin). Routing rules are managed via the Vercel Dashboard or CLI (`vercel routes`), not in the repo, so the backend URL stays out of Git. The SPA rewrite in `vercel.json` should only contain the client-side catch-all.
- `VITE_API_URL` env var in Vercel must be removed/empty so the frontend calls /api/v1 same-origin; the proxy then forwards to Render.

### Tests implemented

- Backend integration tests exist for auth, tapes, tracks, spotify search.
- Backend unit tests exist for auth_service, tape_service, track_service.
- Test setup includes DB lifecycle fixture and fake spotify/email fixtures.
- Spotify unit tests complete: test_spotify_service.py covers search_tracks, handle_oauth_callback, export_tape_to_spotify (happy path + all error cases).
- Spotify integration tests complete: test_spotify.py covers search, auth redirect, callback, and export routes.

### Test suite improvements

Added fast argon2 hasher fixture in integration conftest — cut suite time from 62s to 40s
Removed duplicate engine/sessionmaker from test_auth.py and test_tapes.py — both now import TestSessionLocal from conftest
Created tests/integration/helpers.py — single home for register_and_login, create_tape, create_track, mark_tape_ready, helper_send_tape
Created tests/unit/conftest.py — shared mock_db fixture, removed from individual unit test files

## Appears unfinished or not yet implemented

### Backend/API gaps relative to roadmap docs

- No observability endpoints/integration found (/metrics, Sentry wiring, CI workflow details not found in app code).

### Frontend gaps relative to roadmap docs

- nothing

### Documentation/consistency gaps

- README.md added in wip.
- Planning docs describe many future phases not yet present in code.
- Some tests/comments indicate earlier assumptions (e.g., historical note saying PATCH /ready did not exist), but route now exists.
