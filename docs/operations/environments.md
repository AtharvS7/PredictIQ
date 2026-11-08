Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# Environment Configuration Matrix (Dev, Staging, Production)

This document provides a single source of truth for all runtime configuration variables across PredictIQ environments, documenting defaults, allowed values, and environment-specific parameters.

---

## 1. Environment Comparison Matrix

| Variable Name | Type / Format | Development | Staging | Production | Description |
|---------------|---------------|-------------|---------|------------|-------------|
| `APP_ENV` | `string` | `development` | `staging` | `production` | Active runtime environment name. |
| `APP_VERSION` | `string` | `2.0.0-rc.3` | `2.0.0-rc.3` | `2.0.0-rc.3` | Application build & API release tag. |
| `RELEASE_MODE` | `enum` | `prediction` | `prediction` | `prediction` | Release mode: `prediction` (requires verified ML model) or `manual_budget`. |
| `DATABASE_URL` | `string (URI)` | `postgresql://...localhost:5432/predictiq_dev` | Neon Staging Branch URI | Neon Production Branch URI | PostgreSQL connection URI (`sslmode=require` in cloud). |
| `DB_POOL_MIN_SIZE` | `integer` | `1` | `2` | `5` | Minimum connection pool size. |
| `DB_POOL_MAX_SIZE` | `integer` | `5` | `10` | `20` | Maximum connection pool size. |
| `DB_COMMAND_TIMEOUT`| `integer` | `30` | `30` | `15` | Database command deadline in seconds. |
| `STORAGE_BACKEND` | `enum` | `local` | `s3` | `s3` | Object storage provider: `local` or `s3`. |
| `ALLOW_LOCAL_STORAGE_IN_PRODUCTION` | `boolean` | `true` | `false` | `false` | Prevents container restarts from losing documents in cloud environments. |
| `LOCAL_STORAGE_PATH` | `string (path)` | `./uploads` | N/A | N/A | Filesystem path for local document storage. |
| `S3_BUCKET_NAME` | `string` | N/A | `predictiq-staging-documents` | `predictiq-prod-documents` | S3 bucket name for document uploads. |
| `S3_REGION` | `string` | `us-east-1` | `us-east-1` | `us-east-1` | AWS region hosting S3 bucket. |
| `S3_ACCESS_KEY_ID` | `string` | Optional | Staging IAM Key | IAM Role / Instance Profile | S3 authentication key. |
| `S3_SECRET_ACCESS_KEY` | `string` | Optional | Staging IAM Secret | IAM Role / Instance Profile | S3 authentication secret. |
| `S3_ENDPOINT_URL` | `string (URL)` | Optional | Optional (or Cloudflare R2) | Optional | S3-compatible API endpoint override. |
| `FIREBASE_CREDENTIALS_PATH` | `string (path)` | `./firebase-service-account.json` | N/A | N/A | Local filepath to service account key. |
| `FIREBASE_CREDENTIALS_JSON` | `string (JSON)` | Optional | Raw JSON string | Raw JSON string from Secrets Manager | Inline service account JSON payload. |
| `ALLOWED_ORIGINS` | `comma-separated` | `http://localhost:5173,http://localhost:3000` | `https://staging.predictiq.io` | `https://app.predictiq.io` | Strict CORS allowed origins list. |
| `ML_ARTIFACTS_DIR` | `string (path)` | Empty (default) | Empty (default) | Empty (default) | Override path to production model bundle. |
| `DEFAULT_HOURLY_RATE_USD` | `number` | `75.0` | `75.0` | `75.0` | Default engineering hourly rate. |

---

## 2. Frontend Configuration Variables (`.env`)

The frontend React 19 application compiles environment variables at build time using Vite (`VITE_*` prefix):

| Variable Name | Development | Staging | Production | Description |
|---------------|-------------|---------|------------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | `https://staging-api.predictiq.io/api/v1` | `https://api.predictiq.io/api/v1` | Root API endpoint (must include `/api/v1`). |
| `VITE_APP_ENV` | `development` | `staging` | `production` | Frontend environment identifier. |
| `VITE_FIREBASE_API_KEY` | Dev Firebase Key | Staging Firebase Key | Prod Firebase Key | Firebase web API key. |
| `VITE_FIREBASE_AUTH_DOMAIN` | `dev-predictiq.firebaseapp.com` | `staging-predictiq.firebaseapp.com` | `predictiq.firebaseapp.com` | Firebase authentication domain. |
| `VITE_FIREBASE_PROJECT_ID` | `dev-predictiq` | `staging-predictiq` | `predictiq-prod` | Firebase project identifier. |
| `VITE_FIREBASE_STORAGE_BUCKET`| `dev-predictiq.appspot.com` | `staging-predictiq.appspot.com` | `predictiq-prod.appspot.com` | Firebase storage bucket. |
| `VITE_FIREBASE_MESSAGING_SENDER_ID`| Sender ID | Sender ID | Sender ID | Firebase cloud messaging sender ID. |
| `VITE_FIREBASE_APP_ID` | App ID | App ID | App ID | Firebase web application ID. |

---

## 3. Configuration Validation & Fail-Fast Mechanics

PredictIQ validates all environment variables during application boot in `backend/app/core/config.py` using `pydantic-settings`:

1. **Production Storage Check**: If `APP_ENV` is set to `production` or `staging` while `STORAGE_BACKEND` is set to `local` without `ALLOW_LOCAL_STORAGE_IN_PRODUCTION=true`, the application raises `ValueError` immediately on boot:
   ```python
   if (self.APP_ENV.lower() in ("prod", "production", "staging")
           and self.STORAGE_BACKEND == "local" and not self.ALLOW_LOCAL_STORAGE_IN_PRODUCTION):
       raise ValueError("Production requires S3 storage or explicit durable local storage opt-in")
   ```
2. **S3 Credential Symmetry**: If `STORAGE_BACKEND=s3` and credentials are provided, both `S3_ACCESS_KEY_ID` and `S3_SECRET_ACCESS_KEY` must be populated together.
3. **Database URL Sanity**: In non-test environments, if `DATABASE_URL` contains unconfigured placeholders (e.g. `"your-"`), a critical warning is issued.
4. **Firebase Auth Emulator Safeguard**: If `FIREBASE_AUTH_EMULATOR_HOST` is detected in non-test environments, the server crashes fast to prevent accidental test auth bypass in production.
