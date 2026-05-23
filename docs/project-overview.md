# Project overview: Rewind

A web app where users create virtual cassette tapes, fill them with songs from Spotify, and send them to friends.

The cassette page is the product. Spotify is an optional export.

---

## What it does

A user picks a cassette style, selects a tape length (60 or 90 minutes), and searches Spotify for songs to fill Side A and Side B. Song titles appear on the cassette label in real time as tracks are added, rendered in a retro Google Font (Caveat or Special Elite). The total runtime per side can't exceed half the tape length.

When the tape is ready, the sender enters a friend's email and an optional message. The friend gets an email with a link to a public tape page — no account needed to view it. They can create an account to save the tape, send their own, or claim it to their inbox.

Spotify playlist creation is an optional export step. The sender can connect their Spotify account and generate a public playlist, but the app works fully without it.

Every user has 2 views: tapes sent (recipient, send date, tape title) and tapes received (sender, message, tape title).

---

## The one-screen demo moment

A user adds a song and watches its title appear on the cassette label in real time. That's the moment.

---

## MVP features

- User registration and login (JWT auth)
- Cassette creation: style selection, length (60 or 90 min), song search via Spotify API
- Side A / Side B split: 30 min each for a 60-min tape, 45 min each for a 90-min tape
- Live time remaining display per side as tracks are added
- Cassette label: song titles rendered in real time in a retro Google Font
- Public tape URL: anyone can view a sent tape without an account
- Optional account creation for recipients: save tapes, send their own
- Email delivery: invitation email with public tape link, sent via Resend or Brevo free tier
- Inbox and outbox per user
- Spotify export (optional): sender connects Spotify, app creates a public playlist

---

## Tape state machine

- `draft`: being built, not yet sent
- `ready`: complete, ready to send
- `sent`: delivered to recipient email, public URL active
- `claimed`: recipient created an account and saved the tape
- `archived`: sender archived it from their outbox

---

## Tech stack

**Backend**
- Python, FastAPI
- Layered architecture: router, service, repository
- PostgreSQL with SQLAlchemy ORM
- Alembic for migrations
- Pydantic for request/response validation and typing
- JWT for authentication
- Loguru for structured logging
- Routes prefixed with `/api/v1/`

**Frontend**
- React, TypeScript, Tailwind CSS
- Cassette visuals built in pure CSS (no images)
- Google Fonts for label typography
- Live runtime counter updates as tracks are added
- Label updates are React state only — no polling or WebSockets.

**Integrations**
- Spotify Web API: track search and duration lookup via Client Credentials (no user login required); playlist creation via OAuth 2.0 (optional, sender only)
- Resend: transactional email (free tier)

**Tooling**
- Black and Ruff for Python formatting and linting
- Prettier for TypeScript/React formatting
- pre-commit hooks: runs Black, Ruff, and Prettier before every commit
- GitHub Actions CI: runs tests on every push
- Docker and dev containers for local development
- python-dotenv for environment variables, `.env.example` in repo

**Deployment (free tier)**
- Backend: Railway or Render
- Frontend: Vercel

---

## Data models

**User**
- id, email, password_hash, created_at, updated_at

**Tape**
- id, title, cassette_style, length_minutes (60 or 90)
- status (draft, ready, sent, claimed, archived)
- sender_id (FK: User), recipient_id (FK: User, nullable)
- recipient_email, message, spotify_playlist_url (nullable)
- public_token (unique URL slug, generated on send)
- sent_at, created_at

**Track**
- id, tape_id (FK: Tape), spotify_track_id, title, artist, duration_seconds, side (A or B), position

**Spotify Token**
- spotify_access_token, spotify_refresh_token (nullable, set after OAuth)
---

## Constraints and rules

- Side A and Side B are each capped at half the tape length
- A user removes a track if a side is full; no auto-trim
- A tape can only be sent once
- The public tape URL is active as soon as the tape is sent, with or without a recipient account

---

## Spotify integration details

- Track search and duration lookup use Client Credentials flow. The app gets a token with its own client ID and secret. No user login needed.
- Playlist creation uses Authorization Code flow (OAuth 2.0). Only the sender, and only at export time.
- Spotify tokens stored server-side, never sent to the frontend.
- The Spotify export is a button, not a required step.

---

## Testing

TDD where practical. Tests written alongside code.

- pytest for unit and integration tests
- 100% coverage target on the service layer
- Integration tests for critical endpoints: register, login, create tape, add track, send tape, fetch public tape, claim tape
- UI component tests skipped unless the component has complex logic
- Test report shown in README: passing count and service layer coverage percentage
- GitHub Actions runs the full test suite on every push

---

## Security

- Passwords hashed with Argon2
- JWT tokens with expiry, stored in httpOnly cookies
- Spotify tokens stored server-side, never exposed to the frontend
- Public tape URLs use a random token, not a sequential ID
- All secrets in environment variables, never in source code
- `.env.example` documents required variables without values
- Input validated with Pydantic on every endpoint

---

## Open questions

- Side A / Side B split: fixed 50/50 or user-controlled? Decide during build.
- Spotify API app approval: dev mode supports 25 users. A SPOTIFY_MOCK flag returns fake results in tests and CI. Production calls the real API. Spotify review needed for public use beyond 25 users.
- App name: Rewind or B-Side. Decide before first commit.