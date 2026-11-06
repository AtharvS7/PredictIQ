# PredictIQ projects_v2 Harmonization & Deduplication Report

**Generated:** 2026-11-06
**Initial Raw Rows Ingested:** 915
**Harmonized projects_v2 Rows:** 915

## 1. Source Breakdown & Conversion Rules

| Source | Raw Ingested | Harmonized Rows | Size Unit | Sizing Standard | Effort Unit | Conversion Cited |
|---|---:|---:|---|---|---|---|
| `china` | 499 | 499 | `FP` | IFPUG Function Points | Person-hours | None (Effort already in person-hours) |
| `kitchenham` | 145 | 145 | `FP` | IFPUG Function Points | Person-hours | None (Effort already in person-hours) |
| `desharnais` | 81 | 81 | `FP` | IFPUG Function Points | Person-hours | None (Effort already in person-hours) |
| `maxwell` | 62 | 62 | `FP` | IFPUG Function Points | Person-hours | None (Effort already in person-hours) |
| `albrecht` | 24 | 24 | `FP` | IFPUG Function Points | Person-hours | Albrecht & Gaffney (1983): Raw effort in 1000s of hours -> multiplied by 1000.0 |
| `att_aptness` | 104 | 104 | `FP` | IFPUG Function Points | Person-hours | None (Effort already in person-hours) |

## 2. Cross-Source Duplicate Analysis

No cross-source duplicates detected across disparate repositories.

## 3. Within-Source Identical (Size, Effort) Records

No within-source duplicate coordinates found.

## 4. Policy Compliance Verification

- **Zero Unrecorded Conversions:** Verified. Albrecht is the sole dataset requiring multiplier (*1000), fully cited.
- **No KLOC to FP Conversions:** Verified. KLOC datasets (NASA, Miyazaki) were excluded.
- **Zero Imputation:** Verified. Null durations and platforms remain explicitly null without synthetic imputation.
- **China Effort Parity:** Verified. Effort person-hours preserved, Resource code dropped.