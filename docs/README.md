# PredictIQ Documentation Index

Welcome to the comprehensive documentation suite for **PredictIQ v2.0**. This directory contains formal API contracts, empirical data registries, scientific validation evidence, production runbooks, and architectural audits.

---

## 🗺️ Documentation Map

```text
docs/
├── contracts/          # Formal API contracts, JSON schemas, and evaluation protocols
├── data/               # Empirical dataset registries, datasheets, and acquisition guides
├── evidence/           # Checkpoint logs, ablation studies, and benchmark audit trails
├── runbooks/           # Production deployment, ML serving operations, and rotation runbooks
└── [Architecture/Audits] # Root architectural walkthroughs, security audits, and progress logs
```

---

## 1. Contracts & Specifications (`docs/contracts/`)

Formal interfaces, data schemas, and mathematical evaluation protocols governing PredictIQ v2:

| Document | Description | Format / Standard |
| :--- | :--- | :--- |
| **[`api_estimate_v2.json`](contracts/api_estimate_v2.json)** | Canonical JSON Schema defining the PredictIQ v2 estimation response interface ($P_{10}, P_{25}, P_{50}, P_{75}, P_{90}$ effort, cost, size uncertainty, OOD diagnostics). | JSON Schema Draft 2020-12 |
| **[`mock_estimate_v2.json`](contracts/mock_estimate_v2.json)** | Reference JSON payload illustrating a fully hydrated, calibrated estimate conforming to `api_estimate_v2.json`. | JSON |
| **[`ml_contract.md`](contracts/ml_contract.md)** | Machine learning contract specifying valid input ranges, monotonicity invariants ($\frac{\partial E}{\partial S} > 0$), and fail-closed security guarantees. | Markdown Specification |
| **[`evaluation_protocol.md`](contracts/evaluation_protocol.md)** | Original v2 6-fold Leave-One-Source-Out (LOSO) cross-validation protocol and benchmark baseline rules. | Markdown Protocol |
| **[`evaluation_protocol_rc2.md`](contracts/evaluation_protocol_rc2.md)** | Pre-registered frozen evaluation protocol for RC2: duration elasticity criteria, challenger replacement gates, and non-crossing confidence boundaries. | Markdown Protocol |

---

## 2. Empirical Data Registry (`docs/data/`)

Transparency and provenance records for the **915 verified software projects** powering PredictIQ v2:

| Document | Description | Key Contents |
| :--- | :--- | :--- |
| **[`DATASHEET.md`](data/DATASHEET.md)** | Standardized dataset datasheet (following Gebru et al.) for `projects_v2.csv` ($N = 915$). | Provenance, collection methods, preprocessing, and ethical use |
| **[`DEDUPLICATION_REPORT.md`](data/DEDUPLICATION_REPORT.md)** | Audit report verifying cross-source deduplication, identity resolution, and unit conversion rules across all 6 core repositories. | Zero duplicate projects, verified $1,000 \times$ Albrecht multiplier |
| **[`SOURCES.md`](data/SOURCES.md)** | Comprehensive catalog of all 17 evaluated candidate datasets, licensing statuses, and technical inclusion/exclusion justifications. | PROMISE, ISBSG, COSMIC, Tukutuku, SEERA, Kemerer audits |
| **[`sources.yaml`](data/sources.yaml)** | Machine-readable source registry containing URLs, SHA-256 hashes, citation keys, and column mappings. | YAML Registry |
| **[`ISBSG_PLAN.md`](data/ISBSG_PLAN.md)** | Architectural plan and schema mapping for future enterprise expansion with commercial ISBSG datasets (13,000+ projects). | Schema harmonization, licensing, and validation roadmap |
| **[`MANUAL_DOWNLOADS.md`](data/MANUAL_DOWNLOADS.md)** | Step-by-step instructions for manual retrieval and verification of academic source datasets. | Reproducibility guide |

---

## 3. Scientific Evidence & Audit Trails (`docs/evidence/`)

Comprehensive empirical benchmarks, ablation studies, and checkpoint delivery records:

### 3.1. Master Milestone Tracking & Snapshots
- **[`milestones.md`](evidence/milestones.md):** Master milestone ledger tracking Milestones M1 through M5 and RC2_M1, quality gates, test pass counts, and git commit SHAs.
- **[`MPP_RC2_M1.md`](evidence/MPP_RC2_M1.md):** Milestone Push Procedure verification for RC2_M1 (wiring, cleanup, Brooks' Law duration ablation, log-space size uncertainty).
- **[`MPP_final.md`](evidence/MPP_final.md):** Final Milestone Push Procedure verification record for v2.0.0-rc.1.
- **[`rc2_snapshot.md`](evidence/rc2_snapshot.md):** Baseline commit SHAs, remote safety audits, and baseline test counts for RC2 hardening.
- **[`dev2_snapshot.md`](evidence/dev2_snapshot.md):** Historical baseline state snapshot prior to dev3 branching.

### 3.2. RC2 Hardening Checkpoints (R00 – R13)
- **[`R00.md`](evidence/R00.md) & [`R00_findings.md`](evidence/R00_findings.md):** Repository baseline orientation, truth audit, test path stabilization, and branch safety.
- **[`R01.md`](evidence/R01.md):** Decoupled FastAPI runtime from revoked legacy predictor; implemented fail-closed health and readiness probes.
- **[`R02.md`](evidence/R02.md):** Purged 30 MB revoked binary pickle file, 25 obsolete research scripts, and 17 dead test files from `backend/ml/`.
- **[`R03.md`](evidence/R03.md):** Model input validity & frozen decision rule; empirical duration elasticity ablation ($c = +0.5972 > 0 \implies$ rejected duration under Brooks' Law; enforced size-only point estimate $E = a \cdot S^b$).
  - Raw Data: [`r03_ablation_results.json`](evidence/r03_ablation_results.json)
- **[`R04.md`](evidence/R04.md):** Functional size uncertainty propagation into conformal effort intervals via log-space variance combination ($q_{\text{combined}} = \sqrt{q_{\text{model}}^2 + (b \cdot \Delta_s)^2}$).
  - Simulation Data: [`r04_simulation_results.json`](evidence/r04_simulation_results.json) (10,000 projects, 82.54% empirical coverage).
- **[`R05.md`](evidence/R05.md):** Empirical Bayes shrinkage calibration using completed organization actuals ($+19.52\%$ relative accuracy gain at $k=10$).
  - Monte Carlo Data: [`r05_eb_results.json`](evidence/r05_eb_results.json) (50 trials per fold, $k \in \{0, 3, 5, 10, 20\}$).
- **[`R06.md`](evidence/R06.md):** Round 2 data expansion audit; re-verification of canonical $N=915$; justified exclusion of non-IFPUG candidate datasets.
- **[`R07.md`](evidence/R07.md):** Challenger models shootout under frozen evaluation protocol (Hierarchical Mixed-Effects, Quantile Regression, MonotoneHistGradientBoosting vs Incumbent Model A).
  - Benchmark Data: [`r07_challenger_results.json`](evidence/r07_challenger_results.json)
- **[`R08.md`](evidence/R08.md):** Calibrated 50% Likely Band ($P_{25}–P_{75}$) alongside 80% Plausible Range ($P_{10}–P_{90}$) with strict non-crossing guarantees ($1.0 \le P_{10} \le P_{25} \le P_{50} \le P_{75} \le P_{90}$).
- **[`R12.md`](evidence/R12.md):** Pure parameter serialization (`model_params.json`); elimination of runtime `pickle.load`; cryptographic SHA-256 verification.
- **[`R13.md`](evidence/R13.md):** Documentation and README architecture upgrade; establishment of startup-grade root README and docs master index.

### 3.3. Foundation Milestones (CP00 – CP26)
- **CP00–CP05 (Data Foundation):** Baseline isolation, contracts freeze, data acquisition, dataset harmonization (`projects_v2.csv`), and data leakage gates.
- **CP06–CP11 (Validated ML):** Actuals flywheel migration, 6-fold LOSO evaluation harness, Track 1 & 2 model architectures, and Mondrian split-conformal calibration.
- **CP12–CP17 (Serving & NLP):** SHA-256 artifact packaging, model sanity suite, honest v2 serving, calibrated NLP sizing cascade, and non-circular risk analysis.
- **CP18–CP24 (QA & Frontend):** Dead code pruning, CI hardening, high-contrast design system, 3-step estimation wizard, trust UX, and WCAG 2.1 AA accessibility.
- **CP25–CP26 (Release Candidate):** Truthful documentation overhaul and full multi-suite release verification.

---

## 4. Production Runbooks (`docs/runbooks/`)

Operational guides for engineering, DevOps, and ML administrators:

| Runbook | Purpose & Scope |
| :--- | :--- |
| **[`production-deployment.md`](runbooks/production-deployment.md)** | Production deployment checklist, container orchestration, environment variable configuration, and health check monitoring. |
| **[`PRODUCTION_ML.md`](runbooks/PRODUCTION_ML.md)** | Machine learning operations guide: model artifact packaging, SHA-256 checksum verification, retraining workflow, and rollback procedures. |
| **[`DEPLOYMENT_INPUTS.md`](runbooks/DEPLOYMENT_INPUTS.md)** | Exhaustive specification of required infrastructure inputs, database connection strings, and Firebase credentials. |
| **[`credential-rotation.md`](runbooks/credential-rotation.md)** | Step-by-step procedures for zero-downtime rotation of PostgreSQL passwords, JWT secrets, and API keys. |
| **[`add-team-member.md`](runbooks/add-team-member.md)** | Developer onboarding runbook: local development environment setup, database provisioning, and role assignment. |

---

## 5. Architectural Reviews & System Audits (`docs/`)

High-level system documentation and historical engineering audits:

| Document | Focus |
| :--- | :--- |
| **[`walkthrough.md`](walkthrough.md)** | Comprehensive architectural walkthrough of PredictIQ, detailing frontend components, backend services, and ML execution paths. |
| **[`PROJECT_MANDATE.md`](PROJECT_MANDATE.md)** | Foundational charter, scope boundaries, core philosophy, and quality expectations. |
| **[`PROJECT_STRUCTURE_MAP.md`](PROJECT_STRUCTURE_MAP.md)** | Exhaustive directory tree and component-to-module mapping. |
| **[`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md)** | Pre-flight release verification checklist covering linting, type safety, test suites, and remote branch safety. |
| **[`audit_report.md`](audit_report.md)** | Historical codebase audit and vulnerability remediation review. |
| **[`AWS_DEPLOYMENT.md`](AWS_DEPLOYMENT.md)** | Cloud infrastructure deployment guide for Amazon Web Services (ECS, RDS, S3). |
| **[`codebase_audit_2026-09-07.md`](codebase_audit_2026-09-07.md)** | Technical debt and code smell inventory conducted during early modernization. |
| **[`security_containment_2026-09-08.md`](security_containment_2026-09-08.md)** | Security posture review, secret containment, and vulnerability hardening history. |
| **[`ui_ux_improvements_2026-09-09.md`](ui_ux_improvements_2026-09-09.md)** | Design system evolution, color tokens, and accessibility improvements. |
| **[`validation_2026-09-15.md`](validation_2026-09-15.md)** | Early integration validation and end-to-end user journey tests. |
| **[`engineering_progress_2026-09-08.md`](engineering_progress_2026-09-08.md)** | Historical engineering sprint log. |
| **[`CURRENT_SETUP.md`](CURRENT_SETUP.md)** | Historical environment setup guide. |
| **[`SECRETS_ROTATION.md`](SECRETS_ROTATION.md)** | Legacy secrets rotation documentation. |
| **[`GITHUB_SECRETS_SETUP.md`](GITHUB_SECRETS_SETUP.md)** | Guide for configuring GitHub Actions repository secrets. |
| **[`ml_rebuild_2026-09-09.md`](ml_rebuild_2026-09-09.md)** | Early notes from the ML foundation rebuild initiative. |

---

*For project overview, quickstart instructions, and API references, see the root [README.md](../README.md).*
