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
   rebuild per test (~30s win). (Deferred — keep per-test rebuild for now.)
5. **`pytest-xdist` parallelism** — tempting but won't work for integration
   tests as-is: workers would clobber each other on the shared DB's
   create/drop. Needs per-worker DBs. (Deferred.)

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
