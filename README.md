# PredictIQ v2.0

<div align="center">

[![Release](https://img.shields.io/badge/version-2.0.0-blue.svg?style=for-the-badge)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6.svg?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Conformal Coverage](https://img.shields.io/badge/Conformal_Coverage-80%25_Guaranteed-2ea44f.svg?style=for-the-badge)](#32-calibrated-conformal-uncertainty)
[![Zero-Pickle](https://img.shields.io/badge/Security-Zero_Pickle_Runtime-brightgreen.svg?style=for-the-badge)](#34-zero-pickle-security--pure-json-parameters)
[![License](https://img.shields.io/badge/License-Apache_2.0-orange.svg?style=for-the-badge)](LICENSE)

<br/>

**The modern, calibrated software effort and cost estimation platform built on empirical software engineering data and conformal prediction.**

[Explore Architecture](#4-core-architecture--data-flow) • [Dataset Provenance](#5-dataset-provenance--empirical-benchmarks) • [Quickstart Guide](#6-getting-started--quickstart-guide) • [API Contracts](#7-api-contracts--endpoints) • [Security & Compliance](#8-security--enterprise-compliance)

</div>

---

## 1. Project Vision

Software engineering estimation has historically been broken. For decades, the industry relied on subjective Delphi guessing, fabricated complexity multipliers (such as COCOMO-style $T01-T15$ adjustments), and black-box regression models reporting inflated $R^2$ values that failed completely in production.

**PredictIQ v2** fundamentally rebuilds software effort and cost prediction on rigorous, empirical foundations:
- **No Fabricated Math:** All synthetic adjustment factors and unverified heuristics have been purged.
- **Monotone Economic Reality:** System effort scales monotonically with functional scope ($\frac{\partial \text{Effort}}{\partial \text{Size}} > 0$). Larger projects never predict lower effort.
- **Finite-Sample Uncertainty Guarantees:** Instead of unreliable single-point estimates, PredictIQ generates rigorous, split-conformal prediction intervals with **guaranteed 80% plausible ranges ($P_{10}–P_{90}$)** and **50% likely bands ($P_{25}–P_{75}$)**.
- **Empirical Organization Adaptation:** Continuous learning from closed-loop project delivery actuals through Empirical Bayes shrinkage ($+19.5\%$ accuracy improvement at $k=10$ completed projects).
- **Hardened Supply Chain:** Zero `pickle.load` at runtime serving, pure JSON parameter storage, and fail-closed cryptographic SHA-256 parameter verification.

---

## 2. What Changed in v2.0.0

PredictIQ v2.0.0 represents a complete scientific and architectural overhaul from legacy estimation systems:

| Dimension | Legacy v1 / Conventional Tools | PredictIQ v2.0.0 |
| :--- | :--- | :--- |
| **Model Architecture** | Heuristic formulas with 27 synthetic features ($T01-T15$, $Transactions$, $Entities$) | Interpretable **Monotone Power-Law** ($E = a \cdot S^b$) with mathematically guaranteed sub-linear returns to scale |
| **Uncertainty Engine** | Single-point estimates or arbitrary symmetric $\pm 20\%$ heuristic bands | **Mondrian Split-Conformal Prediction** with non-crossing quantiles ($1.0 \le P_{10} \le P_{25} \le P_{50} \le P_{75} \le P_{90}$) |
| **Organizational Learning** | Static lookup tables or unweighted averages | **Empirical Bayes Hierarchical Shrinkage** adapting to company velocity using completed project actuals |
| **Model Runtime Security** | Vulnerable binary pickle files (`.pkl`) prone to arbitrary remote code execution | **Zero-Pickle Pure JSON** parameter serialization (`model_params.json`) with cryptographic SHA-256 verification |
| **Requirement Ingestion** | Manual feature count spreadsheets | **Calibrated Document NLP Cascade** parsing SRS/PRD documents (PDF, DOCX, TXT) with propagated size uncertainty |
| **User Experience** | Cluttered tables with uncalibrated dials | **Startup-Grade Accessible Dashboard** (React 19, Tailwind CSS) with interactive uncertainty visualization and trust modal |
| **Time Accounting** | Ambiguous, non-standardized calendar months | **152 productive working hours per person-month** (IEEE / industry standard) |

---

## 3. Core Technical Pillars

### 3.1. Interpretable Monotone Power-Law

In observational software engineering datasets, the relationship between functional scope $S$ (in IFPUG Function Points) and total effort $E$ (in productive person-hours) is governed by an empirical power-law:

$$E = a \cdot S^b$$

Taking natural logarithms yields the linear representation:

$$\ln E = \beta_0 + b \cdot \ln S$$

Where:
- $\beta_0 = 3.1880 \implies a = \exp(3.1880) \approx 24.24$
- $b = 0.8270$ ($95\%\text{ CI: } [0.778, 0.876]$)

Because $0 < b < 1$, the model reflects **economies of scale** observed in well-structured software architectures while strictly enforcing positive marginal effort ($\partial E / \partial S > 0$).

> [!NOTE]
> **Brooks' Law & Duration Ablation:** In Checkpoint R03, an empirical duration elasticity ablation ($N=561$) revealed that unrestricted multivariate regression yielded a positive duration exponent ($c = +0.5972$). Under positive elasticity, schedule compression (e.g., cutting timeline from 12 months to 6 months) would artificially reduce predicted effort by 34%, violating Brooks' Law and basic project economics. In accordance with the pre-registered protocol (`docs/contracts/evaluation_protocol_rc2.md`), **duration was rejected from the primary effort equation**. Effort is predicted strictly from functional size; planned duration is utilized exclusively for schedule feasibility and team staffing analysis.

---

### 3.2. Calibrated Conformal Uncertainty

PredictIQ avoids uncalibrated single-point guesses by implementing **Mondrian Size-Bucketed Split-Conformal Prediction**. Calibration offsets are computed on held-out empirical data across three functional size strata:

$$\text{Buckets: } \text{Small } (< 150\text{ FP}), \quad \text{Medium } (150 - 750\text{ FP}), \quad \text{Large } (> 750\text{ FP})$$

```text
Strata Offsets:
├── Small  (<150 FP):    q_80 = 1.1481  |  q_50 = 0.6073
├── Medium (150-750 FP): q_80 = 0.9561  |  q_50 = 0.5999
├── Large  (>750 FP):    q_80 = 1.1864  |  q_50 = 0.6565
└── Global Fallback:     q_80 = 1.0053  |  q_50 = 0.6004
```

This yields two nested, non-crossing estimation intervals:
1. **Outer Plausible Range ($P_{10}–P_{90}$):** Guaranteed 80% nominal coverage for risk management and maximum budget allocation.
2. **Inner Likely Band ($P_{25}–P_{75}$):** Calibrated 50% interquartile range for baseline sprint planning and target bids.

#### Propagated Requirement Size Uncertainty
When functional scope is extracted from natural language requirements (or when sizing uncertainty $[S_{p10}, S_{p90}]$ is provided), PredictIQ propagates sizing ambiguity directly into the conformal interval via log-space variance combination:

$$\Delta_s = \frac{\ln(S_{p90}) - \ln(S_{p10})}{2}$$

$$q_{\text{combined}} = \sqrt{q_{\text{bucket}}^2 + (b \cdot \Delta_s)^2}$$

Empirical simulation over 10,000 projects confirms that this formulation maintains **82.54% empirical coverage** ($\ge 80.0\%$ target) and guarantees strict quantile ordering:

$$1.0 \le P_{10} \le P_{25} \le P_{50} \le P_{75} \le P_{90}$$

---

### 3.3. Organization Actuals Shrinkage (Empirical Bayes)

Every software organization exhibits distinct productivity baselines depending on developer skill, tooling maturity, legacy debt, and architectural complexity. PredictIQ implements a **Hierarchical Empirical Bayes Shrinkage Estimator** that adapts to an organization's delivered project actuals without overfitting.

Let $r_{ij} = \ln(\text{Effort}_{ij}) - \ln(\hat{E}_{ij})$ be the log-residual for completed project $i$ in organization $j$, with sample mean residual $\bar{r}_j = \frac{1}{k} \sum_{i=1}^k r_{ij}$. The optimal shrinkage weight balancing the global prior against observed company actuals is:

$$w_k = \frac{k}{k + (\sigma^2 / \tau^2)} = \frac{k}{k + 2.83}$$

Where $\tau^2 \approx 0.187$ is between-organization variance and $\sigma^2 \approx 0.529$ is within-organization residual variance.

The organizational calibration multiplier $\gamma_{\text{org}}$ applied across all quantiles is:

$$\gamma_{\text{org}} = \exp\left(w_k \cdot \bar{r}_j\right), \quad \gamma_{\text{org}} \in [0.33, 3.00]$$

#### Empirical Performance Gains (6-Fold LOSO Evaluation):
- **$k = 0$ (Global Prior):** Macro MdAPE = $56.14\%$, PRED25 = $19.60\%$
- **$k = 3$ Completed Projects:** Macro MdAPE = $49.46\%$ (**$+11.89\%$ relative gain**)
- **$k = 5$ Completed Projects:** Macro MdAPE = $47.80\%$ (**$+14.85\%$ relative gain**)
- **$k = 10$ Completed Projects:** Macro MdAPE = $45.18\%$ (**$+19.52\%$ relative gain**, PRED25 = $28.30\%$)
- **$k = 20$ Completed Projects:** Macro MdAPE = $43.37\%$ (**$+22.76\%$ relative gain**, PRED25 = $29.89\%$)

---

### 3.4. Zero-Pickle Security & Pure JSON Parameters

Traditional Python machine learning deployments rely on Python `pickle` files (`.pkl`), which are vulnerable to arbitrary code execution if tampered with.

PredictIQ v2 completely purges pickle deserialization from the serving runtime path:
1. **Pure JSON Parameters:** Model architecture and weights are stored in clean JSON format at `backend/ml/artifacts/production_v2/model_params.json`.
2. **Cryptographic SHA-256 Verification:** On startup, the loader reads `manifest.json` and cryptographically verifies the SHA-256 hashes of all artifacts.
3. **Fail-Closed Runtime:** If parameter files are missing, malformed, or fail SHA-256 verification, backend initialization halts immediately. Zero deserialization of executable bytecode occurs.

---

### 3.5. Calibrated Document NLP Extraction

PredictIQ provides zero-shot natural language parsing of project documentation:
- Ingests **SRS, PRD, and RFP documents** in PDF, DOCX, and TXT formats (up to 10 MB).
- Identifies functional user stories, system actors, external API integrations, technical frameworks, and operational complexity.
- Translates extracted features into standardized IFPUG functional size metrics (~8 FP per core functional story, ~5 FP per external integration point).
- Emits an explicit **$\pm 15\%$ sizing uncertainty interval** ($P_{10}, P_{50}, P_{90}$) that flows directly into downstream conformal effort estimation.
- Assigns **Data Quality Tier B** to NLP-extracted scope, ensuring stakeholders clearly distinguish extracted estimates from user-verified functional specs (Tier A).

---

### 3.6. Modern Startup-Grade UI & Trust Experience

The PredictIQ frontend is built with **React 19**, **TypeScript**, and **Tailwind CSS**:
- **3-Step Estimation Wizard:** Seamless workflow from document upload or manual feature entry to parameter calibration and executive reporting.
- **Interactive Uncertainty Visualization:** High-contrast interval charts displaying both the 50% Likely Band ($P_{25}–P_{75}$) and 80% Plausible Range ($P_{10}–P_{90}$) with instant hours-to-person-months translation.
- **Model Transparency & Provenance Modal:** Complete disclosure of model version, SHA-256 artifact hash, training sample count ($N=915$), and cross-validation performance.
- **Out-of-Distribution (OOD) Diagnostics Card:** Transparent warnings when input sizes exceed the empirical domain ($> 4,100$ FP) or when schedule compression violates team productivity bounds.
- **Full WCAG 2.1 AA Compliance:** High-contrast dual-mode tokens (dark/light), full keyboard navigation, and semantic screen-reader landmarks.

---

## 4. Core Architecture & Data Flow

The following diagram illustrates the complete end-to-end estimation pipeline from requirement ingestion to calibrated executive reports:

```mermaid
flowchart TD
    subgraph Ingestion["1. Document & Parameter Ingestion"]
        Doc[Raw SRS / PRD / RFP Document\nPDF, DOCX, TXT <= 10MB] --> Parser[Text Extraction & Normalization]
        Parser --> NLP[NLP Cascade Extractor\nStories, Integrations, Stack]
        NLP --> Sizing[Functional Size\nS_p50 with ±15% Uncertainty]
        Manual[Manual Size / Specs\nUser Verified IFPUG FP] --> ManualSizing[Functional Size\nExact Point Size]
    end

    subgraph CoreML["2. Calibrated Machine Learning Engine"]
        Sizing --> SizeUncert[Log-Space Uncertainty Variance\nΔs = (ln S_p90 - ln S_p10) / 2]
        ManualSizing --> PowerLaw[Monotone Power-Law Engine\nln E = 3.1880 + 0.8270 ln S]
        SizeUncert --> PowerLaw
        PowerLaw --> Conformal[Mondrian Conformal Calibration\nq_combined = sqrt(q_bucket² + (b·Δs)²)]
        Conformal --> Quantiles[5 Non-Crossing Quantiles\nP10, P25, P50, P75, P90]
    end

    subgraph ActualsEngine["3. Empirical Bayes Adaptation"]
        DB[(estimate_actuals\nHistorical Completed Projects)] --> Filter[User Owned & Consented\nk <= 20 Projects]
        Filter --> EB[Empirical Bayes Estimator\nw_k = k / (k + 2.83)]
        EB --> Mult[Org Multiplier γ_org\nClipped to [0.33, 3.0]]
        Mult --> ApplyEB[Quantile Scaling\nE_calibrated = E_base · γ_org]
        Quantiles --> ApplyEB
    end

    subgraph BusinessTranslation["4. Schedule, Cost & Risk Translation"]
        ApplyEB --> EffortHours[Calibrated Effort Hours\nP10, P25, P50, P75, P90]
        EffortHours --> PM[Person-Months\n152 productive hours / PM]
        EffortHours --> CostCalc[Parametric Cost Calculation\nCost_p = Effort_p · Hourly Rate]
        EffortHours --> Risk[Downstream Risk Analyzer\nTeam Velocity & Feasibility]
    end

    subgraph Delivery["5. Client API & UI Presentation"]
        PM --> Contract[Frozen API Contract\napi_estimate_v2.json]
        CostCalc --> Contract
        Risk --> Contract
        Contract --> UI[React 19 Dashboard\nUncertainty Visualizer, Audit Log]
    end
```

---

## 5. Dataset Provenance & Empirical Benchmarks

PredictIQ v2 is trained on **915 verified software projects** harmonized from 6 independent historical empirical software repositories:

```text
Canonical Dataset: backend/ml/data/projects_v2.csv (915 rows)
Dataset SHA-256:   b05ad3b0111d4ed3ff89b7aa2a0f653e494f81953c701916f27756d1746eede3
```

### 5.1. Historical Source Repositories

| Repository | Projects ($N$) | Functional Sizing | Effort Unit | Domain | Audited Provenance Notes |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **China** | 499 | IFPUG AFP | Person-hours | Enterprise IT, Banking | PROMISE repository. Audited person-hours; verified that resource code is not confused with effort ($P_1 = 7,490$ hrs). |
| **Kitchenham** | 145 | IFPUG AFP | Person-hours | Banking & Retail | Audited commercial IT projects with consistent functional scope. |
| **AT&T Aptness** | 104 | IFPUG AFP | Person-hours | Telecommunications | Large-scale internal telecommunications systems from JSE literature. |
| **Desharnais** | 81 | IFPUG AFP | Person-hours | Canadian Business | Commercial applications with rigorous functional sizing. |
| **Maxwell** | 62 | IFPUG Size | Person-hours | Aerospace & Defense | European space agency applications; critical high-reliability domain diversity. |
| **Albrecht** | 24 | IFPUG FP | Person-hours | IBM Business IT | Foundational empirical software engineering dataset; $1,000 \times$ multiplier verified. |
| **Total** | **915** | **IFPUG FP** | **Person-hours** | **Global Cross-Domain** | **100% verified person-hours (0.32 to 95.14 h/FP; median 9.17 h/FP).** |

---

### 5.2. 6-Fold Leave-One-Source-Out (LOSO) Cross-Validation

To ensure true out-of-domain generalization, all models were evaluated by holding out an entire empirical source repository as the test set:

| Fold (Held-out Source) | Test Set Size ($N$) | Median Error (MdAPE) | Within 25% (PRED25) | Mean Absolute Error (MAE) |
| :--- | :---: | :---: | :---: | :---: |
| **China** | 499 | $60.84\%$ | $20.44\%$ | $2,780.2\text{ hrs}$ |
| **Kitchenham** | 145 | $59.24\%$ | $21.38\%$ | $3,581.4\text{ hrs}$ |
| **AT&T Aptness** | 104 | $58.66\%$ | $22.12\%$ | $4,120.9\text{ hrs}$ |
| **Desharnais** | 81 | $52.41\%$ | $16.05\%$ | $2,490.1\text{ hrs}$ |
| **Maxwell** | 62 | $37.50\%$ | $37.10\%$ | $5,640.8\text{ hrs}$ |
| **Albrecht** | 24 | $69.19\%$ | $4.17\%$ | $3,922.5\text{ hrs}$ |
| **Macro Average** | — | **$56.31\%$** | **$20.21\%$** | **$5,875.2\text{ hrs}$** |

---

### 5.3. Challenger Shootout & Pre-Registered Decision

Under the frozen evaluation protocol (`docs/contracts/evaluation_protocol_rc2.md`), challenger architectures were required to demonstrate a $\ge 3.0\%$ relative improvement in Macro MdAPE without sacrificing PRED25 non-inferiority:

| Model Architecture | Macro MdAPE (%) | Relative Gain (%) | Macro PRED25 (%) | Paired Wilcoxon $p$-value | Decision Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Model A: Monotone Power-Law (Incumbent)** | **56.31%** | **Baseline (0.00%)** | **20.21%** | $1.0000$ | **Retained (Production)** |
| **Model B: Hierarchical Mixed-Effects Log-Log** | 56.14% | +0.29% | 19.60% | $7.28 \times 10^{-17}$ | Rejected ($< 3.0\%$ gain threshold) |
| **Model D: QuantileRegression L1 Median** | 57.84% | -2.72% | 19.75% | $0.0182$ | Rejected (Inferior accuracy) |
| **Track 2: MonotoneHistGradientBoosting** | 56.49% | -0.33% | 20.05% | $0.7097$ | Rejected (Overfits within-source variance) |

**Scientific Takeaway:** Across heterogeneous software projects, non-linear tree models overfit idiosyncratic within-sample variance and fail to transfer to completely unseen development organizations. The parsimonious Monotone Power-Law delivers superior out-of-domain transfer and strict monotonicity.

---

## 6. Getting Started / Quickstart Guide

### 6.1. Prerequisites

- **Python 3.12+**
- **Node.js 20+** (LTS recommended)
- **PostgreSQL 15+** (or Neon Serverless Postgres)
- **Git**

---

### 6.2. Backend Setup & Run

1. **Clone the repository and enter directory:**
   ```bash
   git clone https://github.com/AtharvS7/PredictIQ.git
   cd PredictIQ
   ```

2. **Create and activate Python virtual environment:**
   ```bash
   # On Linux/macOS
   python3 -m venv .venv
   source .venv/bin/activate

   # On Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install pinned dependencies:**
   ```bash
   pip install -r backend/requirements.lock.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your DATABASE_URL and SECRET_KEY
   ```

5. **Run database migrations:**
   ```bash
   python backend/scripts/run_migration.py
   ```

6. **Start FastAPI development server:**
   ```bash
   uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   The backend API will be available at `http://localhost:8000`. Interactive OpenAPI documentation is accessible at `http://localhost:8000/docs`.

---

### 6.3. Frontend Setup & Run

1. **Navigate to the frontend directory and install dependencies:**
   ```bash
   cd frontend
   npm ci
   ```

2. **Start Vite development server:**
   ```bash
   npm run dev
   ```
   The application dashboard will open at `http://localhost:5173`.

---

### 6.4. Release Verification & Quality Gates

Run the comprehensive multi-suite verification suite to validate model integrity, type safety, test coverage, and security:

```bash
# Release pre-flight gate check
python scripts/release_gate.py

# Backend Pytest test suite (655+ tests)
pytest backend/tests -q --tb=short

# Python code quality & typing
ruff check backend/app backend/ml --select E,W,F,I --ignore E501,E402
mypy app/ --ignore-missing-imports --no-strict-optional --exclude 'ml/'

# Frontend Vitest test suite (130+ unit tests)
npm --prefix frontend test -- --pool=forks --no-file-parallelism --run

# Frontend TypeScript verification & production build
npm --prefix frontend run typecheck
npm --prefix frontend run build
```

---

## 7. API Contracts & Endpoints

All estimation endpoints strictly follow the frozen JSON schema defined in [`docs/contracts/api_estimate_v2.json`](docs/contracts/api_estimate_v2.json).

### 7.1. API Endpoints Table

| Method | Endpoint | Auth / Role | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/estimates/analyze` | `Editor` | Full estimation from uploaded document with NLP extraction and overrides |
| `POST` | `/api/v1/estimates/manual` | `Editor` | Direct estimation from user-supplied functional size and parameters |
| `GET` | `/api/v1/estimates` | `Viewer` | Paginated listing of estimates for authenticated user |
| `GET` | `/api/v1/estimates/{id}` | `Viewer` | Retrieve full estimate details including uncertainty intervals |
| `POST` | `/api/v1/estimates/{id}/duplicate` | `Editor` | Duplicate estimate as a new version |
| `POST` | `/api/v1/documents/upload-file` | `Editor` | Upload SRS/PRD file (PDF, DOCX, TXT <= 10MB) for parsing |
| `POST` | `/api/v1/estimates/{id}/actuals` | `Editor` | Submit delivered project actuals with training consent flag |
| `GET` | `/api/v1/estimates/{id}/actuals` | `Viewer` | Retrieve historical actuals for an estimate |
| `GET` | `/api/v1/actuals/export` | `Admin` | Export consented actuals into `projects_v2` format |
| `GET` | `/api/v1/health` | Public | Comprehensive readiness probe: DB connectivity, ML model, uptime |
| `GET` | `/api/v1/live` | Public | Lightweight process liveness probe |

---

### 7.2. Sample Estimate Contract (`api_estimate_v2.json`)

```json
{
  "estimate_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "project_name": "Healthcare Claims Portal",
  "effort_hours": {
    "p10": 1150.0,
    "p25": 1420.0,
    "p50": 1820.0,
    "p75": 2340.0,
    "p90": 2940.0
  },
  "person_months": {
    "p10": 7.57,
    "p25": 9.34,
    "p50": 11.97,
    "p75": 15.39,
    "p90": 19.34
  },
  "cost": {
    "p10": 86250.0,
    "p25": 106500.0,
    "p50": 136500.0,
    "p75": 175500.0,
    "p90": 220500.0,
    "currency": "USD",
    "rate": 75.0
  },
  "size": {
    "value": 185.0,
    "source": "nlp",
    "uncertainty": {
      "p10": 157.2,
      "p50": 185.0,
      "p90": 212.8
    }
  },
  "data_quality_tier": "B",
  "ood_flags": [],
  "nominal_interval_coverage": 0.8,
  "confidence_pct": 80.0,
  "org_calibration": {
    "applied": true,
    "k_actuals": 5,
    "shrinkage_weight": 0.639,
    "multiplier": 1.084
  },
  "model": {
    "version": "2.0.0",
    "sha256": "b05ad3b0111d4ed3ff89b7aa2a0f653e494f81953c701916f27756d1746eede3",
    "trained_on_rows": 915,
    "sources": ["china", "desharnais", "kitchenham", "maxwell", "albrecht", "att_aptness"],
    "metrics_ref": "docs/MODEL_VALIDATION_SUMMARY.md"
  }
}
```

---

## 8. Security & Enterprise Compliance

PredictIQ is engineered for enterprise security and strict regulatory compliance:

- **Zero-Pickle Serving Runtime:** Production model serving relies exclusively on pure JSON parameter dictionaries (`model_params.json`). No untrusted Python object deserialization can occur.
- **Fail-Closed Cryptographic Verification:** Artifact loader verifies SHA-256 hashes against `manifest.json`. Tampered or missing parameter files abort startup automatically.
- **Role-Based Access Control (RBAC):** Granular permission enforcement across three standardized roles:
  - `Viewer`: Read-only access to estimates and dashboards.
  - `Editor`: Creation, editing, and execution of estimates; document uploads.
  - `Admin`: Full access, user role synchronization, and actuals dataset export.
- **Input Sanitization & Injection Defense:** All user inputs (project names, notes, requirements) are sanitized against XSS, HTML injection, and control character attacks prior to storage.
- **OWASP Hardened Headers:** Every API response includes `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, and strict `Permissions-Policy`.
- **DDoS & Brute-Force Rate Limiting:** Powered by SlowAPI to defend against denial-of-service and credential stuffing attacks.
- **Audit Logging for SOC 2:** Async middleware captures all API interactions with timestamps, authenticated caller IDs, and unique `X-Request-ID` tracing tokens.
- **Data Privacy & Actuals Opt-in:** Completed project actuals are never used for model adaptation without explicit boolean consent (`consent_for_training = true`). Multi-tenant data isolation ensures organizations only calibrate against their own delivered projects.

---

## 9. Documentation Map

PredictIQ maintains a comprehensive documentation suite in the [`docs/`](docs/) directory:

- **[Documentation Index (`docs/README.md`)](docs/README.md):** Complete catalog and navigation map of all project documentation.
- **[Formal Contracts (`docs/contracts/`)](docs/contracts/):** Frozen JSON schemas, ML contracts, and evaluation protocols.
- **[Data Registry & Provenance (`docs/data/`)](docs/data/):** Dataset datasheets, deduplication reports, source registers, and ISBSG roadmap.
- **[Scientific Evidence & Audit Trails (`docs/evidence/`)](docs/evidence/):** Checkpoint logs (CP00–CP26, R00–R13), ablation studies, and simulation records.
- **[Production Runbooks (`docs/runbooks/`)](docs/runbooks/):** Deployment guides, credential rotation, ML operations, and security procedures.

---

## 10. License & Citation

PredictIQ is open-source software licensed under the **Apache License 2.0**.

If you use PredictIQ's empirical models, dataset harmonization, or conformal calibration in your research or commercial organization, please cite:

```bibtex
@software{predictiq2026,
  author = {PredictIQ Team},
  title = {PredictIQ v2: Calibrated Software Effort and Cost Estimation via Monotone Power-Laws and Split-Conformal Prediction},
  year = {2026},
  url = {https://github.com/AtharvS7/PredictIQ}
}
```
