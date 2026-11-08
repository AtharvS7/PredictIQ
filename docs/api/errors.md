Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# PredictIQ API Error Handling & Status Codes

PredictIQ uses standard HTTP response codes to indicate the outcome of API requests. Error responses return structured JSON payloads accompanied by a unique `X-Request-ID` header for end-to-end tracing and auditing.

---

## 1. Error Payload Format

PredictIQ standardizes on FastAPI/Starlette compliant error payloads. Two standard payload shapes are returned depending on the error type:

### Standard Error Response (`HTTPException`)

```json
{
  "detail": "Estimate not found"
}
```

### Validation Error Response (`422 Unprocessable Entity`)

When input validation fails via Pydantic or FastAPI query/path parsing, `detail` contains an array of specific field failure objects:

```json
{
  "detail": [
    {
      "loc": ["body", "hourly_rate_usd"],
      "msg": "Input should be greater than or equal to 10",
      "type": "greater_than_equal",
      "ctx": {
        "ge": 10.0
      }
    }
  ]
}
```

- `loc`: Path to the invalid field (`["body", "field_name"]` or `["path", "estimate_id"]`).
- `msg`: Human-readable description of why validation failed.
- `type`: Machine-readable error code.
- `ctx`: Context parameters associated with the constraint violation.

---

## 2. HTTP Status Codes Reference

### 400 Bad Request

Indicates that the request was structurally valid JSON but violates domain logic rules.

**Common Scenarios:**
- Updating a user profile with no recognized allowlisted columns (`"No valid fields to update"`).
- Providing an invalid export target format (`"Invalid format"`).
- Supplying contradictory parameter sets.

**Example Response:**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json
X-Request-ID: e12b9a10-23a1-432d-9bc7-60fce7c01b90

{
  "detail": "No valid fields to update"
}
```

---

### 401 Unauthorized

Indicates missing, expired, revoked, or cryptographically invalid authentication credentials.

**Common Scenarios:**
- Missing `Authorization` header on protected endpoints.
- Expired Firebase ID token (default TTL is 1 hour).
- Token signature check failed against Google public certificates.
- Token revoked via Firebase Admin SDK.

**Example Response:**
```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer
Content-Type: application/json
X-Request-ID: 3a9e1022-811c-42b7-a352-87063bdf9114

{
  "detail": "Invalid authentication credentials"
}
```

---

### 403 Forbidden

Indicates the client is authenticated, but does not possess the requisite Role-Based Access Control (RBAC) permission to perform the action.

**Common Scenarios:**
- A user with role `viewer` attempts to call `POST /api/v1/estimates/analyze` (requires `editor` role).
- A non-admin user attempts to access `/api/v1/admin/actuals/export` (requires `admin` role).
- A user attempts to submit actuals or modify an estimate owned by another user without administrative delegation (`"Not authorized to submit actuals for this estimate"`).

**Example Response:**
```http
HTTP/1.1 403 Forbidden
Content-Type: application/json
X-Request-ID: c53db199-6379-4d6f-96a2-cb3e77864aa9

{
  "detail": "Operation not permitted: requires editor role"
}
```

---

### 404 Not Found

Indicates that the requested resource does not exist, has been soft-deleted, or belongs to another user tenant and is inaccessible.

**Common Scenarios:**
- Estimate ID not found in database or marked with `status = 'deleted'`.
- Document upload ID does not exist or does not belong to the calling user.
- User profile record has not yet been initialized.

**Example Response:**
```http
HTTP/1.1 404 Not Found
Content-Type: application/json
X-Request-ID: d4209bb7-4f68-45a2-a9b0-9fbb34e1572c

{
  "detail": "Estimate not found"
}
```

---

### 422 Unprocessable Entity

Raised when request parameters fail structural validation constraints. Importantly, PredictIQ validates path and query parameters before invoking database operations to prevent resource exhaustion and SQL injection vectors.

**Common Scenarios:**
- Passing a non-UUID string to `/api/v1/estimates/{estimate_id}`.
- Project name exceeding 200 characters or containing empty whitespace.
- Hourly rate outside the permitted range [10.0, 500.0] USD.
- Team size below 1 or exceeding 100 engineers.
- Missing required fields in POST requests.

**Example Response (Malformed Path UUID):**
```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
X-Request-ID: b8026194-e354-469b-8321-754d90e29b18

{
  "detail": [
    {
      "loc": ["path", "estimate_id"],
      "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `n` at 1",
      "type": "uuid_parsing"
    }
  ]
}
```

---

### 429 Too Many Requests

Enforced by the `SlowAPI` rate limiting layer when request limits are exceeded.

**Example Response:**
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 3600
X-Request-ID: 7b841a12-6804-48f8-b391-f925b481977d

{
  "error": "Rate limit exceeded: 10 per 1 hour"
}
```

---

### 503 Service Unavailable

Indicates that the service is temporarily unable to handle the request due to external dependency failures or fail-closed security gates.

**Common Scenarios:**
- **Database Connection Failure**: Neon PostgreSQL connection pool saturated or unreachable.
- **Fail-Closed ML Artifact Verification**: Production model SHA-256 mismatch, corrupted `manifest.json`, missing `model_params.json`, or detected revoked checksum (`REVOKED_MODEL_SHA256`).
- **Authorization Service Degradation**: Unable to verify managed roles in `profiles` table.

**Example Response (Tampered or Unavailable ML Model):**
```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
X-Request-ID: fa908711-b1e0-4965-a864-1c2069fae412

{
  "detail": "Prediction service is unavailable: ML artifacts failed verification"
}
```

---

## 3. Request Correlation & Observability

Every request received by the API gateway is assigned a unique UUIDv4 `X-Request-ID`.
- If the incoming client request provides an `X-Request-ID` header, that value is validated and attached to the request state.
- If omitted, the server generates a new UUIDv4.
- All log events generated during the request lifecycle in `structlog` include `request_id`.
- The `X-Request-ID` is echoed back in the response headers of both successful and error responses.

When filing bug reports or investigating 5xx errors, provide the `X-Request-ID` value from the response headers to locate the corresponding execution trace in CloudWatch or backend logs.
