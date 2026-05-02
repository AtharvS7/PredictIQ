# Software Requirements Specification (SRS)

## PredictIQ — AI-Powered Software Cost Estimation Platform

| Field | Value |
|-------|-------|
| **Document Version** | 3.0.0 |
| **Date** | April 23, 2026 |
| **Prepared By** | Atharv Sawane & Team |
| **Standard** | IEEE 830-1998 |
| **Status** | Approved |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features & Functional Requirements](#3-system-features--functional-requirements)
4. [External Interface Requirements](#4-external-interface-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Database Design](#6-database-design)
7. [API Specification](#7-api-specification)
8. [Appendices](#8-appendices)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the functional, non-functional, and interface requirements for **PredictIQ** — an AI-powered SaaS platform that predicts software project cost, timeline, and effort from uploaded project documentation. This document serves as the authoritative reference for development, testing, and stakeholder communication.

### 1.2 Scope

PredictIQ enables software teams and project managers to:

- Upload project documents (SRS, PRD, RFP) in PDF, DOCX, or TXT format
- Automatically extract 11 project parameters using a 4-strategy NLP cascade engine
- Predict effort (hours), cost (multi-currency), and timeline (weeks) using a RandomForest ML model trained on 740 real-world project records
- Analyze project risk across 10 weighted factors
- Export branded reports in PDF, Excel, and CSV formats
- Share estimates via secure, time-limited links

**Boundaries:** PredictIQ does not manage project execution, task assignment, or real-time project tracking. It focuses exclusively on the pre-development estimation phase.

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|-----------|
| **SRS** | Software Requirements Specification |
| **NLP** | Natural Language Processing |
| **ML** | Machine Learning |
| **PERT** | Program Evaluation and Review Technique |
| **IFPUG** | International Function Point Users Group |
| **FP** | Function Points — a software size measurement metric |
| **COCOMO** | Constructive Cost Model |
| **JWT** | JSON Web Token |
| **RLS** | Row-Level Security |
| **BYTEA** | PostgreSQL binary data type |
| **SAST** | Static Application Security Testing |
| **CI/CD** | Continuous Integration / Continuous Deployment |
| **CORS** | Cross-Origin Resource Sharing |
| **OAuth** | Open Authorization protocol |
| **CVE** | Common Vulnerabilities and Exposures |

### 1.4 References

| # | Reference | Description |
|---|-----------|-------------|
| 1 | IEEE 830-1998 | IEEE Recommended Practice for SRS |
| 2 | IFPUG CPM 4.3.1 | Function Point Counting Practices Manual |
| 3 | Albrecht & Gaffney, 1983 | Software Function, Source Lines of Code, and Development Effort Prediction |
| 4 | COCOMO II Model | Constructive Cost Model for effort estimation |
| 5 | NASA93 Dataset | NASA software cost estimation dataset |
| 6 | CSBSG Chinese Dataset | Chinese Software Benchmarking Standards Group |

### 1.5 Overview

Section 2 provides overall product context and constraints. Section 3 details all functional requirements grouped by feature. Sections 4-5 cover interface and non-functional requirements. Sections 6-7 document database and API specifications.

---

## 2. Overall Description

### 2.1 Product Perspective

PredictIQ is a standalone, cloud-hosted SaaS application composed of:

- **Frontend SPA** — React 18 + TypeScript + Vite
- **Backend REST API** — Python FastAPI + Uvicorn
- **Database** — Neon Serverless PostgreSQL (asyncpg)
- **Authentication** — Firebase Auth (Admin SDK)
- **ML Engine** — scikit-learn RandomForest regression model
- **NLP Engine** — Custom 4-strategy cascade document analyzer

### 2.2 Product Functions (High-Level)

| # | Function | Description |
|---|----------|-------------|
| F1 | User Authentication | Email/password and OAuth (Google, GitHub) via Firebase Auth |
| F2 | Document Upload | Upload PDF/DOCX/TXT files (stored as BYTEA in PostgreSQL) |
| F3 | NLP Extraction | Automatically extract 11 project parameters from documents |
| F4 | Manual Entry | Enter project parameters manually without a document |
| F5 | ML Prediction | Predict effort hours using RandomForest model (R² = 0.8953) |
| F6 | Cost Estimation | Convert effort to cost in 10 currencies with PERT bounds |
| F7 | Risk Analysis | Score risk across 10 weighted factors with mitigation advice |
| F8 | Results Dashboard | Visualize predictions with charts, phase breakdown, benchmarks |
| F9 | Export | Generate PDF, Excel, CSV reports |
| F10 | Share | Create secure, password-protected, time-limited share links |
| F11 | Estimate Management | List, view, duplicate, soft-delete past estimates |
| F12 | User Profile | Manage preferences (currency, hourly rate, theme, timezone) |

### 2.3 User Classes and Characteristics

| User Class | Description | Technical Level |
|-----------|-------------|:---------------:|
| **Project Manager** | Uses the platform to estimate budgets for project proposals | Low–Medium |
| **Software Architect** | Validates ML predictions against experience-based estimates | High |
| **Freelance Developer** | Generates cost estimates for client proposals | Medium |
| **Business Analyst** | Extracts project scope from SRS documents for budgeting | Low–Medium |
| **Engineering Lead** | Reviews team sizing and timeline recommendations | Medium–High |

### 2.4 Operating Environment

| Component | Requirement |
|-----------|-------------|
| **Client Browser** | Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ |
| **Backend Runtime** | Python 3.11+ |
| **Frontend Runtime** | Node.js 18+ (build-time only) |
| **Database** | PostgreSQL 15+ (Neon serverless) |
| **Authentication** | Firebase Auth (Google Cloud) |
| **Hosting** | Backend: Railway / Render; Frontend: Vercel / Netlify |

### 2.5 Design and Implementation Constraints

| Constraint | Description |
|-----------|-------------|
| **C1** | Frontend must be a SPA (no server-side rendering) |
| **C2** | Backend must be stateless (no server-side sessions) |
| **C3** | All API endpoints (except health check) require Bearer token authentication |
| **C4** | ML model artifacts must be committed to the repository for teammate reproducibility |
| **C5** | Documents are stored as BYTEA in PostgreSQL (no external object storage) |
| **C6** | Firebase service account credentials must never be committed to version control |
| **C7** | Environment variables must be the sole mechanism for secret management |

### 2.6 Assumptions and Dependencies

| # | Assumption |
|---|-----------|
| A1 | Users have stable internet connectivity |
| A2 | Uploaded documents are in English |
| A3 | The Neon PostgreSQL free tier provides sufficient capacity for MVP |
| A4 | Firebase Auth free tier (50k monthly active users) is sufficient |
| A5 | ExchangeRate API remains available for currency conversion |
| A6 | The 740-record training dataset is representative of general software projects |

---

## 3. System Features & Functional Requirements

### 3.1 User Authentication (F1)

**Priority:** High | **Risk:** High

#### 3.1.1 Description
Users must create an account and authenticate before accessing any estimation features. The system supports email/password registration and OAuth sign-in (Google, GitHub).

#### 3.1.2 Functional Requirements

| ID | Requirement | Priority |
|----|------------|:--------:|
| FR-1.1 | The system shall allow users to register with email, password (min 10 chars), and full name | High |
| FR-1.2 | The system shall allow users to sign in with email and password | High |
| FR-1.3 | The system shall allow users to sign in with Google OAuth | Medium |
| FR-1.4 | The system shall allow users to sign in with GitHub OAuth | Medium |
| FR-1.5 | The system shall redirect authenticated users away from the auth page to /dashboard | High |
| FR-1.6 | The system shall persist authentication state across browser refreshes using Firebase `onAuthStateChanged` | High |
| FR-1.7 | The system shall allow users to reset their password via email | Medium |
| FR-1.8 | The system shall attach a Firebase ID token as `Authorization: Bearer <token>` on all API requests | High |
| FR-1.9 | The backend shall verify tokens using `firebase_admin.auth.verify_id_token()` | High |
| FR-1.10 | The backend shall reject expired, revoked, or invalid tokens with HTTP 401 | High |

---

### 3.2 Document Upload (F2)

**Priority:** High | **Risk:** Medium

#### 3.2.1 Description
Users upload project documentation files which are stored in the database and parsed for text extraction.

#### 3.2.2 Functional Requirements

| ID | Requirement | Priority |
|----|------------|:--------:|
| FR-2.1 | The system shall accept file uploads in PDF, DOCX, and TXT formats | High |
| FR-2.2 | The system shall enforce a maximum file size of 10 MB | High |
| FR-2.3 | The system shall store uploaded files as BYTEA in the `document_uploads` table | High |
| FR-2.4 | The system shall record original filename, file size, MIME type, and upload timestamp | High |
| FR-2.5 | The system shall provide a drag-and-drop upload interface with progress indicator | Medium |
| FR-2.6 | The system shall parse uploaded files using PyPDF2 (PDF), python-docx (DOCX), or plain text reader (TXT) | High |
| FR-2.7 | The system shall store a 500-character text preview in `parsed_text_preview` | Low |

---

### 3.3 NLP Extraction (F3)

**Priority:** High | **Risk:** Medium

#### 3.3.1 Description
Immediately after upload, the system runs an NLP extraction pipeline to automatically identify 11 project parameters from the document text.

#### 3.3.2 Functional Requirements

| ID | Requirement | Priority |
|----|------------|:--------:|
| FR-3.1 | The system shall provide a `POST /documents/{id}/extract` endpoint that triggers NLP analysis | High |
| FR-3.2 | The NLP engine shall extract: project_name, project_type, tech_stack, team_size, duration_months, complexity, methodology, feature_count, integration_count, volatility_score, team_experience | High |
| FR-3.3 | Each extracted parameter shall include a confidence score (0.0–1.0) | Medium |
| FR-3.4 | The NLP engine shall use a 4-strategy cascade: Structural → Section-Aware → Global Patterns → Cross-Validation | High |
| FR-3.5 | The system shall recognize 300+ technology keywords across 7 categories with canonical normalization | Medium |
| FR-3.6 | The frontend shall auto-populate the Step 2 form fields with extracted parameters | High |
| FR-3.7 | Users shall be able to override any NLP-extracted value before generating an estimate | High |
| FR-3.8 | The system shall provide sensible defaults for parameters not detected (e.g., team_size=5, complexity="Medium") | Medium |

---

### 3.4 Manual Entry (F4)

**Priority:** Medium | **Risk:** Low

#### 3.4.1 Functional Requirements

| ID | Requirement | Priority |
|----|------------|:--------:|
| FR-4.1 | The system shall allow users to skip document upload and enter parameters manually | Medium |
| FR-4.2 | The manual entry form shall contain the same 11 fields as the NLP extraction output | Medium |
| FR-4.3 | Project name shall be required; all other fields shall have defaults | Medium |

---

### 3.5 ML Prediction Engine (F5)

**Priority:** High | **Risk:** High

#### 3.5.1 Description
The core prediction engine uses a RandomForest regression model trained on 740 real-world software project records from 4 benchmark datasets.

#### 3.5.2 Functional Requirements

| ID | Requirement | Priority |
|----|------------|:--------:|
| FR-5.1 | The system shall compute IFPUG Function Points from user parameters (feature_count, complexity, integration_count) | High |
| FR-5.2 | The system shall construct a 27-dimensional feature vector from user inputs + computed FP values | High |
| FR-5.3 | The system shall scale the feature vector using the fitted StandardScaler | High |
| FR-5.4 | The system shall predict `effort_likely_hours` using the trained RandomForest model | High |
| FR-5.5 | The system shall compute PERT bounds: min = likely × 0.80, max = likely × 1.40 | High |
| FR-5.6 | The system shall compute a model confidence percentage based on input completeness and feature reliability | Medium |
| FR-5.7 | The ML model shall achieve R² ≥ 0.89 on the test dataset | High |
| FR-5.8 | The model artifacts (`predictiq_best_model.pkl`, `predictiq_scaler.pkl`) shall be committed to the repository | Medium |

---

### 3.6 Cost Estimation (F6)

**Priority:** High | **Risk:** Low

#### 3.6.1 Functional Requirements

| ID | Requirement | Priority |
|----|------------|:--------:|
| FR-6.1 | The system shall compute cost as `effort_hours × hourly_rate` for min/likely/max bounds | High |
| FR-6.2 | The system shall support 10 currencies: USD, EUR, GBP, INR, JPY, AUD, CAD, CHF, CNY, SGD | High |
| FR-6.3 | The system shall fetch live exchange rates from ExchangeRate API with 24-hour cache | Medium |
| FR-6.4 | The system shall fall back to hardcoded rates if the API is unavailable | Medium |
| FR-6.5 | The system shall compute timeline as `effort_hours / (team_size × 40 hours/week)` | High |
| FR-6.6 | The default hourly rate shall be $75 USD, configurable per user profile | Medium |

---

### 3.7 Risk Analysis (F7)

**Priority:** Medium | **Risk:** Low

#### 3.7.1 Functional Requirements

| ID | Requirement | Priority |
|----|------------|:--------:|
| FR-7.1 | The system shall evaluate 10 weighted risk factors (scope ambiguity, team experience, timeline, technology complexity, volatility, QA gap, integration, resources, technical debt, deployment) | Medium |
| FR-7.2 | The system shall compute a composite risk score (0–100) | Medium |
| FR-7.3 | The system shall classify risk as Low (<25), Medium (<45), High (<70), Critical (≥70) | Medium |
| FR-7.4 | The system shall return the top risk factors with descriptions and mitigation advice | Medium |

---

### 3.8 Results Dashboard (F8)

**Priority:** High | **Risk:** Low

#### 3.8.1 Functional Requirements

| ID | Requirement | Priority |
|----|------------|:--------:|
| FR-8.1 | The system shall display effort, cost, and timeline in min/likely/max format | High |
| FR-8.2 | The system shall render charts using Recharts (bar charts, pie charts) | Medium |
| FR-8.3 | The system shall display a phase breakdown (Discovery 10%, Design 12%, Backend 30%, Frontend 22%, QA 18%, DevOps 8%) | Medium |
| FR-8.4 | The system shall display a risk gauge with top risk factors | Medium |
| FR-8.5 | The system shall display industry benchmark comparison data | Low |

---

### 3.9 Export (F9)

**Priority:** Medium | **Risk:** Low

#### 3.9.1 Functional Requirements

| ID | Requirement | Priority |
|----|------------|:--------:|
| FR-9.1 | The system shall export estimates as PDF reports (ReportLab) | Medium |
| FR-9.2 | The system shall export estimates as Excel spreadsheets (openpyxl) | Medium |
| FR-9.3 | The system shall export estimates as CSV files | Low |
| FR-9.4 | Exported reports shall include inputs, outputs, phase breakdown, and risk analysis | Medium |

---

### 3.10 Share Links (F10)

**Priority:** Low | **Risk:** Low

#### 3.10.1 Functional Requirements

| ID | Requirement | Priority |
|----|------------|:--------:|
| FR-10.1 | The system shall generate unique share tokens for estimates | Low |
| FR-10.2 | Share links shall optionally require a password | Low |
| FR-10.3 | Share links shall have configurable expiration dates | Low |

---

### 3.11 Estimate Management (F11)

**Priority:** High | **Risk:** Low

#### 3.11.1 Functional Requirements

| ID | Requirement | Priority |
|----|------------|:--------:|
| FR-11.1 | The system shall list all user estimates with pagination, sorted by creation date | High |
| FR-11.2 | The system shall allow viewing full estimate details | High |
| FR-11.3 | The system shall allow duplicating an estimate as a new version | Medium |
| FR-11.4 | The system shall soft-delete estimates (set status to 'deleted') | Medium |
| FR-11.5 | The system shall display dashboard statistics (total estimates, average cost, average confidence) | Medium |

---

### 3.12 User Profile (F12)

**Priority:** Low | **Risk:** Low

#### 3.12.1 Functional Requirements

| ID | Requirement | Priority |
|----|------------|:--------:|
| FR-12.1 | The system shall auto-create a profile on first sign-in | Medium |
| FR-12.2 | Users shall be able to update: full name, avatar URL, hourly rate, preferred currency, theme, timezone | Low |
| FR-12.3 | Profile preferences shall persist across sessions | Low |

---

## 4. External Interface Requirements

### 4.1 User Interfaces

| Screen | Route | Description |
|--------|-------|-------------|
| Landing Page | / | Hero section, feature grid, how-it-works steps, CTA |
| Auth Page | /auth | Login/register/forgot-password tabs with email + OAuth |
| Dashboard | /dashboard | Estimate cards, aggregate statistics, sort/filter controls |
| New Estimate | /estimate/new | 3-step wizard: Upload → Parameters → Generate |
| Results | /estimate/:id/results | Charts, risk gauge, phase breakdown, export buttons |
| Estimates List | /estimates | Paginated history of all user estimates |
| Settings | /settings | Profile preferences (name, currency, rate, theme) |

**UI Constraints:**
- Responsive layout (desktop-first, mobile-compatible)
- Dark mode with glassmorphism design system
- All interactive elements must have unique IDs for automated testing
- Loading states must use skeleton placeholders

### 4.2 Hardware Interfaces

No direct hardware interfaces. The application runs entirely in the browser and communicates with the backend over HTTPS.

### 4.3 Software Interfaces

| Interface | Protocol | Description |
|-----------|----------|-------------|
| Firebase Auth | HTTPS (Firebase SDK) | User authentication and token issuance |
| Neon PostgreSQL | TCP/TLS (asyncpg) | Primary data storage (connection pooling, min=2, max=10) |
| ExchangeRate API | HTTPS REST | Live currency exchange rates (10 currencies) |
| Firebase Admin SDK | HTTPS | Server-side token verification |

### 4.4 Communication Interfaces

| Protocol | Usage |
|----------|-------|
| HTTPS | All client-server communication |
| WebSocket | Not used (all operations are request-response) |
| TLS 1.3 | Required for database connections (Neon enforces sslmode=require) |

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR-1.1 | API response time for estimation (P95) | < 3 seconds |
| NFR-1.2 | NLP extraction time for a 50-page document | < 5 seconds |
| NFR-1.3 | Frontend initial page load (First Contentful Paint) | < 2 seconds |
| NFR-1.4 | ML model inference time | < 100 ms |
| NFR-1.5 | Concurrent user support | 100+ simultaneous |
| NFR-1.6 | Database connection pool | 2–10 connections |
| NFR-1.7 | File upload size limit | 10 MB max |

### 5.2 Safety Requirements

| ID | Requirement |
|----|------------|
| NFR-2.1 | The system shall not permanently delete data; soft-delete pattern used |
| NFR-2.2 | File uploads shall be validated for MIME type before processing |
| NFR-2.3 | ML model predictions shall be clamped between 1 and 9,587 hours |

### 5.3 Security Requirements

| ID | Requirement | Implementation |
|----|------------|----------------|
| NFR-3.1 | All API endpoints (except /health) shall require authentication | Firebase Admin SDK token verification |
| NFR-3.2 | Passwords shall be minimum 10 characters | Frontend validation + Firebase enforcement |
| NFR-3.3 | API rate limiting shall prevent abuse | slowapi: 200 requests/minute |
| NFR-3.4 | No secrets shall be committed to version control | Pre-push scanner + .gitignore audit |
| NFR-3.5 | CORS shall restrict origins to configured frontend domains | FastAPI CORSMiddleware |
| NFR-3.6 | Firebase credentials shall support dual-mode loading | File path (local) or JSON env var (production) |
| NFR-3.7 | Weekly automated vulnerability scanning | pip-audit + npm audit + CodeQL SAST |
| NFR-3.8 | Expired/revoked tokens shall be rejected with HTTP 401 | Firebase Admin SDK handles revocation checks |
| NFR-3.9 | Database connections shall use TLS encryption | Neon enforces sslmode=require |

### 5.4 Software Quality Attributes

| Attribute | Requirement |
|-----------|-------------|
| **Reliability** | Backend test suite: 104+ tests passing; ML model R-squared >= 0.89 |
| **Maintainability** | Modular service layer; each service is a single Python file with clear responsibility |
| **Portability** | Dockerized deployment; runs on any platform with Python 3.11+ and Node 18+ |
| **Scalability** | Stateless backend; Neon serverless auto-scales; connection pooling via asyncpg |
| **Usability** | 3-step wizard with NLP auto-fill; < 60 seconds from upload to results |
| **Testability** | 111 test cases; pytest markers (unit, integration, e2e, slow) |

### 5.5 Availability

| Requirement | Target |
|-------------|--------|
| Uptime SLA | 99.5% (excluding planned maintenance) |
| Health check endpoint | GET /api/health — returns model status, uptime, version |
| Graceful degradation | Currency API fallback to hardcoded rates |

---

## 6. Database Design

### 6.1 Database Engine

Neon Serverless PostgreSQL with asyncpg driver. Connection pooling: min_size=2, max_size=10, command_timeout=30s.

### 6.2 Entity Relationship Diagram

`
profiles (1) ──── (N) document_uploads
profiles (1) ──── (N) estimates
document_uploads (1) ──── (N) estimates
estimates (1) ──── (N) share_links
`

### 6.3 Table Specifications

#### 6.3.1 profiles
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PK | Firebase UID |
| full_name | TEXT | nullable | Display name |
| avatar_url | TEXT | nullable | Profile image URL |
| hourly_rate_usd | FLOAT | DEFAULT 75.0 | Billing rate |
| currency | TEXT | DEFAULT 'USD' | Preferred currency |
| theme | TEXT | DEFAULT 'system' | UI theme |
| timezone | TEXT | DEFAULT 'UTC' | Timezone |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Created |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Updated |

#### 6.3.2 document_uploads
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, gen_random_uuid() | Document ID |
| user_id | TEXT | NOT NULL | Firebase UID |
| storage_path | TEXT | nullable | Legacy field |
| original_filename | TEXT | NOT NULL | User filename |
| file_size_bytes | BIGINT | DEFAULT 0 | Size |
| mime_type | TEXT | nullable | MIME type |
| status | TEXT | DEFAULT 'uploaded' | uploaded/parsed/failed |
| parsed_text_preview | TEXT | nullable | First 500 chars |
| file_data | BYTEA | nullable | Binary file content |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Upload time |

#### 6.3.3 estimates
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, gen_random_uuid() | Estimate ID |
| user_id | TEXT | NOT NULL | Owner |
| document_id | UUID | FK -> document_uploads | Source document |
| project_name | TEXT | NOT NULL | Project title |
| version | INT | DEFAULT 1 | Version number |
| status | TEXT | DEFAULT 'complete' | processing/complete/failed/deleted |
| inputs_json | JSONB | nullable | Input parameters snapshot |
| outputs_json | JSONB | nullable | Output results snapshot |
| effort_likely_hours | FLOAT | nullable | Predicted effort |
| cost_likely_usd | FLOAT | nullable | Predicted cost |
| duration_likely_weeks | FLOAT | nullable | Predicted timeline |
| risk_score | FLOAT | nullable | Risk score (0-100) |
| confidence_pct | FLOAT | nullable | Model confidence |
| model_version | TEXT | DEFAULT '1.0.0' | ML model version |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Created |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Updated |

#### 6.3.4 share_links
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, gen_random_uuid() | Link ID |
| estimate_id | UUID | FK -> estimates, NOT NULL | Target estimate |
| token | TEXT | UNIQUE, NOT NULL | Share token |
| password_hash | TEXT | nullable | Optional password |
| expires_at | TIMESTAMPTZ | nullable | Expiration |
| view_count | INT | DEFAULT 0 | Access count |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Created |

### 6.4 Indexes

| Index | Table | Column(s) |
|-------|-------|-----------|
| idx_document_uploads_user_id | document_uploads | user_id |
| idx_estimates_user_id | estimates | user_id |
| idx_estimates_status | estimates | status |
| idx_estimates_created_at | estimates | created_at DESC |
| idx_share_links_token | share_links | token |

---

## 7. API Specification

### 7.1 Base URL

- Development: http://localhost:8000/api/v1
- Production: https://<backend-domain>/api/v1

### 7.2 Authentication

All endpoints (except health check) require: Authorization: Bearer <firebase_id_token>

### 7.3 Endpoint Inventory

| Method | Path | Auth | Description |
|--------|------|:----:|-------------|
| POST | /estimates/analyze | Yes | Analyze document and generate full estimate |
| POST | /estimates/manual | Yes | Generate estimate from manual parameters |
| GET | /estimates | Yes | List user estimates (paginated) |
| GET | /estimates/{id} | Yes | Get full estimate details |
| POST | /estimates/{id}/duplicate | Yes | Duplicate estimate as new version |
| DELETE | /estimates/{id} | Yes | Soft-delete estimate |
| POST | /estimates/{id}/share | Yes | Generate share link |
| POST | /documents/upload | Yes | Confirm document upload (metadata) |
| POST | /documents/upload-file | Yes | Upload file (multipart form data) |
| POST | /documents/{id}/extract | Yes | Trigger NLP extraction on uploaded document |
| GET | /currencies/rates | Yes | Get exchange rates (10 currencies) |
| GET | /export/{id}/pdf | Yes | Export estimate as PDF |
| GET | /export/{id}/excel | Yes | Export estimate as Excel |
| GET | /export/{id}/csv | Yes | Export estimate as CSV |
| GET | /health | No | Health check (model status, uptime) |

### 7.4 Error Response Format

`json
{
  "detail": "Human-readable error message"
}
`

Standard HTTP status codes: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 404 (Not Found), 500 (Internal Server Error).

---

## 8. Appendices

### 8.1 Technology Stack Summary

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | React + TypeScript | 18.x / 5.x |
| Build Tool | Vite | 5.x |
| State Management | Zustand | 5.x |
| Charts | Recharts | 2.x |
| Backend | FastAPI + Uvicorn | 0.115+ |
| ML Engine | scikit-learn (RandomForest) | 1.8 |
| NLP Engine | Custom Cascade Engine | v2.4 |
| Database | Neon PostgreSQL (asyncpg) | 17+ |
| Auth | Firebase Auth (Admin SDK) | 6.x |
| CI/CD | GitHub Actions | v4 |
| Rate Limiting | slowapi | 0.1.9 |

### 8.2 ML Training Datasets

| Source | Records | Key Features |
|--------|:-------:|-------------|
| Albrecht | ~24 | Function points, effort, team experience |
| China (CSBSG) | ~499 | Function points, effort, methodology |
| Desharnais-Maxwell | ~77 | FP, language, methodology, duration |
| NASA93 | ~93 | LOC, effort multipliers, COCOMO T-factors |
| **Total** | **740** | Merged into predictiq_merged_dataset.csv |

### 8.3 Supported Currencies

| Code | Symbol | Name |
|------|:------:|------|
| USD | $ | US Dollar |
| EUR | Euro | Euro |
| GBP | Pound | British Pound |
| INR | Rs | Indian Rupee |
| JPY | Yen | Japanese Yen |
| AUD | A$ | Australian Dollar |
| CAD | C$ | Canadian Dollar |
| CHF | Fr | Swiss Franc |
| CNY | Yuan | Chinese Yuan |
| SGD | S$ | Singapore Dollar |

### 8.4 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | April 9, 2026 | Atharv Sawane | Initial SRS |
| 2.0.0 | April 15, 2026 | Atharv Sawane | NLP v2.4, CI/CD pipeline |
| 3.0.0 | April 23, 2026 | Atharv Sawane | Firebase Auth + Neon migration, NLP auto-fill |

---

> **End of Document** — PredictIQ Software Requirements Specification v3.0.0
