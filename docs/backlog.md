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
