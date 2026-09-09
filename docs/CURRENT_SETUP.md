# Current setup and verification

PredictIQ uses a Python 3.13 FastAPI backend, Firebase Authentication, PostgreSQL through asyncpg, local or S3 document storage, and a React 19/TypeScript/Vite frontend. Supabase migrations are legacy reference material. Alembic under `backend/alembic` is the canonical migration history.

## Local setup

**Model integrity gate (September 9, 2026):** the bundled legacy model and training CSV are revoked because source effort labels were corrupted. Their presence does not make inference ready. Prediction and readiness remain unavailable until a compatible, independently validated replacement is approved. The rebuilt 787-project baseline is research-only; see [reproduction and metrics](ml_rebuild_2026-09-09.md).

1. Install Python 3.13 and Node.js 22 or newer. Create a backend virtual environment and install `backend/requirements.lock.txt` with pip. The lock includes hashes and pins scikit-learn to the version required by the bundled artifacts.
2. Copy `backend/.env.example` to `backend/.env`. Supply the database URL and either `FIREBASE_CREDENTIALS_PATH` or `FIREBASE_CREDENTIALS_JSON`. Never commit these values or copy them into an image.
3. Run `python -m alembic upgrade head` from `backend` against the intended development database. For an existing deployment, inspect its schema/history and take a backup before baselining or upgrading. Do not use the legacy SQL-only helper to provision a new release.
4. Verify `backend/ml/predictiq_best_model.pkl`, `predictiq_scaler.pkl`, and `predictiq_features.json` are present. Inference does not manufacture demo estimates when artifacts are absent or invalid.
5. Run `python -m uvicorn main:app --host 127.0.0.1 --port 8000 --no-access-log` from `backend`.
6. In `frontend`, copy the environment example and supply the six public `VITE_FIREBASE_*` values from the same Firebase project. Run `npm ci`, then `npm run dev`.

`GET /api/v1/live` reports process liveness. `/api/v1/ready` and `/api/v1/health` return 503 unless Firebase, PostgreSQL, and the model are ready. An absent service account is a configuration failure, not a reason to bypass authentication.

## Storage and APIs

Upload bytes to `POST /api/v1/documents/upload-file`. The metadata-only `/documents/upload` endpoint returns 410. Extraction and analysis read the owned object's `storage_path`; they do not use the legacy `file_data` column. The old column is retained to avoid destructive migration; historical BYTEA-only records need an explicit migration/re-upload.

Core endpoints:

- `POST /api/v1/documents/{id}/extract`
- `POST /api/v1/estimates/analyze` and `/estimates/manual`
- `GET /api/v1/estimates` and `/estimates/{id}`
- `GET /api/v1/estimates/{id}/export/pdf` and `/export/json`
- `POST /api/v1/estimates/{id}/share`
- `GET /api/v1/shared/{token}`; password-protected links use `POST` with a JSON password
- Public browser page: `/share/{token}`

OpenAPI at `/docs` is the authoritative route/schema reference. There is no CSV export. Share responses omit owner/document identifiers; expiry and estimate deletion disable access.

Production/staging requires S3 unless durable local storage is explicitly enabled. Single-host Compose mounts a named uploads volume and enables that opt-in. Replicas on different hosts must use shared object storage. Run Compose with the frontend public build variables available, for example `docker compose --env-file frontend/.env up --build`; backend secrets are supplied through its runtime env file. Back up the uploads volume/database together and test restores.

## Verification

Backend development tools: `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `mypy`, `types-requests`, `pip-audit`, and `bandit`.

From `backend`:

```text
python -m pytest tests
python -m ruff check . --select E,W,F,I --ignore E501
python -m mypy app
python -m pip_audit -r requirements.lock.txt --no-deps --disable-pip
```

Set `PREDICTIQ_TEST_DATABASE_URL` only to a separate, migrated test database to enable real persistence and concurrency tests. Tests never use the application database URL as that fallback. CI provisions disposable PostgreSQL and runs the migrations before the suite.

From `frontend`:

```text
npm run typecheck
npm run lint
npm test
npm run build
npm audit --omit=dev --audit-level=high
npx playwright install chromium
npx playwright test
```

Playwright starts the frontend and an isolated backend harness with real middleware and no cloud startup. Its public-page checks complement the real PostgreSQL/model integration tests. Authenticated Firebase browser testing still requires an isolated emulator/test-project setup.

For a locally built frontend image, set `PREDICTIQ_TEST_FRONTEND_IMAGE` to its local tag and run `python -m unittest discover -s scripts/tests -p test_frontend_container.py -v` from the repository root. This creates a temporary container with a local upstream stub to check Nginx upload limits, security/cache headers, and share-token access-log privacy, then removes that container. Use test-only public Firebase build values for this image. The Dockerfile copies the root `nginx.conf` directly.

## Release prerequisites

Configure the six public Firebase repository/environment variables before clean CI/CD builds. Production builds fail when these are absent. Backend secrets remain runtime-only. Staging deploys from successful CI; production requires successful CI for the selected commit. Nothing in the local repair session was pushed or deployed.

See [engineering progress](engineering_progress_2026-09-08.md), [credential containment](security_containment_2026-09-08.md), and [model contract](../backend/ml/README.md) for verified changes and outstanding release work, including credential rotation, role reconciliation, calibrated uncertainty, immutable promotion, and restore verification.
