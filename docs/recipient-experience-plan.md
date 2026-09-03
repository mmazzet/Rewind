# Plan: Improve Recipient Tape Experience

## Overview

The recipient experience currently has 5 gaps. Here's a concrete implementation plan for each, ordered by dependency and priority.

---

## Improvement 1: Clickable Inbox Cards → Tape Detail View

**Goal:** Recipients can open a received tape and see its full tracklist.

### Backend
- **`backend/app/schemas/tape.py`** — Add `public_token` to `ReceivedTapeListItem` (it's already on the model but not serialized in the list response). Also add `spotify_playlist_url`.
  ```python
  class ReceivedTapeListItem(BaseModel):
      id: int
      title: str
      sender_id: int
      message: str | None
      status: TapeStatus
      sent_at: datetime
      public_token: str | None = None
      spotify_playlist_url: str | None = None
  ```

### Frontend
- **`frontend/src/features/inbox/types/index.ts`** — Add `public_token` and `spotify_playlist_url` to `ReceivedTapeListItem`:
  ```typescript
  export interface ReceivedTapeListItem {
    id: number;
    title: string;
    sender_id: number;
    message: string | null;
    status: "sent" | "claimed";
    sent_at: string;
    public_token: string | null;
    spotify_playlist_url: string | null;
  }
  ```

- **`frontend/src/features/inbox/components/InboxPage.tsx`** — Make each `<li>` a `<Link to={/tape/${tape.public_token}}>` when `public_token` is present. Show the message preview if available. Style as clickable cards with hover state.

---

## Improvement 2: Show Spotify Playlist Link to Recipients

**Goal:** If the sender already exported to Spotify, the recipient can see and open the playlist link.

### Backend
- **`backend/app/schemas/tape.py`** — Add `spotify_playlist_url` to `PublicTapeResponse`:
  ```python
  class PublicTapeResponse(BaseModel):
      # ... existing fields ...
      spotify_playlist_url: str | None = None
  ```

### Frontend
- **`frontend/src/features/tapes/types/index.ts`** — Add `spotify_playlist_url` to the `Tape` interface:
  ```typescript
  export interface Tape {
    // ... existing fields ...
    spotify_playlist_url: string | null;
  }
  ```

- **`frontend/src/features/tapes/components/PublicTapePage.tsx`** — After the tracklist, add a "Listen on Spotify" button/link when `tape.spotify_playlist_url` is present. Also show a "Create an account to make your own" CTA.

- **`frontend/src/features/inbox/components/InboxPage.tsx`** — On each card, if `spotify_playlist_url` exists, show a small green "Spotify" link that opens in a new tab. This gives recipients quick access without needing to open the full tape view.

---

## Improvement 3: Sender Identity (Replace "user #3")

**Goal:** Show the sender's name or email instead of a numeric ID.

### Problem
The `User` model has no `name` field — only `id`, `email`, `password_hash`, etc.

### Two options

**Option A (Recommended): Add `display_name` to User model**
- Add a `display_name: Mapped[str | None]` column to `backend/app/models/user.py`
- Create an Alembic migration
- Update registration to accept an optional `display_name`
- Backend: Join `User` in `get_received_by_user` query to include `sender_email` (or `sender_name`) in `ReceivedTapeListItem`
- Frontend: Display the resolved name/email

**Option B (Quick): Use email as display**
- Add `sender_email: str` to `ReceivedTapeListItem` schema
- Join `User` in the repository query to include the sender's email
- Show "From: user@email.com" instead of "From: user #3"
- No model change or migration needed, but exposes email

**Recommended: Option B first** (no migration, immediate value), then Option A as a follow-up.

### Changes for Option B

#### Backend
- **`backend/app/repositories/tape_repository.py`** — Update `get_received_by_user` to join `User` and return `sender_email`:
  ```python
  async def get_received_by_user(self, recipient_id: int) -> list[dict]:
      result = await self.db.execute(
          select(Tape, User.email.label("sender_email"))
          .join(User, Tape.sender_id == User.id)
          .where(
              Tape.recipient_id == recipient_id,
              Tape.status.in_([TapeStatus.sent, TapeStatus.claimed]),
          )
          .order_by(Tape.sent_at.desc())
      )
      # Return list of dicts or tuples
  ```

- **`backend/app/services/tape_service.py`** — Update `get_received_tapes` to pass through sender info.

- **`backend/app/schemas/tape.py`** — Add `sender_email: str` to `ReceivedTapeListItem` (replacing or alongside `sender_id`).

#### Frontend
- **`frontend/src/features/inbox/types/index.ts`** — Add `sender_email: string`, remove or keep `sender_id`.
- **`frontend/src/features/inbox/components/InboxPage.tsx`** — Display `tape.sender_email` instead of `user #${tape.sender_id}`.

---

## Improvement 4: Recipient Can Export to Spotify

**Goal:** If the sender hasn't created the playlist yet, the recipient can connect their own Spotify and create it.

### Backend
- **`backend/app/services/spotify_service.py`** — Modify `export_tape_to_spotify` to allow either sender OR recipient to export:
  ```python
  async def export_tape_to_spotify(self, tape_id, user_id, token_repo, tape_repo):
      tape = await tape_repo.get_by_id(tape_id)
      if not tape:
          raise TapeNotFoundError("Tape not found")
      # Allow sender OR recipient (must be sent/claimed)
      if tape.sender_id != user_id and tape.recipient_id != user_id:
          raise NotAuthorisedError("Not authorised")
      # ... rest unchanged
  ```

  Alternatively, keep the sender-only check and add a new `export_tape_to_spotify_as_recipient` method. But the simpler approach is to widen the auth check.

- **`backend/app/services/spotify_service.py`** — In `create_playlist`, change `"public": False` to `"public": True` so the playlist is accessible to anyone with the link (relevant for free accounts too):
  ```python
  json={"name": title, "public": True}
  ```

### Frontend
- **`frontend/src/features/tapes/components/PublicTapePage.tsx`** — Add a Spotify section at the bottom:
  - If `tape.spotify_playlist_url` exists → show "Listen on Spotify" button
  - Else if user is authenticated → show "Connect Spotify" + "Create Playlist" buttons
  - Else → show "Log in to create this playlist on Spotify"

- **`frontend/src/features/inbox/components/InboxPage.tsx`** — Add a small "Export to Spotify" button on each card (when no playlist exists yet and tape is sent/claimed).

- **`frontend/src/features/tapes/api/spotifyApi.ts`** — Already has `exportToSpotify(tapeId)`, no backend changes needed for the API call itself.

### Spotify OAuth redirect consideration
- The current `GET /spotify/auth` redirects to `/outbox?spotify=connected`. If the recipient initiates OAuth from the inbox or public tape page, the redirect should go back to where they were. This requires passing a `redirect_to` param through the OAuth flow, or using the `state` parameter.
- **Simple approach:** Add a `redirect_to` query param to `/spotify/auth`, pass it through to the callback, and redirect to that path on success. E.g., `/api/v1/spotify/auth?redirect_to=/inbox` → callback → `/inbox?spotify=connected`.

---

## Improvement 5: Meaningful "Claimed" Status

**Goal:** "Claimed" means the recipient actually interacted with the tape (opened it, listened), not just that they verified their email.

### Backend
- **`backend/app/models/tape.py`** — Add an `opened_at` timestamp field:
  ```python
  opened_at: Mapped[datetime | None] = mapped_column(
      DateTime(timezone=True), nullable=True
  )
  ```

- **Alembic migration** — `alembic revision --autogenerate -m "add opened_at to tapes"`

- **`backend/app/routers/tapes.py`** — Add a new endpoint `POST /tapes/public/{public_token}/opened` (no auth required) that sets `opened_at` on first call:
  ```python
  @router.post("/public/{public_token}/opened")
  async def mark_tape_opened(public_token: str, db: AsyncSession = Depends(get_db)):
      tape = await tape_service.mark_opened(db, public_token)
      return {"status": "ok"}
  ```

- **`backend/app/services/tape_service.py`** — Add `mark_opened` function that sets `opened_at` if not already set.

- **`backend/app/schemas/tape.py`** — Add `opened_at` to `ReceivedTapeListItem`.

### Frontend
- **`frontend/src/features/tapes/components/PublicTapePage.tsx`** — Call `POST /tapes/public/{token}/opened` on mount (fire-and-forget).
- **`frontend/src/features/inbox/components/InboxPage.tsx`** — Optionally show a "New" badge if `opened_at` is null, or "Opened" if set.
- **`frontend/src/features/outbox/components/OutboxPage.tsx`** — Show "Opened" indicator on sent tapes where `opened_at` is set, giving the sender feedback.

### State machine update
The state machine becomes: `draft → ready → sent → claimed → archived`

"Claimed" now more accurately means: "the recipient has an account AND has opened the tape." The automatic claim-on-verification still happens, but `opened_at` gives a secondary signal of actual engagement.

---

## Implementation Order

| Phase | Items | Effort |
|-------|-------|--------|
| **1** | #1 (clickable inbox) + #2 (show Spotify link) | Small — schema + frontend only |
| **2** | #3 (sender identity) | Small — repo join + schema + frontend |
| **3** | #4 (recipient Spotify export) | Medium — auth change + OAuth redirect + frontend |
| **4** | #5 (meaningful claimed) | Medium — migration + new endpoint + frontend |

Phases 1–2 are independent and can be done in parallel. Phase 3 depends on #2 being done. Phase 4 is fully independent.
