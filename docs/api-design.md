# API design: Rewind

---

## Overview

REST API. All endpoints prefixed with `/api/v1/`.

The frontend is the only consumer. There are no third-party API clients.

Versioning is in the URL from day one. Adding `/v2/` later requires no changes to existing clients.

---

## Conventions

### Authentication

Two access levels:

- `public`: no authentication required
- `protected`: requires a valid JWT cookie

The JWT is set by the backend on login as an httpOnly cookie. The frontend never reads it directly. Every protected request sends the cookie automatically.

### Request and response format

All requests and responses use `application/json`.

Dates and timestamps use ISO 8601: `2024-03-15T10:30:00Z`.

### Standard error shape

Every error response uses the same shape:

```json
{
  "error": "NotFound",
  "message": "Tape not found",
  "details": {}
}
```

`error` is a machine-readable code. `message` is human-readable. `details` is optional and contains field-level validation errors where relevant.

Error messages never reveal internal details. "Invalid credentials" not "user not found" or "wrong password".

### HTTP status codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 204 | Success, no content |
| 400 | Bad request (malformed input) |
| 401 | Not authenticated |
| 403 | Authenticated but not authorised |
| 404 | Resource not found |
| 409 | Conflict (e.g. email already registered) |
| 422 | Validation error |
| 429 | Rate limit exceeded |
| 500 | Server error |

### Pagination and sorting

All list endpoints support pagination and sorting query parameters even if the frontend uses defaults for now. This means the backend contract is future-proof and pagination can be added to the UI later with no API changes.

```
GET /api/v1/tapes?page=1&page_size=20&sort=sent_at&order=desc
```

| Parameter | Default | Notes |
|---|---|---|
| page | 1 | Page number, starts at 1 |
| page_size | 20 | Max 100 |
| sort | created_at | Field to sort by |
| order | desc | asc or desc |

All list responses use this envelope:

```json
{
  "items": [],
  "total": 45,
  "page": 1,
  "page_size": 20,
  "pages": 3
}
```

---

## Rate limiting

Rate limiting protects both the app and the Spotify API quota.

| Endpoint group | Limit |
|---|---|
| `POST /auth/login` | 10 requests per minute per IP |
| `POST /auth/register` | 5 requests per minute per IP |
| `GET /spotify/search` | 30 requests per minute per user |
| All other endpoints | 60 requests per minute per user |

Exceeding a limit returns `429 Too Many Requests` with a `Retry-After` header.

---

## CSRF protection

The app uses JWT in httpOnly cookies. Cookies are sent automatically by the browser, which makes state-changing requests vulnerable to cross-site request forgery.

All state-changing endpoints (POST, PATCH, DELETE) require a CSRF token sent as a custom header: `X-CSRF-Token`. The backend validates this token on every state-changing request.

GET requests are exempt. They do not change state.

---

## Third-party API strategy (Spotify)

The frontend never calls Spotify directly. All Spotify calls go through the Rewind backend. This protects API credentials and gives the backend full control over rate limiting and error handling.

Rules for all Spotify-proxied requests:

- Search queries are sanitised and length-limited before being forwarded (max 100 characters)
- The backend validates the Spotify response before returning it to the frontend
- Spotify errors are caught and returned as standard Rewind error responses
- Results are cached server-side for 5 minutes to reduce redundant API calls
- The frontend uses a debounce on the search input (minimum 300ms) to avoid sending a request on every keystroke

These rules apply to any third-party API added in the future, not just Spotify.

---

## Endpoints

---

### Auth

#### `POST /api/v1/auth/register` — public

Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Validation:**
- `email`: valid email format, max 255 characters
- `password`: min 8 characters, at least 1 uppercase, at least 1 number

**Response `201`:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2024-03-15T10:30:00Z"
}
```

**Errors:**
- `409` email already registered

**Notes:**

Sends a verification email after registration. Auto-claiming of tapes runs after email verification, not immediately on registration. A future alternative is explicit claiming: the recipient clicks a button on the tape page. The service layer function is the same either way; only the trigger changes.

---

#### `POST /api/v1/auth/login` — public

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response `200`:**
```json
{
  "id": 1,
  "email": "user@example.com"
}
```

Sets a JWT in an httpOnly cookie. Also sets a CSRF token cookie (readable by JavaScript, used for the `X-CSRF-Token` header).

**Errors:**
- `401` invalid credentials (same message whether email or password is wrong)

---

#### `POST /api/v1/auth/logout` — protected

Clears the JWT cookie and CSRF cookie.

**Response `204`:** no content

---

#### `GET /api/v1/auth/me` — protected

Returns the current authenticated user.

**Response `200`:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2024-03-15T10:30:00Z"
}
```

---

#### `POST /api/v1/auth/verify-email` — public

Verifies a user's email using the token sent in the verification email.

**Request:**
```json
{
  "token": "abc123verificationtoken"
}
```

**Response `200`:**
```json
{
  "message": "Email verified"
}
```

**Errors:**
- `400` token invalid or expired

---

### Tapes

#### `POST /api/v1/tapes` — protected

Create a new tape in `draft` status.

**Request:**
```json
{
  "title": "Summer Mix",
  "cassette_style": "classic",
  "length_minutes": 60
}
```

**Validation:**
- `title`: max 100 characters
- `cassette_style`: must be a known style value
- `length_minutes`: must be 60 or 90

**Response `201`:**
```json
{
  "id": 1,
  "title": "Summer Mix",
  "cassette_style": "classic",
  "length_minutes": 60,
  "status": "draft",
  "tracks": [],
  "created_at": "2024-03-15T10:30:00Z"
}
```

---

#### `GET /api/v1/tapes/{tape_id}` — protected

Returns a tape owned by the current user (sent or received).

**Response `200`:**
```json
{
  "id": 1,
  "title": "Summer Mix",
  "cassette_style": "classic",
  "length_minutes": 60,
  "status": "draft",
  "recipient_email": null,
  "message": null,
  "spotify_playlist_url": null,
  "tracks": [
    {
      "id": 1,
      "spotify_track_id": "4uLU6hMCjMI75M1A2tKUQC",
      "title": "Come Together",
      "artist": "The Beatles",
      "duration_seconds": 259,
      "side": "A",
      "position": 1
    }
  ],
  "created_at": "2024-03-15T10:30:00Z"
}
```

**Errors:**
- `403` tape belongs to another user
- `404` tape not found

---

#### `GET /api/v1/tapes/public/{public_token}` — public

Returns a sent tape by its public token. No authentication required. Used for the shareable tape link.

**Response `200`:** same shape as above, minus any private fields (recipient email is excluded)

**Errors:**
- `404` tape not found or not yet sent

---

#### `PATCH /api/v1/tapes/{tape_id}` — protected

Update tape metadata while in `draft` status.

**Request** (all fields optional):
```json
{
  "title": "Summer Mix 2024",
  "cassette_style": "chrome"
}
```

**Response `200`:** updated tape object

**Errors:**
- `403` tape belongs to another user
- `409` tape is not in draft status

---

#### `PATCH /api/v1/tapes/{tape_id}/ready` — protected
Marks a tape as ready to send. Transitions status from draft to ready.
Request: no body required
Response 200: updated tape object
Errors:

403 tape belongs to another user
409 tape is not in draft status
422 tape has no tracks


NOTE: the service layer should validate that the tape has at least one track before allowing the transition. An empty tape should not be sendable.

#### `POST /api/v1/tapes/{tape_id}/send` — protected

Send a tape. Transitions status from `ready` to `sent`. Generates the public token and sends the email.

**Request:**
```json
{
  "recipient_email": "maria@example.com",
  "message": "Made this for you"
}
```

**Validation:**
- `recipient_email`: valid email format
- `message`: optional, max 500 characters

**Response `200`:**
```json
{
  "id": 1,
  "status": "sent",
  "public_token": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "sent_at": "2024-03-15T10:30:00Z"
}
```

**Errors:**
- `409` tape is not in ready status
- `409` tape has already been sent

---

#### `PATCH /api/v1/tapes/{tape_id}/archive` — protected

Archive a sent tape. Only the sender can archive.

**Response `200`:** updated tape object

---

#### `GET /api/v1/tapes/sent` — protected

Returns the current user's outbox.

**Query params:** `page`, `page_size`, `sort` (default: `sent_at`), `order` (default: `desc`)

**Response `200`:**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Summer Mix",
      "recipient_email": "maria@example.com",
      "status": "sent",
      "sent_at": "2024-03-15T10:30:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

---

#### `GET /api/v1/tapes/received` — protected

Returns the current user's inbox.

**Query params:** `page`, `page_size`, `sort` (default: `sent_at`), `order` (default: `desc`)

**Response `200`:** same envelope, items show sender info instead of recipient

---

### Tracks

#### `POST /api/v1/tapes/{tape_id}/tracks` — protected

Add a track to a tape. Only allowed while tape is in `draft` status.

**Request:**
```json
{
  "spotify_track_id": "4uLU6hMCjMI75M1A2tKUQC",
  "title": "Come Together",
  "artist": "The Beatles",
  "duration_seconds": 259,
  "side": "A",
  "position": 1
}
```

**Validation:**
- `side`: must be `A` or `B`
- `duration_seconds`: adding this track must not exceed the side's time limit
- `position`: must be a positive integer

**Response `201`:** the created track object

**Errors:**
- `403` tape belongs to another user
- `409` tape is not in draft status
- `422` side would exceed time limit

---

#### `DELETE /api/v1/tapes/{tape_id}/tracks/{track_id}` — protected

Remove a track from a tape. Only allowed while tape is in `draft` status.

**Response `204`:** no content

**Errors:**
- `403` tape belongs to another user
- `409` tape is not in draft status

---

### Spotify

#### `GET /api/v1/spotify/search` — protected

Search for tracks via Spotify. The backend proxies the request; the frontend never calls Spotify directly.

**Query params:**
- `q`: search query, required, max 100 characters

**Example:** `GET /api/v1/spotify/search?q=the+beatles`

**Response `200`:**
```json
{
  "tracks": [
    {
      "spotify_track_id": "4uLU6hMCjMI75M1A2tKUQC",
      "title": "Come Together",
      "artist": "The Beatles",
      "album": "Abbey Road",
      "duration_seconds": 259,
      "preview_url": "https://p.scdn.co/mp3-preview/..."
    }
  ]
}
```

**Errors:**
- `422` query missing or too long
- `429` rate limit exceeded
- `502` Spotify API unavailable

---

#### `GET /api/v1/spotify/auth` — protected

Starts the Spotify OAuth flow for playlist export. Redirects the user to Spotify's consent screen.

---

#### `GET /api/v1/spotify/callback` — public

Spotify redirects here after the user grants permission. The backend exchanges the auth code for tokens and stores them.

**Response:** redirects to the frontend with a success or error query parameter.

---

#### `POST /api/v1/spotify/export/{tape_id}` — protected

Creates a Spotify playlist from a sent tape. Requires the user to have connected their Spotify account.

**Response `200`:**
```json
{
  "spotify_playlist_url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
}
```

**Errors:**
- `403` tape belongs to another user
- `409` tape has not been sent yet
- `422` Spotify account not connected

---

## Security summary

| Concern | Approach |
|---|---|
| Authentication | JWT in httpOnly cookie |
| CSRF | X-CSRF-Token header on all state-changing requests |
| Password storage | Argon2 hash, never stored plain |
| Error messages | Never reveal user existence or internal details |
| Rate limiting | Per-IP on auth endpoints, per-user on others |
| Spotify credentials | Stored server-side, never sent to frontend |
| Public tape URLs | Random UUID token, not sequential ID |
| Input validation | Pydantic on every endpoint |
| Third-party requests | Sanitised, length-limited, cached, never proxied raw |
