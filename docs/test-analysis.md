# Test Suite Analysis (Aug 2026)

Analysis of the backend test suite: where the time goes, why tests are slow, and
duplication found. No changes were made during analysis.

## Measurements

- Unit tests: 52 tests, ~7s total.
- Integration tests: 72 tests, ~225s (~4 min).

## Where the time goes

### 1. Real argon2 password hashing (dominant cost)

`app/services/auth_service.py` uses the default `PasswordHasher()` (64MB memory,
t=3) — deliberately expensive by design.

- **Unit tests**: `test_register_success` alone is 2.18s because it patches the
  repository but not `ph`, so it runs a real argon2 hash. Every other auth unit
  test already mocks `ph` (the good pattern).
- **Integration tests**: the conftest mocks Spotify and email but **not the
  password hasher**. `register_and_login` is called 58 times plus raw
  `register` calls — ~115 auth operations in total, each a hash (~0.4s idle,
  ~2s under CPU contention) plus a verify (~0.35s). This is most of the 225s.

### 2. Per-test full schema rebuild

The autouse `setup_database` fixture in `tests/integration/conftest.py` runs
`create_all` + `drop_all` for every test — ~0.3–0.5s × 72 ≈ 35–40s total.

### 3. No connection reuse + duplicated engines

Three separate engine/sessionmaker copies exist (conftest, `test_auth.py`,
`test_tapes.py`), all with `NullPool`, so every request opens a fresh TCP
connection to Postgres.

## Duplication found

- `FakeSpotifyClient` defined twice: `tests/unit/test_spotify_service.py` and
  `tests/integration/conftest.py`.
- `TEST_DATABASE_URL` + engine + sessionmaker copied in 3 files
  (`conftest.py`, `test_auth.py`, `test_tapes.py`).
- Helpers split messily:
  - `create_track` in both `test_tapes.py` and `test_tracks.py`
  - `helper_send_tape` in both `test_tapes.py` and `test_spotify.py`
  - `test_tracks.py` / `test_spotify.py` import helpers from `test_tapes.py`
    (fragile cross-test-file imports)
- `mock_db` fixture redefined in `test_tape_service.py`, `test_track_service.py`,
  `test_auth_service.py`.

Note: `test_verify_email_claims_tapes` and
`test_send_tape_claims_immediately_for_verified_recipient` look alike but test
**different business rules** (claim-on-verify vs claim-at-send). Not true
duplicates; only the setup steps overlap.

## Best practice for the hashing fix

Keep a real hasher but at reduced cost in tests (what Django does by swapping in
a fast hasher for tests). You keep exercising the real hash→store→verify round
trip while making it fast. Concretely:

```python
PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)
```

patched into `app.services.auth_service.ph` via an autouse fixture. `verify`
still works because argon2 reads its parameters from the stored hash string.
Don't drive cost from an env var that production could read — test-only
patching is safer.

## Improvement plan

Priority order, biggest win first:

1. **Fast/low-cost password hashing for tests** (~150s win)
   - Integration: autouse fixture swaps `auth_service.ph` for a low-cost
     `PasswordHasher` (or a fake). Real hashing stays covered by unit tests.
   - Unit: mock `ph.hash` in `test_register_success` (matching the login tests).
2. **Single shared DB engine/sessionmaker** in `tests/integration/conftest.py`.
3. **Centralize helpers + `FakeSpotifyClient`** (de-duplication; details below).
4. **Session-scoped schema creation + truncate-between-tests** instead of full
   rebuild per test. (Implemented — see status below.)
5. **`pytest-xdist` parallelism** — tempting but won't work for integration
   tests as-is: workers would clobber each other on the shared DB's
   create/drop. Needs per-worker DBs. (Deferred — not worth the complexity for
   this project.)

## De-duplication plan (current scope)

1. **`tests/fakes.py` (new)** — one `FakeSpotifyClient` (merge the two
   near-identical copies; keep the query-aware `search`). Unit and integration
   both import it.
2. **`tests/integration/helpers.py` (new)** — single home for
   `register_and_login`, `create_tape`, `create_track`, `mark_tape_ready`,
   `helper_send_tape`. Removes the duplicated helpers and the fragile
   cross-file imports.
3. **`tests/integration/conftest.py`** — single source of the engine and
   `TestSessionLocal`; delete the duplicates in `test_auth.py` and
   `test_tapes.py`. Keep `NullPool`.
4. **`tests/unit/conftest.py` (new)** — shared `mock_db` fixture; delete the
   identical redefinitions in the unit test files.
5. Keep both "claims tapes" tests (different rules); optionally extract a shared
   "register + verify recipient" helper.

Verification after changes:
- `docker compose exec backend bash -lc "cd /workspace/backend && uv run pytest -q"`
- `uv run pre-commit run --all-files`

## Implementation status (post-fix verification, Aug 2026)

Items 1–4 of the improvement plan were implemented and verified. Timings:
unit 3.4s (was ~7s), integration ~57s (was 64s after items 1–3, ~225s
originally). All 52 unit + 72 integration tests pass.

- **1. Fast hashing — implemented correctly.** Integration autouse
  `fast_password_hasher` fixture patches `app.services.auth_service.ph` with
  `PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)` (the recommended
  snippet). Unit `test_register_success` patches the same low-cost hasher
  instead of a mock — this is fine, arguably better: it keeps the real
  hash→store→verify round trip while staying fast.
- **2. Single shared engine/sessionmaker — implemented correctly.**
  `TEST_DATABASE_URL`/`test_engine`/`TestSessionLocal` now exist only in
  `tests/integration/conftest.py`; `test_auth.py`, `test_tapes.py`,
  `test_tracks.py` all import `TestSessionLocal` from conftest. `NullPool`
  retained.
- **3. Centralize helpers + FakeSpotifyClient — done.**
  - `tests/integration/helpers.py` is the single home for
    `register_and_login`, `create_tape`, `create_track`, `mark_tape_ready`,
    `helper_send_tape`; all integration tests import from it; the fragile
    cross-test-file imports are gone. `mock_db` is centralized in
    `tests/unit/conftest.py` with the three redefinitions removed.
  - `tests/fakes.py` is the single home for `FakeSpotifyClient`, imported by
    both `tests/integration/conftest.py` and `tests/unit/test_spotify_service.py`.
    The fake keeps the query-aware `search` (`"Mock result for {query}"`), so
    `test_search_tracks_authenticated` still proves the `q` parameter reaches
    the client. `test_search_tracks_returns_formatted_results` asserts the
    query-aware values (`mock_1`, `Mock result for beatles`, `Mock Artist`,
    `Mock Album`, 200s).

Note: the unit copy of `FakeSpotifyClient` previously returned realistic canned
data ("Come Together", 259s) and the integration copy query-aware data. They
are now merged into one query-aware fake; the unit test's expected values were
updated to match. Both copies shared the same interface and response shape, so
a single fake is sufficient.
- **4. Session-scoped schema + truncate-between-tests — implemented.**
  `setup_database` is now `scope="session"` (create_all once, drop_all once);
  a new autouse `truncate_tables` fixture empties all tables
  (`TRUNCATE ... RESTART IDENTITY CASCADE`, table list from
  `Base.metadata.sorted_tables`) before each test. Measured win was ~7s
  (64s → 57s), smaller than the ~30s originally estimated — the earlier
  estimate was made while argon2 hashing still dominated the run. The
  per-test fixture cost dropped from ~450ms (create+drop) to ~110ms
  (truncate). Point 5 (pytest-xdist) was deliberately not implemented: it
  needs per-worker databases and the complexity isn't justified for this
  suite.
