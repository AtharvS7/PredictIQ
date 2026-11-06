# Datasheet for Dataset: PredictIQ projects_v2

*Following the framework proposed by Gebru et al. in "Datasheets for Datasets" (CACM 2021).*

---

## 1. Motivation

- **For what purpose was the dataset created?**  
  The `projects_v2.csv` dataset was created to provide a clean, harmonized, leakage-free benchmark foundation for empirical software effort estimation models in PredictIQ v2. It replaces the revoked `predictiq_merged_dataset.csv`, which suffered from 481 corrupted target labels, fabricated synthetic features (`T01-T15`, `Transactions`, `Entities`, `PointsNonAdjust`, `Adjustment`, `TeamExp`, `ManagerExp`), and severe train/serve skew.
- **Who created the dataset?**  
  Assembled and verified by the PredictIQ engineering team via `backend/ml/rebuild_dataset.py`, sourcing public academic and empirical software engineering repositories (Promise, SEERA, JSE).
- **Who funded the creation of the dataset?**  
  PredictIQ internal engineering / Open source academic contributions.

---

## 2. Composition

- **What do the instances that comprise the dataset represent?**  
  Each instance represents a completed software engineering project with recorded functional size (Function Points), total effort expended in person-hours, and where available, project duration, delivery platform, programming language, and development year.
- **How many instances are there in total?**  
  Exactly **915 completed software projects** across 6 distinct empirical sources.
- **Breakdown by source:**
  1. **China (499 projects, 54.5%)**: Commercial and government IT software projects collected from Chinese software organizations (1995–2008).
  2. **Kitchenham (145 projects, 15.8%)**: Commercial software maintenance and enhancement projects collected by Barbara Kitchenham (1979–1990).
  3. **AT&T Aptness (104 projects, 11.4%)**: Corporate data center and infrastructure development projects from AT&T Bell Labs / business units (1986–1991).
  4. **Desharnais (81 projects, 8.9%)**: Commercial business applications collected by Jean-Marc Desharnais in Canada (1980s).
  5. **Maxwell (62 projects, 6.8%)**: Mission-critical and engineering projects from European space/aerospace organizations collected by Katrina Maxwell (1980s–1990s).
  6. **Albrecht (24 projects, 2.6%)**: Historical baseline projects from IBM DP Services collected by Allan Albrecht and John Gaffney (1970s).
- **Does the dataset contain all possible instances or is it a sample?**  
  It contains all complete, verified instances from the 6 approved academic and industry sources that report both functional size (Function Points) and effort in work-hours.
- **What data does each instance consist of?**
  - `project_id` (string, unique): Source-prefixed identifier (e.g. `china_001`, `att_042`).
  - `source` (string, categorical): One of `china`, `kitchenham`, `desharnais`, `maxwell`, `albrecht`, `att_aptness`.
  - `year` (integer, nullable): Completion year (1982–1988 where available).
  - `size_value` (float): Functional size in IFPUG/COSMIC compatible Function Points.
  - `size_unit` (string): Always `"FP"`.
  - `effort_hours` (float): Total person-hours expended.
  - `duration_months` (float, nullable): Calendar elapsed time in months.
  - `team_size` (float, nullable): Mean or peak team members.
  - `platform` (string, nullable): Operating environment (e.g., `"MVS"`, `"Unix"`, `"IBM Mainframe"`).
  - `language` (string, nullable): Implementation language (e.g., `"COBOL"`, `"C"`, `"PLI"`).
  - `dev_type` (string, nullable): Project typology.
  - `notes` (string): Provenance notes and citation references.
- **Are there any confidential, sensitive, or personally identifiable data (PII)?**  
  No. All project records originate from anonymized public academic datasets. No names, company proprietary source code, or private credentials are included.

---

## 3. Collection Process

- **How was the data associated with each instance acquired?**  
  Data was downloaded and verified directly from authoritative public archives (Promise Software Engineering Repository, Journal of Statistics Education, Zenodo) using the deterministic script `backend/ml/acquire_all.py`.
- **What mechanisms were used to collect the data?**  
  HTTP GET requests with SHA-256 integrity checksum verification.
- **Who was involved in the collection process?**  
  Empirical software engineering researchers (Albrecht, Kitchenham, Desharnais, Maxwell, Menzies, Stutzke).

---

## 4. Preprocessing and Cleaning

- **What was done to clean or prepare the data?**
  1. **China Dataset Label Restoration**: Fixed the critical flaw where China project 1 had `Effort=4.0` (which was the Resource categorization index); restored genuine recorded `Effort=7490.0` work-hours.
  2. **Albrecht Unit Standardisation**: Multiplied raw `Effort` values by `1000.0`, reflecting Albrecht & Gaffney (1983)'s documentation that effort was recorded in thousands of work-hours (e.g., raw 4.9 = 4,900 hours).
  3. **AT&T Aptness Column Realignment**: Cleaned 5-column whitespace format (`size_fp`, `effort_hours`, `os`, `dbms`, `language`) eliminating column shifting.
  4. **Fabricated Feature Elimination**: Dropped all synthetic features (`T01-T15`, `Transactions`, `Entities`, `PointsNonAdjust`, `Adjustment`, `TeamExp`, `ManagerExp`) that were previously imputed from `size_fp` and complexity heuristics.
  5. **Deduplication Audit**: Audited within-source and cross-source duplicates. Confirmed zero duplicate project IDs and zero duplicate tuples across disjoint sources.

---

## 5. Uses

- **What are the intended tasks?**  
  - Supervised training of software effort estimation models (parametric power-law regressions, gradient boosted decision trees).
  - Evaluating cross-organization generalization via Leave-One-Source-Out (LOSO) cross-validation.
  - Calibrating prediction intervals (e.g., conformal prediction p10, p50, p90).
- **Is there anything about the composition of the dataset that might impact future uses?**  
  - **Historical Bias**: The datasets were collected primarily between 1979 and 2008. While functional sizing physics (power-law relationship between functional complexity and human effort) remains empirically valid, modern tooling (cloud infrastructure, AI-assisted development, continuous deployment) exhibits higher median productivity than historical averages.
  - **Language Representation**: Predominance of 3GL/4GL legacy languages (COBOL, C, PL/I, 4GL) relative to modern cloud-native stacks (TypeScript, Go, Rust, Python).
- **What tasks should the dataset NOT be used for?**  
  - **Individual Developer Assessment**: Must never be used to evaluate, rank, or discipline individual engineers or team members.
  - **Micro-task / Hourly Time Tracking**: The models predict aggregate macro-project lifecycle effort, not daily task ticket durations.
  - **Fabricating Inputs**: Downstream serving systems must not fabricate missing inputs; missing covariates must remain `None`.

---

## 6. Distribution & Maintenance

- **How is the dataset distributed?**  
  The dataset is located at `backend/ml/data/projects_v2.csv` with SHA-256 checksum:
  `b05ad3b0111d4ed3ff89b7aa2a0f653e494f81953c701916f27756d1746eede3`.
- **How will the dataset be updated?**  
  Future expansion paths include licensed ISBSG commercial releases (detailed in `docs/data/ISBSG_PLAN.md`) and modern open-source repository telemetry via the actuals flywheel.
