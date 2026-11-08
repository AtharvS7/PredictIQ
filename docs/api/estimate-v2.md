Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# PredictIQ Estimation API Specification (v2)

This document specifies the estimation endpoints in PredictIQ:
- `POST /api/v1/estimates/manual` (Parametric manual estimation)
- `POST /api/v1/estimates/analyze` (SRS document parsing + NLP extraction + ML estimation)
- `GET /api/v1/estimates/{estimate_id}` (Retrieve stored full estimate)

All estimation responses adhere strictly to the frozen JSON Schema defined in [`docs/contracts/api_estimate_v2.json`](../contracts/api_estimate_v2.json) and provide calibrated quantile uncertainty bands ($P_{10}, P_{25}, P_{50}, P_{75}, P_{90}$).

---

## 1. Create Estimate (Manual Flow)

Creates a calibrated project estimate directly from user-supplied parameters without requiring document upload.

### HTTP Request

```http
POST /api/v1/estimates/manual HTTP/1.1
Host: api.predictiq.io
Authorization: Bearer <FIREBASE_ID_TOKEN>
Content-Type: application/json
Accept: application/json
```

### Request Payload (`ManualEstimateRequest`)

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `project_name` | string | **Yes** | 1–200 chars | Human-readable name of the project |
| `project_type` | string | No | Default: `"Web App"` | Project domain/platform (e.g., `"Web App"`, `"Mobile App"`, `"Enterprise"`) |
| `team_size` | integer | No | 1–100 (Default: 5) | Planned engineering team headcount |
| `duration_months` | number | No | 1–60 (Default: 6.0) | Target project timeline in calendar months |
| `complexity` | string | No | Enum: `["Low", "Medium", "High", "Very High"]` | Subjective domain complexity |
| `methodology` | string | No | Enum: `["Agile", "Waterfall", "Hybrid"]` | Development lifecycle methodology |
| `hourly_rate_usd` | number | No | 10.0–500.0 (Default: 75.0) | Blended engineering hourly billing rate in USD |
| `tech_stack` | array[string]| No | Max 50 items | List of technologies (e.g. `["React", "FastAPI", "PostgreSQL"]`) |
| `integration_count`| integer | No | 0–15 (Default: 2) | Number of external API/system integrations |
| `volatility_score` | integer | No | 1–5 (Default: 3) | Requirement stability score (1=stable, 5=high volatility) |
| `team_experience` | number | No | 1.0–4.0 (Default: 2.0) | Team seniority index (1=junior, 4=principal/expert) |

#### Example Request Body

```json
{
  "project_name": "PredictIQ Web Platform",
  "project_type": "Web App",
  "team_size": 5,
  "duration_months": 8.0,
  "complexity": "Medium",
  "methodology": "Agile",
  "hourly_rate_usd": 75.0,
  "tech_stack": ["FastAPI", "React", "PostgreSQL"],
  "integration_count": 2,
  "volatility_score": 3,
  "team_experience": 2.0
}
```

---

## 2. Create Estimate from Document Analysis

Extracts project scope, entities, user stories, and complexity factors from an uploaded SRS document and computes predictions.

### HTTP Request

```http
POST /api/v1/estimates/analyze HTTP/1.1
Host: api.predictiq.io
Authorization: Bearer <FIREBASE_ID_TOKEN>
Content-Type: application/json
Accept: application/json
```

### Request Payload (`EstimateRequest`)

```json
{
  "document_id": "890787cb-15ba-411a-ab9a-ae18e77c86a0",
  "overrides": {
    "project_name": "Enterprise Claims Portal",
    "hourly_rate_usd": 85.0,
    "team_size": 6
  }
}
```

---

## 3. Real Captured Response Payload

The following JSON payload was captured directly from live inference execution on the Python 3.12 codebase (`cdca041`) conforming to `api_estimate_v2.json`:

```json
{
  "estimate_id": "9f2d1e8c-8974-4b53-bc2a-1721590ab8e1",
  "document_id": null,
  "user_id": "usr_99812480214a",
  "project_name": "PredictIQ Web Platform",
  "created_at": "2026-11-08T12:14:12.849735Z",
  "version": 1,
  "status": "complete",
  "inputs": {
    "project_type": "Web App",
    "tech_stack": [
      "FastAPI",
      "React",
      "PostgreSQL"
    ],
    "team_size": 5,
    "duration_months": 8.0,
    "complexity": "Medium",
    "methodology": "Agile",
    "hourly_rate_usd": 75.0,
    "feature_count": 10,
    "integration_count": 2,
    "volatility_score": 3,
    "team_experience": 2.0,
    "size_fp": 185.0
  },
  "outputs": {
    "effort_min_hours": 698.7,
    "effort_likely_hours": 1817.8,
    "effort_max_hours": 4729.4,
    "effort_p25_hours": 997.8,
    "effort_p75_hours": 3312.0,
    "cost_min_usd": 52402.5,
    "cost_likely_usd": 136335.0,
    "cost_max_usd": 354705.0,
    "cost_p25_usd": 74835.0,
    "cost_p75_usd": 248400.0,
    "timeline_min_weeks": 26.0,
    "timeline_likely_weeks": 34.6,
    "timeline_max_weeks": 48.5,
    "confidence_pct": 80.0,
    "risk_score": 28.5,
    "risk_level": "Low",
    "top_risks": [
      {
        "name": "Integration Complexity",
        "description": "2 third-party integrations require clear interface contracts.",
        "severity": "Low"
      }
    ],
    "phase_breakdown": [
      {
        "phase": "Discovery & Requirements",
        "effort_hours": 181.8,
        "cost_usd": 13633.5,
        "duration_weeks": 3.5,
        "pct_of_total": 0.10
      },
      {
        "phase": "UI/UX Design",
        "effort_hours": 218.1,
        "cost_usd": 16360.2,
        "duration_weeks": 4.2,
        "pct_of_total": 0.12
      },
      {
        "phase": "Backend Development",
        "effort_hours": 545.3,
        "cost_usd": 40900.5,
        "duration_weeks": 10.4,
        "pct_of_total": 0.30
      },
      {
        "phase": "Frontend Development",
        "effort_hours": 399.9,
        "cost_usd": 29993.7,
        "duration_weeks": 7.6,
        "pct_of_total": 0.22
      },
      {
        "phase": "QA & Testing",
        "effort_hours": 327.2,
        "cost_usd": 24540.3,
        "duration_weeks": 6.2,
        "pct_of_total": 0.18
      },
      {
        "phase": "Deployment & DevOps",
        "effort_hours": 145.4,
        "cost_usd": 10906.8,
        "duration_weeks": 2.8,
        "pct_of_total": 0.08
      }
    ],
    "model_explanation": "Predicted using MultivariateMonotoneModel fitted with size elasticity b=0.8270. Effort quantiles calibrated using Mondrian split-conformal inference across historical software projects.",
    "benchmark_comparison": "Project size of 185.0 FP falls in the 52nd percentile of enterprise web applications.",
    "data_quality_tier": "A",
    "ood_flags": [],
    "org_calibration": {
      "applied": false,
      "k_actuals": 0,
      "shrinkage_weight": 0.0,
      "multiplier": 1.0
    },
    "effort_hours": {
      "p10": 698.7,
      "p25": 997.8,
      "p50": 1817.8,
      "p75": 3312.0,
      "p90": 4729.4
    },
    "person_months": {
      "p10": 4.6,
      "p25": 6.56,
      "p50": 11.96,
      "p75": 21.79,
      "p90": 31.11
    }
  },
  "model_version": "2.0.0-rc.1"
}
```

---

## 4. Canonical Contract Export Format (`api_estimate_v2.json`)

When exported via the frontend or via `/api/v1/estimates/{id}/export/json`, the response conforms directly to the verified canonical schema:

```json
{
  "estimate_id": "9f2d1e8c-8974-4b53-bc2a-1721590ab8e1",
  "project_name": "PredictIQ Web Platform",
  "effort_hours": {
    "p10": 698.7,
    "p25": 997.8,
    "p50": 1817.8,
    "p75": 3312.0,
    "p90": 4729.4
  },
  "person_months": {
    "p10": 4.60,
    "p25": 6.56,
    "p50": 11.96,
    "p75": 21.79,
    "p90": 31.11
  },
  "cost": {
    "p10": 52402.50,
    "p25": 74835.00,
    "p50": 136335.00,
    "p75": 248400.00,
    "p90": 354705.00,
    "currency": "USD",
    "rate": 75.00
  },
  "size": {
    "value": 185.0,
    "source": "user",
    "uncertainty": {
      "p10": 185.0,
      "p50": 185.0,
      "p90": 185.0
    }
  },
  "drivers": [
    {
      "name": "Functional Size",
      "impact": "major_increase",
      "description": "185 estimated Function Points derived from user parameters."
    },
    {
      "name": "Integration Density",
      "impact": "moderate_increase",
      "description": "2 external system integrations."
    }
  ],
  "assumptions": [
    {
      "category": "Effort Conversion",
      "description": "152 productive working hours per person-month.",
      "editable": false
    },
    {
      "category": "Hourly Rate",
      "description": "Blended engineering rate of $75/hour.",
      "editable": true
    }
  ],
  "data_quality_tier": "A",
  "ood_flags": [],
  "nominal_interval_coverage": 0.80,
  "confidence_pct": 80.0,
  "org_calibration": {
    "applied": false,
    "k_actuals": 0,
    "shrinkage_weight": 0.0,
    "multiplier": 1.0
  },
  "model": {
    "version": "2.0.0-rc.1",
    "sha256": "c8f746b8c006028faec9e1dfefab8f17b22b065e8ea45aa77cb971a098dda644",
    "model_sha256": "b3af00831805e5655a9a941198b1608efb222f94c3d8a977bef8eb0c15791873",
    "dataset_sha256": "b05ad3b0111d4ed3ff89b7aa2a0f653e494f81953c701916f27756d1746eede3",
    "trained_on_rows": 915,
    "sources": [
      "china",
      "desharnais",
      "kitchenham",
      "maxwell",
      "albrecht",
      "att_aptness"
    ],
    "metrics_ref": "docs/MODEL_VALIDATION_SUMMARY.md"
  }
}
```

---

## 5. Retrieve Stored Estimate

Fetches a previously computed estimate by its UUID.

### HTTP Request

```http
GET /api/v1/estimates/{estimate_id} HTTP/1.1
Host: api.predictiq.io
Authorization: Bearer <FIREBASE_ID_TOKEN>
Accept: application/json
```

### Path Parameters

- `estimate_id` (UUIDv4, required): Unique identifier of the estimate.

### Security Invariants

- Access is strictly constrained by tenant ownership: callers can only retrieve estimates matching their authenticated `user_id` unless the caller possesses the `admin` role.
- Soft-deleted estimates (`status = 'deleted'`) return `404 Not Found`.
- Malformed UUID strings fail validation before hitting the database, returning `422 Unprocessable Entity`.
