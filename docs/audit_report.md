# Predictify — v3.1.0 Industry-Grade Audit Report

> **Date:** April 29, 2026 | **Auditor:** Antigravity AI | **Scope:** Full Codebase Audit — Industry Deployment Readiness

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. Project Metrics](#2-project-metrics)
- [3. Architecture Review](#3-architecture-review)
- [4. Security Audit](#4-security-audit)
- [5. Code Quality Audit](#5-code-quality-audit)
- [6. Test Coverage Audit](#6-test-coverage-audit)
- [7. DevOps & Infrastructure](#7-devops--infrastructure)
- [8. Frontend Audit](#8-frontend-audit)
- [9. ML Pipeline Audit](#9-ml-pipeline-audit)
- [10. Industry Comparison & Gap Analysis](#10-industry-comparison--gap-analysis)
- [11. Deployment Readiness Score](#11-deployment-readiness-score)
- [12. Next-Semester Roadmap](#12-next-semester-roadmap)

---

## 1. Executive Summary

Predictify is an AI-powered SaaS tool that estimates software project cost and timeline from uploaded documents. It combines NLP extraction, IFPUG function points, and ML prediction (RandomForest) into a single pipeline.

**Overall Deployment Readiness: 62% — NOT ready for production client deployment.**

The core estimation pipeline works well and the architecture is sound, but critical gaps in security hardening, test coverage, observability, and containerization must be addressed before pitching to enterprise clients.

| Category | Score | Industry Target | Status |
|----------|:-----:|:---------------:|:------:|
| Security | 55% | 90%+ | 🔴 |
| Test Coverage | 48% | 80%+ | 🔴 |
| Code Quality | 78% | 85%+ | 🟡 |
| DevOps/CI/CD | 45% | 85%+ | 🔴 |
| Frontend | 70% | 80%+ | 🟡 |
| ML Pipeline | 65% | 80%+ | 🟡 |
| Documentation | 85% | 75%+ | 🟢 |
| **Overall** | **62%** | **80%+** | 🔴 |

---

## 2. Project Metrics

| Metric | Value |
|--------|:-----:|
| Total LOC (code + docs) | 15,879 |
| Backend Python LOC | 3,801 |
| ML Pipeline LOC | 1,039 |
| Test LOC | 1,016 |
| Frontend TSX/TS/CSS LOC | 5,350 |
| Documentation LOC | 2,071 |
| Backend test count | 111 (106 pass, 5 fail) |
| Frontend test count | 0 |
| API endpoints | 14 |
| Database tables | 4 |
| CI/CD workflows | 5 |

---

## 3. Architecture Review

### 3.1 Current Stack

| Layer | Technology | Industry Standard |
|-------|-----------|:-----------------:|
| Frontend | React 19 + Vite 8 + Zustand | ✅ |
| Backend | FastAPI 0.135 + Python 3.13 | ✅ |
| Database | Neon PostgreSQL (asyncpg) | ✅ |
| Auth | Firebase Auth + Admin SDK | ✅ |
| ML | scikit-learn (RandomForest) | 🟡 |
| File Storage | BYTEA in PostgreSQL | 🔴 |

### 3.2 Architecture Issues Found

| # | Severity | Issue | Impact |
|---|:--------:|-------|--------|
| A1 | **CRITICAL** | Files stored as BYTEA in PostgreSQL | DB bloat, slow queries, no CDN caching. Industry uses S3/GCS/R2 object storage |
| A2 | **HIGH** | No database migration tool (Alembic/Flyway) | Only 1 raw SQL file; no versioned migrations, no rollback capability |
| A3 | **HIGH** | No ORM layer | Raw SQL strings throughout API routes; error-prone, hard to maintain |
| A4 | **MEDIUM** | Monolithic backend | All services in single process; no background task queue (Celery/RQ) for NLP/ML |
| A5 | **MEDIUM** | Connection pool (2-10) hardcoded | Should be configurable via env vars for different deployment tiers |
| A6 | **LOW** | No API versioning strategy | Routes under `/api/v1` but no deprecation or v2 plan |

---

## 4. Security Audit

### 4.1 Findings Summary

| Check | Status | Notes |
|-------|:------:|-------|
| Hardcoded secrets in source | ✅ CLEAN | 1 test file has mock token (acceptable) |
| `.env` files tracked by Git | ✅ CLEAN | Properly gitignored |
| Firebase token verification | ✅ GOOD | Proper Admin SDK verification with expiry/revocation checks |
| CORS configuration | ✅ GOOD | Configurable via env var |
| File upload validation | ✅ GOOD | 10MB limit + MIME whitelist |
| Rate limiting | ✅ PRESENT | slowapi at 200/min global |
| Request ID tracing | ✅ GOOD | X-Request-ID on every response |

### 4.2 Critical Security Gaps

| # | Severity | Gap | Industry Standard | Fix |
|---|:--------:|-----|-------------------|-----|
| S1 | **CRITICAL** | SQL injection risk in `profile.py` | Parameterized queries only | Dynamic column names from `model_dump()` keys are interpolated into f-strings. Although keys come from Pydantic (not user input), this pattern is dangerous and would fail any security audit. Use an allowlist of column names |
| S2 | **CRITICAL** | SQL injection risk in `estimates.py` sort | Parameterized queries only | `order_clause` uses f-string interpolation in SQL. The `sort_map` whitelist mitigates this, but the pattern is flagged by SAST tools |
| S3 | **HIGH** | No RBAC (Role-Based Access Control) | Admin/User/Viewer roles | Only "authenticated" role exists; no admin panel, no org-level permissions |
| S4 | **HIGH** | No input sanitization on `project_name` | XSS prevention on stored data | User-supplied `project_name` stored and rendered without sanitization |
| S5 | **HIGH** | Share links have no rate limiting | Brute-force protection | Token is 32-byte urlsafe but no lockout after failed attempts |
| S6 | **HIGH** | No audit logging | SOC 2 compliance | No record of who accessed what data and when |
| S7 | **MEDIUM** | CORS allows all methods/headers | Restrict to needed methods | `allow_methods=["*"], allow_headers=["*"]` is too permissive |
| S8 | **MEDIUM** | No CSP/security headers | OWASP Top 10 | Missing Content-Security-Policy, X-Frame-Options, HSTS |
| S9 | **MEDIUM** | No request body size limit (global) | Prevent DoS | Only file upload has size limit; JSON payloads unlimited |
| S10 | **MEDIUM** | CI uses stale Supabase secrets | Clean CI config | `ci.yml` still references `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `JWT_SECRET` |
| S11 | **LOW** | Database URL logged (first 40 chars) | Never log credentials | `database.py:24` logs DSN prefix which may contain username |

### 4.3 OWASP Top 10 Compliance

| OWASP Category | Status | Notes |
|---------------|:------:|-------|
| A01 Broken Access Control | 🟡 | User isolation works but no RBAC |
| A02 Cryptographic Failures | ✅ | bcrypt for share passwords, Firebase for auth |
| A03 Injection | 🔴 | SQL f-string patterns in profile.py and estimates.py |
| A04 Insecure Design | 🟡 | No threat model documented |
| A05 Security Misconfiguration | 🟡 | Permissive CORS, no security headers |
| A06 Vulnerable Components | 🟡 | Pydantic v2 deprecation warning; stale deps in lock file (gotrue, supabase remnants) |
| A07 Auth Failures | ✅ | Firebase Admin SDK is industry-grade |
| A08 Data Integrity | ✅ | Token verification on all protected routes |
| A09 Logging Failures | 🔴 | No audit trail, no structured error alerting |
| A10 SSRF | ✅ | No outbound URL fetching from user input |

---

## 5. Code Quality Audit

### 5.1 Backend Quality

| Check | Status | Notes |
|-------|:------:|-------|
| Type hints on public functions | ✅ | Consistent |
| Docstrings on public functions | ✅ | All services documented |
| Structured logging (structlog) | ✅ | 43 logging calls |
| Error handling in API routes | ✅ | 65 error handlers |
| Pydantic models for I/O | ✅ | All schemas in models/ |
| No circular imports | ✅ | Clean dependency graph |
| Environment-based config | ✅ | Pydantic BaseSettings |
| Async endpoints | ✅ | All routes async |

### 5.2 Code Smells Found

| # | Severity | Issue | Location | Fix |
|---|:--------:|-------|----------|-----|
| Q1 | **HIGH** | Pydantic v2 `class Config` deprecated | `config.py:49` | Use `model_config = ConfigDict(...)` — will break in Pydantic v3 |
| Q2 | **HIGH** | 5 broken tests (currency async) | `test_currencies.py` | `asyncio.get_event_loop()` removed in Python 3.14; use `asyncio.run()` |
| Q3 | **MEDIUM** | `estimates.py` is 619 lines | `api/v1/estimates.py` | Extract `_run_estimation` to a service class; too much business logic in route handler |
| Q4 | **MEDIUM** | Stale Supabase dependencies in requirements | `requirements.lock.txt` | `gotrue`, `supabase`, `storage3` still present — remove dead deps |
| Q5 | **MEDIUM** | No connection retry/backoff on DB | `database.py` | `asyncpg.create_pool()` with no retry; production needs exponential backoff |
| Q6 | **LOW** | `export.py:108` deletes dict keys during iteration | `export.py` | `del result_dict[key]` while iterating — use comprehension instead |
| Q7 | **LOW** | Magic numbers in ML service | `ml_service.py` | `0.85`, `0.30`, `0.04` — extract to named constants |

---

## 6. Test Coverage Audit

### 6.1 Current Coverage

| Service | Test File | Tests | Pass | Fail |
|---------|----------|:-----:|:----:|:----:|
| NLP Extractor | `test_nlp_extractor.py` | 35 | 35 | 0 |
| Cost Calculator | `test_cost_calculator.py` | 18 | 18 | 0 |
| ML Service | `test_ml_service.py` | 11 | 11 | 0 |
| Inference | `test_inference.py` | 12 | 12 | 0 |
| Risk Analyzer | `test_risk_analyzer.py` | 10 | 10 | 0 |
| Document Parser | `test_document_parser.py` | 8 | 8 | 0 |
| Currencies | `test_currencies.py` | 7 | 2 | **5** |
| Health | `test_health.py` | 5 | 5 | 0 |
| Benchmark | `test_benchmark.py` | 5 | 5 | 0 |
| **Total** | | **111** | **106** | **5** |

### 6.2 Industry Coverage Gaps

| Area | Current | Industry Standard | Gap |
|------|:-------:|:-----------------:|:---:|
| Backend unit tests | 111 | 200+ for this codebase | 🔴 |
| API integration tests | **0** | Full route coverage | 🔴 CRITICAL |
| Frontend component tests | **0** | 70%+ component coverage | 🔴 CRITICAL |
| E2E tests | **0** | Core flows covered | 🔴 CRITICAL |
| Export service tests | **0** | PDF/CSV generation | 🔴 |
| Auth flow tests | **0** | Login/logout/token refresh | 🔴 |
| Load/performance tests | **0** | Response time SLAs | 🟡 |
| Test-to-code ratio | 0.21:1 | 0.8:1+ | 🔴 |

**Industry benchmark:** Enterprise SaaS requires 80%+ code coverage. Current estimated coverage is ~35-40%.

---

## 7. DevOps & Infrastructure

### 7.1 CI/CD Pipeline

| Workflow | Purpose | Status |
|----------|---------|:------:|
| `ci.yml` | Lint + Test + Security | 🟡 Has stale Supabase env vars |
| `cd-staging.yml` | Deploy to staging | ❓ Not verified |
| `cd-production.yml` | Deploy to prod | ❓ Not verified |
| `codeql.yml` | GitHub CodeQL scan | ✅ |
| `security-weekly.yml` | Weekly security scan | ✅ |

### 7.2 Infrastructure Gaps

| # | Severity | Gap | Industry Standard |
|---|:--------:|-----|-------------------|
| D1 | **CRITICAL** | No Dockerfile for backend | Every SaaS needs containerized deployment |
| D2 | **CRITICAL** | No health check endpoint for DB/Firebase | Load balancers need `/health` with dependency checks |
| D3 | **CRITICAL** | No monitoring/alerting (APM) | Datadog/Sentry/New Relic for production |
| D4 | **HIGH** | No structured error reporting | Sentry/Bugsnag for exception tracking |
| D5 | **HIGH** | No log aggregation | ELK/CloudWatch/Loki for centralized logs |
| D6 | **HIGH** | No backup strategy for Neon DB | Point-in-time recovery, daily snapshots |
| D7 | **HIGH** | `docker-compose.yml` exists but no individual Dockerfiles | `Dockerfile.backend` and `Dockerfile.frontend` referenced in CI but missing |
| D8 | **MEDIUM** | No environment promotion pipeline | dev → staging → prod with gates |
| D9 | **MEDIUM** | No secrets rotation policy | Firebase/DB credentials should rotate quarterly |
| D10 | **LOW** | No auto-scaling configuration | Kubernetes HPA or Railway auto-scale |

---

## 8. Frontend Audit

### 8.1 Strengths

| Feature | Status |
|---------|:------:|
| Code splitting (lazy routes) | ✅ |
| Error boundary | ✅ |
| Auth guard (RequireAuth) | ✅ |
| Theme support (dark/light/system) | ✅ |
| Toast notifications | ✅ |
| Loading states | ✅ (29 patterns) |
| Zustand state management | ✅ |
| TypeScript strict (0 errors) | ✅ |
| No XSS (`dangerouslySetInnerHTML`) | ✅ |
| Form validation (react-hook-form + zod) | ✅ |

### 8.2 Frontend Gaps

| # | Severity | Gap | Industry Standard |
|---|:--------:|-----|-------------------|
| F1 | **HIGH** | Zero frontend tests | Jest + React Testing Library minimum |
| F2 | **HIGH** | Only 6 ARIA attributes total | WCAG 2.1 AA compliance for enterprise |
| F3 | **HIGH** | No i18n/localization | Multi-language support for international clients |
| F4 | **MEDIUM** | No Storybook component library | Design system documentation |
| F5 | **MEDIUM** | No PWA support | Offline capability, installability |
| F6 | **MEDIUM** | No SEO meta tags on pages | Only index.html has meta; SPA needs react-helmet |
| F7 | **LOW** | Duplicate chart libraries | Both `recharts` and `chart.js`/`react-chartjs-2` in deps |
| F8 | **LOW** | No bundle size analysis | `vite-plugin-visualizer` for tree-shaking audit |

---

## 9. ML Pipeline Audit

### 9.1 Current State

| Aspect | Status | Notes |
|--------|:------:|-------|
| Model type | RandomForest | Trained on 740 records |
| Feature vector | 27 features | Well-documented T-factor mapping |
| PERT estimation | ✅ | Min/Likely/Max bounds |
| Fallback mode | ✅ | Heuristic when model unavailable |
| Model explainability | ✅ | Feature importance available |

### 9.2 ML Gaps vs. Industry

| # | Severity | Gap | Industry Standard |
|---|:--------:|-----|-------------------|
| M1 | **CRITICAL** | Training dataset only 740 records | ISBSG has 8,000+; need 2,000+ minimum for production |
| M2 | **CRITICAL** | No model versioning/registry | MLflow/Weights&Biases for model lifecycle |
| M3 | **HIGH** | No model monitoring/drift detection | Track prediction accuracy over time |
| M4 | **HIGH** | No A/B testing framework | Compare model versions in production |
| M5 | **HIGH** | `.pkl` files not in Git LFS | Binary artifacts should use LFS or artifact registry |
| M6 | **HIGH** | No automated retraining pipeline | CI/CD for model retraining on new data |
| M7 | **MEDIUM** | Single model (no ensemble) | Ensemble of RF + XGBoost + Ridge improves generalization |
| M8 | **MEDIUM** | No user feedback loop | "Was this estimate accurate?" → retraining data |
| M9 | **LOW** | No confidence calibration | Platt scaling for calibrated probability outputs |

---

## 10. Industry Comparison & Gap Analysis

### 10.1 Competitive Landscape

| Feature | Predictify v3.1 | COCOMO II | FP Workbench | Jira Plugins | ProjectCodeMeter |
|---------|:---------------:|:---------:|:------------:|:------------:|:----------------:|
| ML prediction | ✅ | ❌ | ❌ | ❌ | ❌ |
| NLP doc extraction | ✅ | ❌ | ❌ | ❌ | ❌ |
| IFPUG FP | ✅ Auto | ❌ | ✅ Manual | ❌ | ❌ |
| Risk analysis | ✅ 10 factors | ❌ | ❌ | ❌ | ❌ |
| Multi-currency | ✅ | ❌ | ❌ | Partial | ❌ |
| PDF export | ✅ | ❌ | ✅ | ✅ | ✅ |
| Open source | ✅ | Partial | ❌ | ❌ | ❌ |
| RBAC | ❌ | N/A | ✅ | ✅ | ✅ |
| SOC 2 ready | ❌ | N/A | ❌ | ✅ | ❌ |
| SSO/SAML | ❌ | N/A | ❌ | ✅ | ❌ |

### 10.2 What Enterprise Clients Expect (vs. Current State)

| Requirement | Current | Required | Priority |
|------------|:-------:|:--------:|:--------:|
| SOC 2 Type II compliance | ❌ | ✅ | P0 |
| SSO (SAML/OIDC) | ❌ | ✅ | P0 |
| RBAC with org management | ❌ | ✅ | P0 |
| 99.9% uptime SLA | ❌ | ✅ | P0 |
| Data residency controls | ❌ | ✅ | P1 |
| Audit logging | ❌ | ✅ | P1 |
| API rate limiting (per-user) | Partial (global only) | Per-org quotas | P1 |
| Webhook integrations | ❌ | ✅ | P2 |
| White-label/custom branding | ❌ | ✅ | P2 |
| SLA-backed support | ❌ | ✅ | P2 |

### 10.3 Deployment Readiness by Category

```
Security         ████████░░░░░░░░░░░░  55%  (need 90%+)
Testing          ██████░░░░░░░░░░░░░░  48%  (need 80%+)
Code Quality     ████████████████░░░░  78%  (need 85%+)
DevOps           █████████░░░░░░░░░░░  45%  (need 85%+)
Frontend         ██████████████░░░░░░  70%  (need 80%+)
ML Pipeline      █████████████░░░░░░░  65%  (need 80%+)
Documentation    █████████████████░░░  85%  (target met ✅)
─────────────────────────────────────────────
OVERALL          ████████████░░░░░░░░  62%  (need 80%+)
```

---

## 11. Deployment Readiness Score

### 11.1 Blocker Issues (Must Fix Before Any Client Demo)

| # | Issue | Category | Effort |
|---|-------|----------|:------:|
| B1 | Fix 5 broken currency tests | Testing | 1 hour |
| B2 | Fix SQL f-string patterns in profile.py | Security | 2 hours |
| B3 | Remove stale Supabase env vars from CI | DevOps | 1 hour |
| B4 | Remove dead Supabase deps from requirements.lock | Code Quality | 1 hour |
| B5 | Fix Pydantic v2 deprecation warning | Code Quality | 30 min |
| B6 | Add Dockerfile.backend + Dockerfile.frontend | DevOps | 3 hours |
| B7 | Stop logging database DSN | Security | 10 min |

**Estimated effort to clear blockers: ~8 hours (1 sprint day)**

### 11.2 Pre-Client-Pitch Checklist

| Check | Status |
|-------|:------:|
| All tests pass | ❌ (5 failing) |
| Zero known security vulnerabilities | ❌ (SQL patterns) |
| Containerized deployment | ❌ (no Dockerfiles) |
| CI/CD pipeline green | ❌ (stale env vars) |
| Monitoring in place | ❌ |
| Documentation complete | ✅ |
| Core features working | ✅ |
| Error handling comprehensive | ✅ |

---

## 12. Next-Semester Roadmap

### Phase 1: Foundation (Weeks 1-3) — Security & Testing

| Task | Priority | Effort | Impact |
|------|:--------:|:------:|:------:|
| Fix all blocker issues (§11.1) | P0 | 8h | Unblocks everything |
| Add API integration tests (pytest + httpx) | P0 | 16h | 30% coverage boost |
| Add frontend tests (Vitest + Testing Library) | P0 | 20h | 25% coverage boost |
| Implement RBAC (admin/user/viewer roles) | P0 | 24h | Enterprise requirement |
| Add audit logging middleware | P0 | 8h | SOC 2 requirement |
| Fix SQL injection patterns (use allowlist) | P0 | 4h | Security compliance |
| Add security headers middleware (CSP, HSTS) | P1 | 4h | OWASP compliance |

### Phase 2: Infrastructure (Weeks 4-6) — DevOps & Scaling

| Task | Priority | Effort | Impact |
|------|:--------:|:------:|:------:|
| Create proper Dockerfiles | P0 | 8h | Containerized deployment |
| Add Alembic for DB migrations | P0 | 12h | Safe schema changes |
| Integrate Sentry for error tracking | P1 | 4h | Production observability |
| Move file storage to S3/R2 | P1 | 16h | DB performance |
| Add health checks (DB + Firebase ping) | P1 | 4h | Load balancer support |
| Set up staging environment | P1 | 8h | Safe testing |
| Add E2E tests (Playwright) | P1 | 16h | Confidence in releases |

### Phase 3: Enterprise Features (Weeks 7-10) — Client Readiness

| Task | Priority | Effort | Impact |
|------|:--------:|:------:|:------:|
| Multi-tenant org management | P0 | 40h | Enterprise requirement |
| SSO/SAML integration | P1 | 24h | Enterprise requirement |
| Expand ML dataset to 2,000+ records | P1 | 20h | Prediction accuracy |
| Add model versioning (MLflow) | P1 | 16h | ML lifecycle |
| Jira/Linear integration | P2 | 24h | Velocity-based calibration |
| User feedback loop ("Was estimate accurate?") | P2 | 12h | Model improvement |
| Ensemble model (RF + XGBoost + Ridge) | P2 | 16h | Better generalization |

### Phase 4: Polish (Weeks 11-13) — Market Readiness

| Task | Priority | Effort | Impact |
|------|:--------:|:------:|:------:|
| WCAG 2.1 AA accessibility audit | P1 | 16h | Legal compliance |
| i18n/localization | P2 | 20h | International market |
| Performance optimization + CDN | P2 | 8h | User experience |
| White-label theming | P2 | 12h | B2B customization |
| Landing page + marketing site | P2 | 16h | Client acquisition |
| SOC 2 documentation prep | P1 | 20h | Enterprise sales |

### Projected Readiness After Next Semester

```
Security         ██████████████████░░  90%  (+35%)
Testing          ████████████████░░░░  80%  (+32%)
Code Quality     ██████████████████░░  90%  (+12%)
DevOps           █████████████████░░░  85%  (+40%)
Frontend         ████████████████░░░░  82%  (+12%)
ML Pipeline      ████████████████░░░░  80%  (+15%)
Documentation    ██████████████████░░  90%  (+5%)
─────────────────────────────────────────────
OVERALL          █████████████████░░░  85%  (+23%)
```

---

> *Full codebase audit performed April 29, 2026 — Predictify v3.1.0*
> *Benchmarked against: OWASP Top 10, SOC 2, ISBSG standards, SaaS industry best practices*
> *Next audit recommended: End of next semester or after Phase 2 completion*
