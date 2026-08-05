# Rewind progress handoff (repo snapshot)

Date: 2026-07-14
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
- POST /auth/verify-email implemented: validates token, marks user verified, triggers tape claiming.
- Tape claiming implemented in TapeService: claim_tapes_for_email sets recipient_id and status to claimed for all sent tapes matching the user's email.
- Second claiming trigger implemented in send_tape: if recipient already has a verified account, tape is claimed immediately at send time.
- POST /auth/verify-email now returns {"message": "Email verified"} instead of user object, matching API design.

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
- VerifyEmailPage calls /auth/verify-email and redirects to /inbox on success
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

### Tests implemented

- Backend integration tests exist for auth, tapes, tracks, spotify search.
- Backend unit tests exist for auth_service, tape_service, track_service.
- Test setup includes DB lifecycle fixture and fake spotify/email fixtures.

## Appears unfinished or not yet implemented

### Backend/API gaps relative to roadmap docs

- No spotify OAuth/export endpoints found.
- No observability endpoints/integration found (/metrics, Sentry wiring, CI workflow details not found in app code).

### Frontend gaps relative to roadmap docs

- No spotify connect/export UI found.

### Documentation/consistency gaps

- README.md added in wip.
- Planning docs describe many future phases not yet present in code.
- Some tests/comments indicate earlier assumptions (e.g., historical note saying PATCH /ready did not exist), but route now exists.
