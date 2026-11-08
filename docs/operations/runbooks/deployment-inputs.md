Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# Operational Runbook: Production Deployment Inputs & Verification

This runbook catalogs the required inputs, credentials, and verification gates necessary to configure and approve a production deployment of PredictIQ.

---

## 1. Required Deployment Inputs Matrix

| Category | Input Identifier | Description / Format | Target Location |
|----------|------------------|----------------------|-----------------|
| **Database** | `DATABASE_URL` | Neon PostgreSQL production URI with `sslmode=require`. | AWS Secrets Manager (`predictiq/production/database-url`) |
| **Auth (Server)** | `FIREBASE_CREDENTIALS_JSON` | Firebase Admin SDK service account key JSON. | AWS Secrets Manager (`predictiq/production/firebase-credentials`) |
| **Auth (Client)** | `VITE_FIREBASE_*` (6 variables) | Web app configuration from Firebase Console. | GitHub Actions production environment variables |
| **Storage** | `STORAGE_BACKEND` | Must be set to `s3` in production. | ECS Task Definition environment |
| **Storage Bucket**| `S3_BUCKET_NAME` | Dedicated AWS S3 bucket for documents. | ECS Task Definition environment |
| **Storage Region**| `S3_REGION` | AWS region hosting bucket (e.g., `us-east-1`). | ECS Task Definition environment |
| **CORS** | `ALLOWED_ORIGINS` | Strict HTTPS frontend domain (e.g. `https://app.predictiq.io`). | ECS Task Definition environment |
| **Release Mode** | `RELEASE_MODE` | Must be set to `prediction` for full estimation capabilities. | ECS Task Definition environment |
| **ML Artifacts** | Production Manifest Hash | Pinned SHA-256 digest of `manifest.json`. | Verified by `loader.py` during startup |

---

## 2. Pre-Deployment Preflight Checks

Run the production preflight script to validate environment shape and configuration syntax prior to launching services:

```bash
# Execute preflight check within production environment context
python scripts/production_preflight.py
```

The preflight check validates:
1. `DATABASE_URL` is well-formed with valid driver syntax (`postgresql://` or `postgresql+asyncpg://`).
2. `RELEASE_MODE` is explicitly set to `prediction`.
3. `STORAGE_BACKEND` is set to `s3` and S3 bucket settings are populated.
4. `ALLOWED_ORIGINS` does not contain unencrypted HTTP or wildcard `*` domains.
5. All 9 checks of `scripts/release_gate.py` have passed on the deployed commit SHA.
