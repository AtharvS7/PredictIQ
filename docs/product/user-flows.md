# PredictIQ User Flows & Journeys

Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

---

## 1. Overview of Core User Journeys

PredictIQ provides structured, accessible workflows for engineering leaders, project managers, and finance officers. This document details the five primary user journeys through the application:

```mermaid
flowchart TD
    Start(["User Lands on Platform"]) --> Auth{"Authenticated?"}
    Auth -- "No" --> Journey0["Sign In / Registration Flow"]
    Auth -- "Yes" --> Nav{"Select Destination"}

    Nav --> J1["1. Estimation Wizard Flow"]
    Nav --> J2["2. Results & Transparency Flow"]
    Nav --> J3["3. Actuals Flywheel Flow"]
    Nav --> J4["4. History & Archive Flow"]
    Nav --> J5["5. Settings & Profile Flow"]

    J1 --> J2
    J2 --> J3
    J2 --> J4
```

---

## 2. Journey 1: Estimation Wizard Flow

The Estimation Wizard guides users through project scoping and parameter configuration in three structured stages:

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as Frontend (Vite/React)
    participant Store as estimateStore (Zustand)
    participant Backend as FastAPI Backend
    participant Parser as Isolated Parser Subprocess
    participant Engine as ML Inference Engine

    User->>Frontend: Select "New Estimate"
    alt Document Upload Route
        User->>Frontend: Upload SRS (.pdf, .docx, .txt)
        Frontend->>Backend: POST /api/v1/documents/upload
        Backend->>Parser: Parse & Extract Text (Timeout: 15s)
        Parser-->>Backend: Clean Text Preview + Scope Candidates
        Backend-->>Frontend: Return Document ID & Extracted Parameters
    else Direct Sizing Route
        User->>Frontend: Enter Functional Size directly (Function Points)
    end

    User->>Frontend: Review & Adjust Parameters (Step 2)
    Note over User,Frontend: Adjust Team Size, Planned Duration, Hourly Rate, Tech Stack, Volatility
    User->>Frontend: Click "Generate Calibrated Estimate"
    Frontend->>Store: Set Loading State
    Frontend->>Backend: POST /api/v1/estimates/analyze (or /manual)
    Backend->>Engine: Run Monotone Power Law + Mondrian Calibration
    Engine-->>Backend: Return P10–P90, P25–P75, Risk, Phases, OOD Diagnostics
    Backend-->>Frontend: HTTP 200 EstimateResult JSON
    Frontend->>Store: Hydrate Current Estimate
    Frontend->>User: Route to /results/:estimateId
```

### Detailed Steps:
1. **Scope Intake (Step 1):**
   - The user selects either document-driven analysis or direct manual entry.
   - For document intake, the user drops a specification file (max 10 MB). The client validates file extensions and mime types before dispatching to `/api/v1/documents/upload`.
   - The backend validates magic bytes, verifies archive safety, and extracts text in an isolated worker subprocess.
2. **Parameter Refinement (Step 2):**
   - The user reviews extracted attributes and overrides values where necessary:
     - **Project Type:** Web App, Mobile App, API / Backend, Enterprise System, Data Platform, IoT / Embedded.
     - **Functional Size:** Function Points (FP) derived from document analysis or manually entered.
     - **Team & Schedule:** Team size (1–100 engineers) and optional target duration (1–60 months).
     - **Complexity & Risk Factors:** Integration count (0–15), requirements volatility (1–5), team experience level (1.0–4.0), and methodology (Agile, Waterfall, Hybrid).
     - **Financial Parameters:** Hourly labor rate (USD 10–500/hr) defaulted from user profile.
3. **Execution & Routing (Step 3):**
   - Clicking "Generate Estimate" sends an immutable payload to `/api/v1/estimates/analyze`.
   - The backend computes calibrated quantiles, phase breakdowns, and risk flags, persists the record to PostgreSQL, and redirects to the Results view.

---

## 3. Journey 2: Results Exploration & Analysis

The Results view serves as the comprehensive decision center for a generated estimate:

```mermaid
flowchart TD
    R0["Results Page Loaded"] --> R1["Top Bar: Project Name, Timestamp, Version"]
    R1 --> R2["Model Transparency Modal Trigger"]
    R1 --> R3["Key Metrics Cards"]

    R3 --> M1["Effort Card: P50 Median Hours & Person-Months"]
    R3 --> M2["Cost Card: Likely Cost in Active Currency"]
    R3 --> M3["Timeline Card: Likely Duration in Weeks"]

    R0 --> R4["Calibrated Confidence Interval Display"]
    R4 --> C1["P25–P75 Likely Band: Operational Focus"]
    R4 --> C2["P10–P90 Plausible Range: Risk Envelope"]

    R0 --> R5["Out-of-Distribution (OOD) Diagnostics Card"]
    R0 --> R6["Functional Size Breakdown Card"]
    R0 --> R7["Interactive Lifecycle Phase Breakdown"]
    R0 --> R8["Export & Sharing Actions"]
```

### Key Interactive Elements:
- **Model Transparency Modal:** Clicking the info badge reveals the cryptographic model lineage, training dataset SHA-256 (`b05ad3...`), manifest hash, sample count (915 projects), and Mondrian bucket cutoff points.
- **Calibrated Intervals:** The `ConfidenceInterval` visualizer displays the relationship between median effort ($P_{50}$), the inner 50% likely operating band ($P_{25}$–$P_{75}$), and the outer 80% plausible range ($P_{10}$–$P_{90}$).
- **OOD Diagnostics:** If project parameters fall outside empirical training envelopes, warning badges explain that intervals widen naturally to reflect epistemic uncertainty.
- **Export & Share Controls:**
  - **Generate Share Link:** Creates an expirable, password-protected public URL (`/shared/:token`).
  - **Download JSON:** Emits the full contract-compliant JSON payload for automated toolchains.
  - **Download Executive PDF:** Produces an audit-ready summary for client and executive presentations.

---

## 4. Journey 3: Actuals Flywheel Flow

The Actuals Flywheel enables continuous organizational learning by capturing real-world project outcomes:

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as Frontend
    participant Backend as FastAPI Backend
    participant DB as PostgreSQL (Neon)
    participant ML as ML Service

    User->>Frontend: Navigate to "Record Actuals" from Estimate
    User->>Frontend: Enter Final Actual Effort (e.g., 1,420 hours)
    User->>Frontend: Enter Final Cost, Duration, and Delivered Size
    User->>Frontend: Toggle "Consent for Model Training" (Opt-In)
    User->>Frontend: Submit Actuals Form
    Frontend->>Backend: POST /api/v1/actuals/
    Backend->>DB: INSERT INTO estimate_actuals
    DB-->>Backend: Confirmed Stored Record
    Backend-->>Frontend: HTTP 201 Created
    Note over Backend,ML: Subsequent estimates for this user/org load prior actuals
    User->>Frontend: Request New Estimate
    Frontend->>Backend: POST /api/v1/estimates/analyze
    Backend->>ML: Evaluate Shrinkage w_k = k / (k + 2.83)
    ML-->>Backend: Return Calibrated Quantiles with Org Multiplier
    Backend-->>Frontend: HTTP 200 with org_calibration Metadata
    Frontend->>User: Display Calibrated Estimate with Shrinkage Pill
```

### Flow Details:
1. **Entry Point:** Users access the actuals form from any completed estimate in their history.
2. **Data Logging:** The form captures total verified person-hours, final invoice cost, actual elapsed calendar months, and delivered functional size.
3. **Training Consent:** Users can optionally opt in to anonymous model retraining.
4. **Bayesian Shrinkage Trigger:** Once logged, subsequent estimates for the organization query historical actuals, calculating an empirical Bayes adjustment factor that calibrates global baseline predictions toward internal delivery speed.

---

## 5. Journey 4: Estimates History & Archive

The Estimates archive provides central management, filtering, and comparison across all historic estimates:

```mermaid
flowchart TD
    H0["Open /estimates Dashboard"] --> H1["Fetch Paginated Estimates"]
    H1 --> H2["Render Overview Table"]

    H2 --> F1["Search by Project Name"]
    H2 --> F2["Filter by Project Type"]
    H2 --> F3["Sort by Date, Cost, or Risk"]

    H2 --> A1["Row Action: View Results Page"]
    H2 --> A2["Row Action: Duplicate & Re-Estimate"]
    H2 --> A3["Row Action: Generate Share Link"]
    H2 --> A4["Row Action: Delete Estimate"]
```

### Table Columns and Actions:
- **Project Name & Version:** Identifies the project and iteration count.
- **Type & Tech Stack:** Displays categorized stack pills.
- **Likely Cost & Effort:** Formatted in the currently active currency and hours.
- **Risk Badge:** Color-coded indicator (Green: Low, Blue: Medium, Amber: High, Red: Critical).
- **Date Created & Updated:** Formatted timestamps with relative display.
- **Batch Operations:** Export selected estimates to CSV or JSON summary formats.

---

## 6. Journey 5: Settings & Profile Flow

The Settings page enables users to tailor organizational defaults, display parameters, and localization:

```mermaid
flowchart TD
    S0["Open /settings Page"] --> S1["Fetch User Profile via GET /api/v1/profile"]
    S1 --> S2["Render Settings Tabs"]

    S2 --> T1["Profile Information: Full Name, Email, Avatar"]
    S2 --> T2["Financial Defaults: Default Hourly Rate ($/hr)"]
    S2 --> T3["Localization: Default Currency (USD, EUR, GBP, CAD, AUD, INR)"]
    S2 --> T4["Appearance: Light, Dark (Obsidian), or System Theme"]

    T1 & T2 & T3 & T4 --> Save["Click 'Save Changes'"]
    Save --> PUT["PUT /api/v1/profile"]
    PUT --> Sync["Synchronize Local Zustand Stores & Apply Dark Theme"]
```

### Profile Attributes Configured:
- **Hourly Billing Rate:** Used as the initial pre-filled rate for all new estimates.
- **Base Currency:** Controls the primary currency used for cost calculations and reports.
- **Theme Selection:** Toggles between High-Contrast Light Mode and Obsidian Dark Mode instantly via the CSS theme provider.
- **Timezone:** Standardizes timestamp presentation across shared links and export documents.
