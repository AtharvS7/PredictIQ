Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# PredictIQ Frontend Design & Quality Review (Release Candidate 3)

**Document:** `docs/design/REVIEW_RC3.md`  
**Checkpoint:** `S07` (Frontend Quality & Responsive Review)  
**Program:** `PREDICTIQ_RC3_PORTABILITY_VALIDITY_DOCS_PROGRAM`  
**Role:** Frontend Quality & Review Engineer (`WS_FE`)  
**Date:** 2026-11-08  
**Branch:** `dev3`  
**Status:** **PASS**

---

## 1. Executive Summary

This document presents the comprehensive visual design, responsive layout, dark mode, accessibility, and statistical reality audit conducted for PredictIQ Release Candidate 3 (RC3).

The primary objective of Checkpoint S07 is to guarantee that every authenticated and public frontend surface truthful conveys the statistical and mathematical reality of the underlying machine learning engine:
1. **Effort depends strictly on functional size (`size_fp`)** via the production Monotone Power-Law ($E = a \cdot S^b$).
2. **Team size and duration are clearly labeled as schedule and staffing capacity planning indicators, NOT effort predictors** (Brooks' Law).
3. **Both the 50% Likely Band (P25–P75) and 80% Plausible Range (P10–P90) are presented with their measured empirical coverage text** (51.2% measured coverage and 79.0% holdout pooled coverage).
4. **Plain-language uncertainty disclaimers are prominent** (e.g. "typical error is roughly ±50% on novel projects").
5. **Assumption badges are visible for NLP functional sizing** (~8 FP/feature, ~5 FP/integration, ±15% propagated size uncertainty).
6. **Consented project actuals logging and empirical Bayes shrinkage calibration status are exposed and actionable**.

All 24 test suites (132 tests) pass, TypeScript strict typecheck passes with 0 errors, and the production build compiles cleanly without warnings.

---

## 2. Statistical Reality & Scientific Rigor Review

| Requirement | Statistical Reality | UI Presentation & Implementation | Status |
| :--- | :--- | :--- | :---: |
| **1. Primary Effort Model** | Production model is strictly size-only Monotone Power-Law: $E = a \cdot S^b$. Duration was ablated in R03 ($c = +0.5972$) because positive elasticity violates Brooks' Law (compressing schedule would spuriously decrease effort). | Prominently displayed in `FunctionalSizeCard.tsx`, `ModelTransparencyModal.tsx`, `EstimationResultView.tsx`, and `ResultsPage.tsx`. Removed misleading label of multivariate duration formula as "Primary Engine". | **PASS** |
| **2. Capacity vs Effort Labeling** | Planned Duration ($D$) and Team Size ($T$) compute target capacity ($H = 152 \cdot T \cdot D$) and run-rate budget ($B = H \cdot R$). They do not drive or alter predicted effort hours. | Labeled as "Schedule Planning Horizon" and "Staffing Capacity Indicator (Brooks' Law)" across `PlanningCapacityCard.tsx`, `NewEstimatePage.tsx`, `EstimationResultView.tsx`, and `ResultsPage.tsx`. | **PASS** |
| **3. Dual Calibrated Ranges** | Split-conformal Mondrian intervals guarantee valid finite-sample coverage: Outer 80% Plausible Range (P10–P90, nominal 80%) and Inner 50% Likely Band (P25–P75, nominal 50%). | Both bands presented with measured empirical coverage text: `50% Likely Band (Inner) [51.2% measured coverage]` and `80% Plausible Range (Outer) [79.0% holdout pooled coverage]`. | **PASS** |
| **4. Plain-Language Uncertainty** | Software decision-makers need plain-language guidance rather than pure mathematical quantile terminology. | Added uncertainty guidance: "Typical estimation error is roughly ±50% on novel projects. Use 50% Likely Band for sprint planning and 80% Plausible Range for budget caps." | **PASS** |
| **5. NLP Assumption Badges** | NLP specification parsing uses heuristic functional extraction: ~8 FP per user story and ~5 FP per external API, with ±15% sizing variance propagated into effort intervals. | Rendered explicit assumption badges on `FunctionalSizeCard.tsx` and result views: `Assumption: ~8 FP/Story`, `Assumption: ~5 FP/API`, `NLP Size Uncertainty: ±15%`. | **PASS** |
| **6. Empirical Bayes & Actuals** | Organizations log delivered actuals with explicit consent; shrinkage adapts velocity: $w_k = k / (k + 2.83)$, achieving $+19.52\%$ error reduction at $k=10$. | Rendered `EB Shrinkage: k=...` or `EB Prior: Global` badge with tooltip on estimates, full settings explanation, and admin CSV/JSON export actions. | **PASS** |

---

## 3. Responsive & Dark Mode Audit Notes

### 3.1. Mobile Viewport (360px Width)
- **Target Devices:** Small phones (e.g. iPhone SE, compact Android, 360x640px).
- **Layout & Overflow:** Fixed padding replaced with fluid CSS `clamp(1rem, 3vw, 2rem)`. `overflow-x: hidden` and `max-width: 100vw` prevent accidental horizontal viewport blowing.
- **Navigation:** Fixed 5-destination bottom rail on mobile (`.workspace-bottom-nav`) replaces the wide sidebar. Navigation touch targets maintain $\ge 44\text{px}$ height with accessible focus outlines.
- **Controls & Modals:** Action buttons wrap into multi-line rows (`flex-wrap: wrap; gap: 8px`). Modals utilize `max-h-[90vh]` with internal scroll and backdrop blur.

### 3.2. Tablet Viewport (768px Width)
- **Target Devices:** Tablets (e.g. iPad portrait, 768x1024px).
- **Layout Grid:** 2-column and 3-column metric grids adapt cleanly without orphaned elements (`grid-template-columns: repeat(auto-fit, minmax(min(100%, 200px), 1fr))`).
- **Sidebar Integration:** Collapsed sidebar mode allows full tablet screen width utilization while maintaining accessible keyboard expand/collapse controls.

### 3.3. Desktop Viewport (1280px+ Width)
- **Target Devices:** Desktop monitors and widescreen displays.
- **Max-Width Containers:** Page content is bounded to readable maximum widths (`max-width: 1100px` for results/dashboard, `900px` for wizard), preventing stretched wide-line typography.
- **Data Density:** High-density summary cards, multi-format chart switchers (Bar, Polar, Pie, Line), and interactive modals.

### 3.4. Dark Mode & Accessibility (WCAG AA)
- **Theme Tokens:** Strict adherence to semantic CSS variables (`var(--bg-primary)`, `var(--bg-surface)`, `var(--bg-elevated)`, `var(--text-primary)`, `var(--text-secondary)`, `var(--border-color)`).
- **Obsidian Palette:** Dark theme utilizes rich `#090D16` and `#1E293B` surfaces with high-contrast text (`#F1F5F9`, `#94A3B8`). Jarring pure white hardcoded backgrounds in header and dropdown menus were eliminated.
- **Color Semantics:** Low risk uses emerald (`#10B981`), medium risk uses amber (`#F59E0B`), high/critical risk uses rose/red (`#EF4444`). Confidence intervals use a calibrated green-to-blue-to-amber spectrum.

---

## 4. Audited Surfaces & Detailed Findings

### 4.1. Landing Page (`LandingPage.tsx`)
- **Review:** Hero section, methodology walkthrough steps, call-to-action buttons, and footer.
- **Findings:**
  - *Defect:* Footer contained outdated branding: `"© 2026 Predictify. Know Before You Build."`
  - *Remediation:* Updated footer to `"© 2026 PredictIQ. Know Before You Build."`. Updated hero copy to highlight the Monotone Power-Law model, dual conformal ranges (P25–P75 and P10–P90), and typical ±50% novel project uncertainty.

### 4.2. Dashboard (`DashboardPage.tsx`)
- **Review:** Welcome banner, quick-action cards, metric readouts, and recent estimate history.
- **Findings:**
  - Fluid padding handles long project titles without breaking flex layout (`minWidth: 0; overflowWrap: 'anywhere'`).
  - Welcome banner highlights PredictIQ v2 calibrated architecture.
  - Empty states render accessible illustrations and actions.

### 4.3. New Estimate Wizard (`NewEstimatePage.tsx`, `FunctionalSizeCard.tsx`, `PlanningCapacityCard.tsx`)
- **Review:** Step progress indicator, document dropzone, manual input parameters form, and reactive capacity card.
- **Findings:**
  - *Defect:* Step 2 inputs labeled Team Size and Duration without clarifying their status as capacity indicators.
  - *Remediation:* Added helper text: `"Staffing capacity indicator (Brooks' Law: does not shorten effort)"` and `"Target planning horizon (effort depends strictly on functional size)"`.
  - Added assumption badges to `FunctionalSizeCard.tsx` when scope is extracted via NLP (`Assumption: ~8 FP/Story`, `Assumption: ~5 FP/API`, `NLP Size Uncertainty: ±15%`).
  - Re-stated the statistical reality that effort depends strictly on functional size (`size_fp`).

### 4.4. Results View (`ResultsPage.tsx`, `EstimationResultView.tsx`, `ConfidenceInterval.tsx`)
- **Review:** Primary confidence range bar, quantiles summary boxes, phase breakdown chart, input parameters audit, and export toolbar.
- **Findings:**
  - *Defect:* Uncertainty spread banner only stated "50% Likely Band (Inner) • 80% Plausible Range (Outer)" without citing measured empirical coverage.
  - *Remediation:* Updated `ConfidenceInterval.tsx`, `EstimationResultView.tsx`, and `ResultsPage.tsx` to display:
    `50% Likely Band (Inner) [51.2% measured coverage] • 80% Plausible Range (Outer) [79.0% holdout pooled coverage]`.
  - Added plain-language uncertainty disclaimers:
    `Typical estimation error is roughly ±50% on novel projects prior to empirical Bayes shrinkage. Use the 50% Likely Band (P25–P75) for sprint planning and expected delivery milestones, and the 80% Plausible Range (P10–P90) for contractual budget caps and governance risk reserves.`
  - Clarified Input Parameters card with explanatory note:
    `Effort depends strictly on Functional Size (size_fp); Team Size and Duration are planning capacity indicators (Brooks' Law).`

### 4.5. Model Transparency Modal (`ModelTransparencyModal.tsx`)
- **Review:** Architecture section, feature elimination statement, cited benchmark datasets, conformal calibration methodology, and EB shrinkage details.
- **Findings:**
  - *Defect (High Severity):* Displayed `MultivariateMonotoneModel` ($E = a \cdot S^b \cdot D^c$) as "Primary Engine" and `MonotonePowerLaw` ($E = a \cdot S^b$) as "Size-Only Fallback".
  - *Remediation:* Corrected `ModelTransparencyModal.tsx` so that `MonotonePowerLaw` is presented as the primary production engine, and `MultivariateMonotoneModel` is documented as the ablated candidate from Checkpoint R03, explaining that positive duration elasticity ($c = +0.5972$) violates Brooks' Law by spuriously shrinking effort under schedule compression.
  - Added measured coverage citations: 79.0% holdout pooled coverage for 80% Plausible Range, and 51.2% measured coverage for 50% Likely Band.

### 4.6. Project History (`EstimatesPage.tsx`)
- **Review:** Search input, project type and sort filter dropdowns, estimate summary table, pagination, and action controls.
- **Findings:**
  - Project title links use `minWidth: 0` and word-break wrapping to avoid clipping on 360px screens.
  - Delete and Duplicate action buttons provide touch targets $\ge 44\text{px}$ with accessible aria labels (`aria-label="Duplicate Project Name"`).

### 4.7. Settings & Calibration (`SettingsPage.tsx`)
- **Review:** Profile fields, default hourly rate (USD), display currency selector, and Empirical-Bayes Calibration card.
- **Findings:**
  - Dedicated Empirical-Bayes card displays active pipeline parameters:
    - Shrinkage weight formula: $w_k = k / (k + 2.83)$
    - Prior variance ratio: $\sigma^2 / \tau^2 = 2.83$
    - Empirical gain: $+19.52\%$ MdAPE verified at $k=10$
    - Bounded scaling multiplier: $[0.33, 3.0]$
  - Explicit consent collection notice for retrained delivery actuals.
  - Administrative export links for consented actuals (CSV and JSON).

### 4.8. Shared Estimate View (`SharedEstimatePage.tsx`)
- **Review:** Unauthenticated / public read-only estimate page, password protection form, and summary view.
- **Findings:**
  - *Defect:* Contained legacy branding link: `<Link to="/">&larr; Predictify</Link>`.
  - *Remediation:* Updated link to `&larr; PredictIQ`. Added statistical reality box explaining that effort depends strictly on functional size (`size_fp`), team size and duration are staffing and schedule planning indicators (Brooks' Law), and typical error is roughly ±50%.

---

## 5. Review Findings & Remediation Register

| ID | Component / File | Severity | Defect Description | Remediation Applied |
| :--- | :--- | :---: | :--- | :--- |
| **FE-01** | `ModelTransparencyModal.tsx` | **High** | Claimed `MultivariateMonotoneModel` ($E = a \cdot S^b \cdot D^c$) was the "Primary Engine" and `MonotonePowerLaw` was fallback. | Corrected to present `MonotonePowerLaw` ($E = a \cdot S^b$) as the Production Engine driving effort strictly from functional size. Documented R03 duration ablation where positive duration elasticity ($c=+0.5972$) violated Brooks' Law. |
| **FE-02** | `ConfidenceInterval.tsx`, `EstimationResultView.tsx`, `ResultsPage.tsx` | **High** | Uncertainty spread summary omitted empirical coverage text for the dual conformal bands. | Added explicit measured coverage text: `50% Likely Band (Inner) [51.2% measured coverage]` and `80% Plausible Range (Outer) [79.0% holdout pooled coverage]`. |
| **FE-03** | `EstimationResultView.tsx`, `ResultsPage.tsx`, `FunctionalSizeCard.tsx` | **Medium** | Lacked plain-language uncertainty disclaimers for non-statistician decision-makers. | Added standard plain-language uncertainty guidance: "Typical estimation error is roughly ±50% on novel projects prior to empirical Bayes shrinkage. Use 50% Likely Band for sprint planning and 80% Plausible Range for budget caps." |
| **FE-04** | `FunctionalSizeCard.tsx`, `EstimationResultView.tsx` | **Medium** | Sizing assumption provenance was unbadged during document upload / NLP extraction. | Added explicit visual assumption badges: `Assumption: ~8 FP/Story`, `Assumption: ~5 FP/API`, and `NLP Size Uncertainty: ±15%`. |
| **FE-05** | `PlanningCapacityCard.tsx`, `NewEstimatePage.tsx`, `ResultsPage.tsx` | **Medium** | Team size and duration needed clearer labeling as capacity indicators, not effort predictors. | Labeled inputs as "Planned Team Size (Staffing Capacity)" and "Planned Target Duration (Schedule Horizon)", explaining Brooks' Law and functional size independence. |
| **FE-06** | `LandingPage.tsx`, `SharedEstimatePage.tsx` | **Low** | Contained legacy "Predictify" branding in footer and back link. | Replaced all instances of "Predictify" with "PredictIQ". |

---

## 6. Verification & Test Evidence

### 6.1. TypeScript Strict Typecheck
```text
npm --prefix frontend run typecheck
> tsc --noEmit && tsc -p tsconfig.test.json --noEmit
Exit code: 0 (0 errors)
```

### 6.2. Vitest Component & Unit Tests
```text
cd frontend; npx vitest run --pool=forks --maxWorkers=2
Test Files: 24 passed (24)
Tests:      132 passed (132)
Errors:     0 errors
Exit code:  0
```

### 6.3. Production Build Compilation
```text
npm --prefix frontend run build
> tsc && node scripts/check-build-env.mjs && vite build
dist/index.html                     1.88 kB
dist/assets/index-CsRGHmyH.css     76.19 kB
dist/assets/ResultsPage-D3MI7bY_.js 20.72 kB
dist/assets/NewEstimatePage-*.js   43.63 kB
built in 49.33s (0 errors)
Exit code: 0
```

---

## 7. Conclusion & Quality Sign-Off

The PredictIQ frontend application has undergone rigorous inspection and remediation. All user interfaces truthfully represent the mathematical properties of the production monotone power-law model, respect Brooks' Law regarding duration and team size, present dual calibrated prediction intervals with measured empirical coverage, expose plain-language uncertainty disclaimers, provide assumption badges for NLP sizing, and present organizational calibration status.

**Frontend Quality Status:** **VERIFIED & APPROVED (PASS)**.
