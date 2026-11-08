# PredictIQ Documentation Master Index

Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

---

## 1. Documentation Structure & Map

Welcome to the documentation suite for **PredictIQ**. This repository contains formal specifications, architectural designs, API contracts, empirical data registries, production runbooks, and historical development archives.

```text
docs/
├── product/              # Product vision, user journeys, requirements, roadmap, glossary
├── architecture/         # System topology, backend, frontend, data model, ML pipeline, security
├── design/               # Design tokens, responsive clamps, accessibility, content guidelines
├── api/                  # REST API endpoints, estimation contracts, error handling, deprecation
├── contracts/            # Formal JSON schemas, ML behavioral contracts, evaluation protocols
├── data/                 # Empirical dataset registries, datasheets, deduplication reports
├── operations/           # CI/CD pipelines, deployment guides, monitoring, backup & recovery, runbooks
├── security/             # Threat models (STRIDE), RBAC, artifact integrity, privacy handling
├── history/              # Preserved historical audit reports & earlier development records
└── evidence/             # Formal checkpoint audit logs and milestone push verification records
```

---

## 2. Product Specifications (`docs/product/`)

Core specifications governing product vision, functional capabilities, and user experience:

| Document | Description |
| :--- | :--- |
| **[`overview.md`](product/overview.md)** | Product vision, target personas (CTO, TPM, PM, Procurement), and core value proposition. |
| **[`requirements-spec.md`](product/requirements-spec.md)** | Traceable functional requirements (`REQ-AUTH`, `REQ-EST`, `REQ-UNC`, `REQ-ACT`, `REQ-BUD`). |
| **[`user-flows.md`](product/user-flows.md)** | Five core user journeys: Estimation Wizard, Results Exploration, Actuals Flywheel, History, Settings. |
| **[`glossary.md`](product/glossary.md)** | Canonical definitions for Function Points, IFPUG, LOSO, MdAPE, Mondrian Conformal, Brooks' Law. |
| **[`roadmap.md`](product/roadmap.md)** | Multi-phase development roadmap (v2.1 COSMIC & Jira sync, v2.2 ISBSG, v3.0 Codebase Sizing). |

---

## 3. Architecture & Technical Design (`docs/architecture/`)

Detailed architectural designs strictly verified against current production code:

| Document | Description |
| :--- | :--- |
| **[`system-overview.md`](architecture/system-overview.md)** | End-to-end multi-tier architectural topology and component boundaries with Mermaid diagrams. |
| **[`backend.md`](architecture/backend.md)** | FastAPI services, middleware stack, dependency injection container, and asyncpg connection pooling. |
| **[`frontend.md`](architecture/frontend.md)** | React 18, Vite build pipeline, Tailwind CSS token integration, and Zustand reactive stores. |
| **[`data-model.md`](architecture/data-model.md)** | PostgreSQL relational schema: profiles, documents, estimates, actuals, and task budgets. |
| **[`ml-pipeline.md`](architecture/ml-pipeline.md)** | Monotone power-law engine ($E = a \cdot S^b$), Mondrian conformal intervals, and empirical Bayes shrinkage. |
| **[`security-architecture.md`](architecture/security-architecture.md)** | Zero-pickle JSON serving, fail-closed SHA-256 verification, RBAC, and isolated subprocess parsing. |

---

## 4. Design System & Accessibility (`docs/design/`)

Visual guidelines, design tokens, and user experience invariants:

| Document | Description |
| :--- | :--- |
| **[`design-system.md`](design/design-system.md)** | CSS custom properties, color palettes, responsive `clamp()` expressions, and typography scales. |
| **[`accessibility.md`](design/accessibility.md)** | WCAG 2.1 AA guidelines, 44px touch targets, `:focus-visible` rings, and screen reader ARIA roles. |
| **[`content-guidelines.md`](design/content-guidelines.md)** | Plain-language uncertainty communication, banned hype words policy, and replacement vocabulary. |

---

## 5. API Reference & Contracts (`docs/api/` & `docs/contracts/`)

Formal REST API interfaces, JSON schemas, and machine learning constraints:

| Document | Description |
| :--- | :--- |
| **[`api/README.md`](api/README.md)** | REST API overview, base URLs, authentication headers, and rate limiting policies. |
| **[`api/estimate-v2.md`](api/estimate-v2.md)** | Endpoint specification for `/estimates/manual`, `/estimates/analyze`, and `/estimates/{id}` with real captured responses. |
| **[`api/errors.md`](api/errors.md)** | Standardized HTTP status codes (400, 401, 403, 404, 422, 503) and structured error response payloads. |
| **[`api/versioning-and-deprecation.md`](api/versioning-and-deprecation.md)** | Semantic versioning policy, sunset timelines, and RFC 8594 deprecation header specifications. |
| **[`contracts/api_estimate_v2.json`](contracts/api_estimate_v2.json)** | Canonical JSON Schema (Draft 2020-12) for estimation outputs. |
| **[`contracts/ml_contract.md`](contracts/ml_contract.md)** | Invariant rules prohibiting synthetic features, enforcing monotonicity, and bounding outputs. |
| **[`contracts/evaluation_protocol_rc3.md`](contracts/evaluation_protocol_rc3.md)** | Pre-registered frozen evaluation protocol governing RC3 empirical Bayes shrinkage and challenger criteria. |

---

## 6. Empirical Data Registry (`docs/data/`)

Provenance and audit records for the 915 verified software projects powering PredictIQ:

| Document | Description |
| :--- | :--- |
| **[`data/DATASHEET.md`](data/DATASHEET.md)** | Standardized dataset datasheet (Gebru et al.) for `projects_v2.csv` ($N = 915$). |
| **[`data/DEDUPLICATION_REPORT.md`](data/DEDUPLICATION_REPORT.md)** | Verification of zero cross-source duplicate projects and audited unit conversions. |
| **[`data/SOURCES.md`](data/SOURCES.md)** | Detailed audit of all 17 evaluated empirical datasets with inclusion/exclusion justifications. |
| **[`data/sources.yaml`](data/sources.yaml)** | Machine-readable source registry containing URLs, SHA-256 hashes, and citation metadata. |
| **[`data/ISBSG_PLAN.md`](data/ISBSG_PLAN.md)** | Roadmap and ingestion framework for future commercial ISBSG expansion. |
| **[`data/MANUAL_DOWNLOADS.md`](data/MANUAL_DOWNLOADS.md)** | Reproducibility guide for retrieving primary research datasets. |

---

## 7. Operations & Security (`docs/operations/` & `docs/security/`)

Infrastructure deployment, system administration, and security postures:

| Document | Description |
| :--- | :--- |
| **[`operations/deployment-aws.md`](operations/deployment-aws.md)** | Production deployment architecture for AWS ECS Fargate, App Runner, and CloudFront. |
| **[`operations/environments.md`](operations/environments.md)** | Configuration variables matrix across development, staging, and production environments. |
| **[`operations/ci-cd.md`](operations/ci-cd.md)** | Continuous Integration workflows, unified release gate integration, and branch protection rules. |
| **[`operations/monitoring-and-health.md`](operations/monitoring-and-health.md)** | Health probe specifications (`/live`, `/health`, `/ready`), metrics collection, and alerting policies. |
| **[`operations/backup-and-recovery.md`](operations/backup-and-recovery.md)** | Neon PostgreSQL continuous PITR, immutable S3 dumps, and RTO/RPO disaster recovery procedures. |
| **[`operations/release-checklist.md`](operations/release-checklist.md)** | Step-by-step production release verification checklist from pre-release to post-deploy. |
| **[`operations/secrets-rotation.md`](operations/secrets-rotation.md)** | Zero-downtime rotation procedures for database credentials, Firebase keys, and API secrets. |
| **[`operations/github-secrets-setup.md`](operations/github-secrets-setup.md)** | Required repository and environment secrets setup for GitHub Actions CI/CD. |
| **[`security/threat-model.md`](security/threat-model.md)** | Comprehensive STRIDE threat model across all system trust boundaries. |
| **[`security/rbac-and-authz.md`](security/rbac-and-authz.md)** | Role-Based Access Control implementation, permission matrices, and token verification. |
| **[`security/privacy-and-data-handling.md`](security/privacy-and-data-handling.md)** | Explicit training consent flywheel, multi-tenant isolation, and GDPR/CCPA data export/erasure. |
| **[`security/artifact-integrity.md`](security/artifact-integrity.md)** | Cryptographic SHA-256 verification and fail-closed zero-pickle pure JSON serving guarantee. |
| **[`security/incident-response.md`](security/incident-response.md)** | Coordinated vulnerability disclosure policy, severity matrix, and emergency triage playbooks. |
| **[`security/enterprise-readiness-gaps.md`](security/enterprise-readiness-gaps.md)** | Objective appraisal of enterprise security posture, SOC 2 Type II status, SSO, and SIEM roadmap. |

---

## 8. Runbooks (`docs/operations/runbooks/`)

Step-by-step operational procedures and developer onboarding runbooks:

| Runbook | Scope |
| :--- | :--- |
| **[`operations/runbooks/production-deployment.md`](operations/runbooks/production-deployment.md)** | Production rollout procedures, configuration checklist, and post-deployment validation. |
| **[`operations/runbooks/production-ml.md`](operations/runbooks/production-ml.md)** | Model artifact packaging, checksum verification, and promotion workflows. |
| **[`operations/runbooks/credential-rotation.md`](operations/runbooks/credential-rotation.md)** | Zero-downtime rotation of database credentials, Firebase secrets, and API keys. |
| **[`operations/runbooks/deployment-inputs.md`](operations/runbooks/deployment-inputs.md)** | Production deployment input matrix, preflight verification, and required variables. |
| **[`operations/runbooks/add-team-member.md`](operations/runbooks/add-team-member.md)** | Developer onboarding guide and local environment setup. |

---

## 9. Historical Archives & Evidence (`docs/history/` & `docs/evidence/`)

- **[`docs/history/`](history/):** Preserved historical audit reports, engineering progress logs, and security containment records from earlier development phases. All files carry prominent historical warning banners.
- **[`docs/evidence/`](evidence/):** Checkpoint audit trails (CP00–CP26, R00–R14, S00) and Milestone Push Procedure (MPP) verification records.
