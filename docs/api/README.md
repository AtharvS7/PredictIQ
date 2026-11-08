Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# PredictIQ REST API Overview

PredictIQ exposes a high-performance, asynchronous REST API built with FastAPI and Python 3.12, providing probabilistic software project effort, cost, and timeline predictions backed by conformal prediction and empirical Bayes calibration.

---

## 1. Architectural Architecture & Base URLs

The API server operates asynchronously on top of Uvicorn/FastAPI with asyncpg connecting to Neon Serverless PostgreSQL and AWS S3/Cloudflare R2 for durable document storage.

| Environment | Base URL | Protocol | Documentation |
|-------------|----------|----------|---------------|
| **Local Development** | `http://localhost:8000/api/v1` | HTTP/1.1 | `http://localhost:8000/docs` |
| **Staging** | `https://staging-api.predictiq.io/api/v1` | HTTPS (TLS 1.3) | `https://staging-api.predictiq.io/docs` |
| **Production** | `https://api.predictiq.io/api/v1` | HTTPS (TLS 1.3) | Restricted / Enterprise |

All API endpoints reside beneath the `/api/v1` prefix. System health probes (`/api/v1/live`, `/api/v1/health`, `/api/v1/ready`) and root API discovery (`/`) are available at top level.

---

## 2. Authentication & Authorization

All stateful and estimation endpoints require token-based authentication via Firebase Identity Platform ID tokens passed via standard HTTP Bearer headers.

### Request Headers

```http
GET /api/v1/estimates HTTP/1.1
Host: api.predictiq.io
Authorization: Bearer <FIREBASE_ID_TOKEN>
X-Request-ID: c8b31a89-d971-4a1e-8bc2-a1b72e519280
Content-Type: application/json
Accept: application/json
```

- **`Authorization`**: Required for all protected routes. Must contain `Bearer <token>`. The backend validates token signatures against Google's public key sets, validates audience and issuer, and checks for revocation.
- **`X-Request-ID`**: Optional client request correlation ID (UUIDv4). If omitted, the API gateway automatically generates and injects one into both the request context and the response headers (`expose_headers: ["X-Request-ID"]`).
- **`Content-Type`**: Must be `application/json` for JSON request bodies, or `multipart/form-data` for document file uploads.

### Role Hierarchy & Permissions

PredictIQ implements Role-Based Access Control (RBAC):
- **`admin`**: Full tenant administrative control, including user role management and consented data flywheel export.
- **`editor`** (Estimator): Can create, update, delete, duplicate, share estimates, manage budgets, and submit project actuals.
- **`viewer`**: Read-only access to view authorized estimates, profiles, and export PDF/JSON reports.

---

## 3. Rate Limiting Policy

Rate limiting is enforced via `SlowAPI` with in-memory or Redis backends to protect the engine against abuse, brute-force attacks, and denial-of-service attempts.

| Endpoint Category | Default Limit | Strategy / Key | Headers Returned |
|-------------------|---------------|----------------|------------------|
| **Estimation Analysis** (`/estimates/analyze`, `/estimates/manual`) | 60 requests / minute | Authenticated User ID (`CurrentUser.id`) | `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` |
| **Share Link Generation** (`/estimates/{id}/share`) | 10 requests / hour | User ID & IP address | `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` |
| **Document Uploads** (`/documents/upload`, `/upload-file`) | 30 requests / minute | User ID & IP address | Standard HTTP 429 when exceeded |
| **Public Shared Views** (`/shared/{token}`) | 120 requests / minute | Remote Client IP address | Standard HTTP 429 when exceeded |
| **Health Probes** (`/live`, `/health`, `/ready`) | Unthrottled | Infrastructure bypass | None |

When rate limits are exceeded, the API responds with HTTP 429 Too Many Requests:
```json
{
  "error": "Rate limit exceeded: 10 per 1 hour"
}
```

---

## 4. Cross-Origin Resource Sharing (CORS)

CORS is strictly configured via FastAPI `CORSMiddleware` using explicit allowed origins specified in the `ALLOWED_ORIGINS` environment variable:
- **Allowed Methods**: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`
- **Allowed Headers**: `Authorization`, `Content-Type`, `Accept`, `X-Request-ID`, `X-Requested-With`
- **Exposed Headers**: `X-Request-ID`
- **Credentials**: Enabled (`allow_credentials=True`)

Wildcard (`*`) origins are strictly prohibited in production and staging environments.

---

## 5. Security & Response Headers

Every HTTP response from the PredictIQ API includes hardened security headers conforming to OWASP best practices:

```http
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer
Permissions-Policy: camera=(), microphone=(), geolocation=()
X-XSS-Protection: 1; mode=block
X-Request-ID: 7a8dfb02-5819-4841-860f-2e9fcf0f0119
```

Shared link read-only endpoints additionally include `Cache-Control: no-store` to prevent caching of shared estimate data on shared proxy intermediaries.

---

## 6. Endpoints Index

| Method | Endpoint | Minimum Role | Summary |
|--------|----------|--------------|---------|
| `GET` | `/live` | Public | Process liveness probe |
| `GET` | `/health` | Public | Service health & model status |
| `GET` | `/ready` | Public | Kubernetes/ECS readiness check |
| `POST` | `/estimates/analyze` | `editor` | Full pipeline: Document NLP + ML estimation |
| `POST` | `/estimates/manual` | `editor` | Parametric manual estimation |
| `GET` | `/estimates` | `viewer` | Paginated list of user estimates |
| `GET` | `/estimates/{id}` | `viewer` | Fetch single full estimate |
| `POST` | `/estimates/{id}/duplicate` | `editor` | Duplicate estimate as new revision |
| `DELETE` | `/estimates/{id}` | `editor` | Soft-delete an estimate |
| `POST` | `/estimates/{id}/share` | `editor` | Generate password-protectable share token |
| `GET` | `/estimates/{id}/export/pdf` | `viewer` | Export branded multi-currency PDF report |
| `GET` | `/estimates/{id}/export/json` | `viewer` | Export raw contract JSON |
| `POST` | `/estimates/{id}/actuals` | `editor` | Submit project completion actuals with training consent |
| `POST` | `/documents/upload-file` | `editor` | Upload SRS document (.pdf, .docx, .txt, .md) |
| `GET` | `/profile` | `viewer` | Retrieve user profile & defaults |
| `PATCH` | `/profile` | `editor` | Update profile settings |
| `GET` | `/admin/actuals/export` | `admin` | Export consented flywheel data for model training |
