# Rewind

A full-stack web app where you create virtual cassette tapes, fill them with songs from Spotify, and send them to your friends via email. It's like making someone a mixtape but in 2026.

## Why?

I wanted to build something fun and creative while also practicing enterprise-grade patterns. It's a portfolio project that I hope shows what I can do across the full stack.

## Features

- [x] Create a custom cassette with different styles (classic, chrome, metal, vintage)
- [x] Pick a tape length (60 or 90 minutes)
- [x] Search and add songs from Spotify to Side A and Side B
- [x] See the cassette label update in real time as you add tracks
- [x] Send your tape to a friend via email
- [x] Friends can view the tape without needing an account
- [x] Track sent and received tapes in your inbox and outbox
- [x] Recipients claim the tape by creating an account and verifying their email
- [x] Export tapes to Spotify playlists

## Tech Stack

### Backend

- **Python 3.12** with **FastAPI**
- **SQLAlchemy 2.0** (async) + **Alembic** for migrations
- **PostgreSQL 16**
- **JWT** authentication with **Argon2** password hashing
- **Pydantic 2.x** for validation
- **Loguru** for structured logging
- **Resend** for email delivery
- **httpx** for async HTTP (Spotify API calls)

### Frontend

- **React 19** + **TypeScript**
- **Tailwind CSS**
- **Vite**
- **Zustand** for state management
- **TanStack React Query** for server state
- **React Router 7**
- **react-hot-toast** for notifications

### Tooling

- **Docker** and **Docker Compose**
- **uv** (Python package manager)
- **Black**, **Ruff**, and **Prettier** for formatting/linting
- **pre-commit** hooks
- VS Code **Dev Containers** support

## Getting Started

### Prerequisites

- Docker and Docker Compose
- A Spotify Developer app (Client ID + Secret)
- (Optional) VS Code with the Dev Containers extension

### Installation

1. Clone the repo:

```bash
git clone https://github.com/mmazzet/rewind.git
cd rewind
```

2. Create a `.env` file in the `backend/` directory:

```bash
# backend/.env
DATABASE_URL=postgresql+asyncpg://rewind:rewind@db:5432/rewind
JWT_SECRET=your-secret-key-here
ENV=development
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
SPOTIFY_REDIRECT_URI=https-ngrok-link
PUBLIC_BASE_URL=http://localhost:5173
RESEND_API_KEY=your-resend-api-key
RESEND_FROM_EMAIL=you@example.com
```

3. Start the dev environment:

```bash
docker compose up -d
```

4. Run database migrations:

```bash
docker compose exec backend alembic upgrade head
```

5. Open the app:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/docs

## Project Structure

```
Rewind/
├── backend/            # Python/FastAPI backend
│   ├── app/
│   │   ├── core/       # Config, security, exceptions
│   │   ├── models/     # SQLAlchemy models
│   │   ├── schemas/    # Pydantic schemas
│   │   ├── repositories/  # Data access layer
│   │   ├── services/   # Business logic (auth, tape, track, spotify, email)
│   │   ├── routers/    # API endpoints
│   │   ├── middleware/  # Error handlers
│   │   └── db/         # Async session factory
│   ├── tests/          # Unit and integration tests
│   └── alembic/        # Database migrations
├── frontend/           # React/TypeScript frontend
│   └── src/
│       ├── api/        # Axios clients, helpers
│       ├── store/      # Zustand stores
│       ├── components/ # Shared components (Nav, ErrorBoundary, ProtectedRoute)
│       └── features/   # Feature modules (auth, tapes, inbox, outbox)
├── docs/               # Project documentation
└── docker-compose.yml
```

## How It Works

### Tape Lifecycle

Every tape goes through a state machine:

```
draft → ready → sent → claimed
                  ↓
               archived
```

You create a draft, add tracks to Side A and Side B, mark it as ready when the total duration fits within the tape length (60 or 90 min), then send it. Your friend gets an email with a link to view the tape, no account needed.

### Cassette Visual

The cassette is pure CSS, no images. It has 4 themes (classic, chrome, metal, vintage) and the label text updates in real time as you add tracks. It uses the Caveat Google Font for that handwritten style.

### Email Integration

Tapes are sent via the Resend API. When you hit send, your friend gets an email with a link to the public tape page. If the recipient already has a verified account, the tape is claimed immediately; otherwise they can register, verify their email, and claim it into their inbox.

### CSRF Protection

All state-changing requests require an `X-CSRF-Token` header that matches a `csrf_token` cookie. This is handled automatically by the frontend Axios client.

## API Overview

All endpoints live under `/api/v1/`.

**Auth** — register, login, logout, email verification, and session restore (`GET /auth/me`)

**Tapes** — create a draft, get a tape, mark ready, send, archive, and list your inbox/outbox. There's also a public endpoint (`GET /tapes/public/{token}`) that doesn't require auth.

**Tracks** — add and remove tracks from a draft tape. Each side has a time limit based on the tape length.

**Spotify** — search endpoint that queries the Spotify API on your behalf, plus OAuth connect and playlist export of a tape.

## Development

### Running Tests

The backend has unit tests for services and integration tests that spin up a real test database. Spotify calls are mocked with a `FakeSpotifyClient` in tests.

## Roadmap

- [x] Phase 6: Inbox and outbox
- [x] Phase 7: Email verification and tape claiming
- [x] Phase 8: Spotify playlist export
- [ ] Phase 9: Observability and CI/CD
- [ ] Phase 10: Polish and backlog
