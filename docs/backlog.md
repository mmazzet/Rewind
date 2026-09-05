# Product Backlog

Project-wide backlog of features, improvements, and fixes for Rewind.

**How to read this doc:**
- **Done** — implemented, tested, and working.
- **In Progress** — currently being worked on.
- **Backlog** — planned but not started.
- Each item lists sub-tasks so work can be tracked granularly.

---

# ✅ Done

## Recipient Experience: Clickable Inbox Cards → Tape Detail View

**Status:** Done

Recipients can now open a received tape and see its full tracklist.

- [x] Backend: add `public_token` + `spotify_playlist_url` to `ReceivedTapeListItem` schema (`backend/app/schemas/tape.py`)
- [x] Frontend: add `public_token` / `spotify_playlist_url` / `message` to `ReceivedTapeListItem` type (`frontend/src/features/inbox/types/index.ts`)
- [x] Frontend: make inbox cards clickable, link to `/tape/{public_token}` (`frontend/src/features/inbox/components/InboxPage.tsx`)
- [x] Tests: assert `public_token` is present and `spotify_playlist_url` defaults to `None` on received tapes (`backend/tests/integration/test_tapes.py`)

---

## Recipient Experience: Show Spotify Playlist Link to Recipients

**Status:** Done

Recipients see the sender's exported Spotify playlist, both on the inbox card and the public tape page.

- [x] Backend: add `spotify_playlist_url` to `PublicTapeResponse` schema (`backend/app/schemas/tape.py`)
- [x] Frontend: add `spotify_playlist_url` to `Tape` type (`frontend/src/features/tapes/types/index.ts`)
- [x] Frontend: "Listen on Spotify →" link on inbox cards (`frontend/src/features/inbox/components/InboxPage.tsx`)
- [x] Frontend: "Listen on Spotify →" button on public tape page (`frontend/src/features/tapes/components/PublicTapePage.tsx`)
- [x] **Bugfix:** persist `spotify_playlist_url` on the tape after export so recipients can see it — export previously returned the URL but never saved it to the DB
  - [x] Backend: add `set_spotify_playlist_url` repo method (`backend/app/repositories/tape_repository.py`)
  - [x] Backend: call it after creating the playlist (`backend/app/services/spotify_service.py`)
  - [x] Tests: verify URL is persisted on `GET /tapes/sent` after export (`backend/tests/integration/test_spotify.py`)
  - [x] Tests: assert repo method is called on export (`backend/tests/unit/test_spotify_service.py`)

---

# 📋 Backlog

## Recipient Experience: Sender Identity (replace "user #3")

**Status:** Not started

Recipients currently see "From: user #3" — a numeric ID. Show the sender's name or email instead.

**Problem:** The `User` model has no name field — only `id`, `email`, `password_hash`, etc.

**Recommended approach:** Option B first (use email, no migration, immediate value), then Option A as a follow-up.

- [ ] Backend: add `sender_email: str` to `ReceivedTapeListItem` schema (`backend/app/schemas/tape.py`)
- [ ] Backend: update `get_received_by_user` to join `User` and return the sender email (`backend/app/repositories/tape_repository.py`)
- [ ] Backend: update `get_received_tapes` service to pass sender info through (`backend/app/services/tape_service.py`)
- [ ] Frontend: add `sender_email` to inbox type, remove or keep `sender_id` (`frontend/src/features/inbox/types/index.ts`)
- [ ] Frontend: display `sender_email` instead of `user #${sender_id}` (`frontend/src/features/inbox/components/InboxPage.tsx`)
- [ ] Tests: verify received-tape response includes sender email
- [ ] *(Follow-up / Option A)* Add `display_name` to `User` model + migration + registration

---

## Recipient Experience: Recipient Can Export to Spotify

**Status:** Not started

If the sender hasn't created the playlist yet, the recipient can connect their own Spotify and create it.

- [ ] Backend: widen `export_tape_to_spotify` auth check to allow sender **or** recipient (`backend/app/services/spotify_service.py`)
- [ ] Backend: change playlist creation to `public: True` so it's link-accessible to free accounts (`backend/app/services/spotify_service.py`)
- [ ] Frontend: add Spotify section to public tape page (Listen / Connect+Export / Log in CTA) (`frontend/src/features/tapes/components/PublicTapePage.tsx`)
- [ ] Frontend: add "Export to Spotify" button on inbox cards when no playlist exists (`frontend/src/features/inbox/components/InboxPage.tsx`)
- [ ] Backend: support `redirect_to` param in Spotify OAuth flow so recipients return to their originating page instead of `/outbox`
- [ ] Tests: recipient can export; public playlist wording; OAuth redirect

---

## Recipient Experience: Meaningful "Claimed" Status

**Status:** Not started

Currently "claimed" just means the recipient verified their email. Make it reflect actual interaction (opened/listened).

- [ ] Backend: add `opened_at` timestamp to `Tape` model (`backend/app/models/tape.py`)
- [ ] Backend: Alembic migration for `opened_at`
- [ ] Backend: add `POST /tapes/public/{public_token}/opened` endpoint (no auth) (`backend/app/routers/tapes.py`)
- [ ] Backend: add `mark_opened` service function (`backend/app/services/tape_service.py`)
- [ ] Backend: add `opened_at` to `ReceivedTapeListItem` schema (`backend/app/schemas/tape.py`)
- [ ] Frontend: fire-and-forget `POST .../opened` when public tape page mounts (`frontend/src/features/tapes/components/PublicTapePage.tsx`)
- [ ] Frontend: "New" / "Opened" badge on inbox cards (`frontend/src/features/inbox/components/InboxPage.tsx`)
- [ ] Frontend: "Opened" indicator on sent tapes so the sender gets feedback (`frontend/src/features/outbox/components/OutboxPage.tsx`)
- [ ] Tests: opened endpoint, service, badge rendering

---

# 🔧 New / Fix Items

*(Add new backlog items below — suggestions you want tracked.)*

## Drafts: list and resume (PRIORITY)

**Status:** Not started

Tapes are saved as `draft` in the DB when created, but there's no way to see or resume them after leaving the builder — they just pile up invisibly. Users can log out and "lose" an unsaved tape (it still exists in the DB; the problem is discoverability).

Keep all drafts indefinitely. Draft can be resumed → completed → sent.

- [ ] Backend: add `get_drafts_by_user` repo method (`backend/app/repositories/tape_repository.py`)
- [ ] Backend: add `get_drafts` service function (`backend/app/services/tape_service.py`)
- [ ] Backend: add `GET /tapes/drafts` endpoint (declare before `/tapes/{tape_id}`) (`backend/app/routers/tapes.py`)
- [ ] Frontend: "My drafts" list, each clickable to `/tapes/:tapeId` to resume the builder
- [ ] Tests: drafts list endpoint + service

---

## Archived tapes should be viewable (terminal, not resumable)

**Status:** Not started

`archive_tape()` flips a `sent` tape → `archived` (backend/app/services/tape_service.py:141), but there's no `GET /tapes/archived` and no UI, so archived tapes are invisible. Archive currently acts like a black hole.

**Design decision:** Archive = permanent "hidden" state but still viewable. It is **terminal** — archived tapes are NOT resumable and NOT reversible back to `sent` (a sent tape was already emailed; re-sending makes no sense). Recipient-side stays `claimed`/`sent` as today.

- [ ] Backend: add `get_archived_by_user` repo method (`backend/app/repositories/tape_repository.py`)
- [ ] Backend: add `get_archived` service function (`backend/app/services/tape_service.py`)
- [ ] Backend: add `GET /tapes/archived` endpoint (declare before `/tapes/{tape_id}`) (`backend/app/routers/tapes.py`)
- [ ] Frontend: "Archived" list where tapes can be opened (view tape + Spotify playlist link), not resumed
- [ ] Tests: archived list endpoint + service

---

## Collaborative tapes (async + real-time follow-on)

**Status:** Not started

Let multiple users work on the same tape. Two phases:

### Phase 1 — Async (turn-based) collaboration
- [ ] **Data model:** `tape_members` table (tape_id, user_id, role: owner/editor) — tapes currently have a single `sender_id` (`backend/app/models/tape.py`)
- [ ] **Invite flow:** invite by email (reuse `email_service`), accept → becomes editor
- [ ] **Permissions:** every tape route checks `sender_id` today (`tapes.py`, `track_service.py`) — change to "is member + role" check; only owner can mark ready / send
- [ ] `Track.added_by` column so members see who added each track
- [ ] Frontend: "Invite collaborators" button, member list, "added by X" on tracks
- [ ] Locking: prevent mark-ready/send while another member is mid-edit

### Phase 2 — Real-time (educational)
Websocket-based live builder so both users see track adds immediately. FastAPI websockets + broadcast + reconnection handling. Only the builder page needs it — rest of app stays HTTP + React Query.

**Why real-time:** user's primary motivation is educational (learning websockets). Note: reconnection / missed-event handling is the bulk of the work, harder than the websockets themselves.

---

## Spotify token refresh (missing — export breaks after ~1h)

**Status:** Not started

Spotify access tokens expire after 1 hour (`expires_in`). The app stores a `refresh_token` (`backend/app/services/spotify_service.py:218`) but **never uses it** — `export_tape_to_spotify()` passes the stored `access_token` directly to `create_playlist()` (lines 243-247) with no expiry check or refresh. Result: any export after the token expires fails with a Spotify 401. User would have to redo the whole OAuth flow.

**Approach:** Option C.
- [ ] Backend: in `export_tape_to_spotify`, if `expires_at` is at/near expiry, call Spotify `/token` with `grant_type=refresh_token`, store the new access token (`backend/app/services/spotify_service.py`)
- [ ] Backend: only ask the user to reconnect if the refresh itself fails (token revoked)
- [ ] Frontend: show a "Reconnect to Spotify" prompt only when refresh fails, instead of a generic error (`frontend/src/features/outbox/...`)

---

## Show more detail in Spotify search results

**Status:** Not started

Search results currently show only title + artist. The API already returns `album`, `duration_seconds`, and `preview_url` per result (`backend/app/services/spotify_service.py:183-193`; type in `frontend/src/features/tapes/types/index.ts:34-41`), the frontend just doesn't show them.

- [ ] Frontend: show album + duration in search rows (`frontend/src/features/tapes/components/SpotifySearch.tsx`) — album disambiguates same-title songs; duration matches the new tape-builder durations
- [ ] *(optional)* preview play button using `preview_url` (`<audio>` element)
- [ ] *(optional)* raise search result count above 10 (`limit: 10` at `backend/app/services/spotify_service.py:79`)

**Note:** Spotify has no structured "version" field (remix/live/deluxe appear inline in the track name) — don't attempt extraction.

---

## Show track / side durations in the tape builder

**Status:** Not started

While building a tape the user can't easily see how much space is used. Add duration info (all data already exists in the DB as `duration_seconds`).

- [ ] Frontend: show per-track duration next to each track title (`frontend/src/features/tapes/components/TrackList.tsx`)
- [ ] Frontend: show per-side used/total time (instead of only "X:XX remaining"), e.g. "34:20 / 45:00"
- [ ] *(optional, later)* progress bar / total tape runtime — skip for now

**Note:** On mobile, screen estate is limited during search — the added-tracks list / remaining time isn't visible while searching (ties into the duplicate-selection fix, item 3).

---

## Prevent accidental duplicate track selection on mobile

**Status:** Not started

On mobile, search results sit above the added-tracks list, so users can't see what they've already added while tapping. They can accidentally add the same track multiple times.

**Note:** Backend currently allows duplicates by design (no unique constraint) — legitimate for a mixtape (same song repeated). Don't hard-block duplicates.

- [ ] **A** — Change the "Add A"/"Add B" buttons to show "Added ✓" once a track is on the tape (clicking still works to allow deliberate re-adding). (`frontend/src/features/tapes/components/SpotifySearch.tsx`)
- [ ] **C** *(later stage)* — Persist the "added" state across searches (Set of `spotify_track_id`s), so re-searching still shows previously-added tracks.
- [ ] *(later stage / separate)* Full UI review of the tape-builder page layout.

---

## Handle backend cold starts on Render free tier

**Status:** Not started

Backend container spins down after inactivity on Render free tier. The frontend (Vercel) loads instantly, but the first API call hangs while the backend wakes up (30–60s) with no user feedback.

**Possible approaches (not decided):**
- **A** — Show a loading banner/spinner when the first request is slow ("Waking up the server…"), keep free tier.
- **B** — Dedicated loading/"maintenance" splash screen shown on first load until first API call succeeds.
- **D** — Migrate backend to a provider without cold starts (Fly.io free tier / Railway) — no UX work needed.

---

## Fix navbar with hamburger menu for smaller screen and mobile view

**Status:** Done

Nav has a working hamburger menu (`frontend/src/components/Nav.tsx`) — links, logout, and email all accessible via the `md:hidden` toggle button on mobile.

### Mobile layout overflow fix (Done)

Root cause of "R cut off / can't see nav / tapes too big": the cassette was a fixed `380px` wide, forcing the builder page wider than the phone viewport and triggering pinch-zoom that persisted across SPA pages (clipping the inbox nav + heading). Also added a global overflow guard.

- [x] Cassette shell responsive: `width: min(380px, 92vw)`, `height: min(240px, 58vw)` (`frontend/src/features/tapes/components/Cassette.styles.ts`)
- [x] Global `overflow-x: hidden` on `html, body` (`frontend/src/index.css`)
- [x] Verify `npm run build` passes
