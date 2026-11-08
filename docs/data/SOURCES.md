Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# PredictIQ Data Sources Registry & Provenance (v2.0)

**Last Updated:** 2026-11-06  
**Status:** Approved for Data Foundation (M1)

This document formalizes the criteria and status for every empirical software estimation dataset evaluated for PredictIQ v2.

---

## 1. Primary Model Datasets (`decision: IN`)

The main estimation model trains strictly on verified, project-level records using IFPUG-compatible Function Points and measured person-hours.

| Source | Raw Rows | Sizing Metric | Target Effort | Years | Domain | SHA-256 Checksum | Licence / Provenance |
|---|---:|---|---|---|---|---|---|
| **China** | 499 | AFP (Function Points) | `Effort` (person-hours) | 2000–2008 | Information systems | `ae9df9c52c5bc5ba03b9732ecc159093f0c500ffa0f3d8260ddd7350f0a22c58` | PROMISE / Public Domain |
| **Kitchenham** | 145 | Adjusted FP | `Actual.effort` (hours) | 1994–1998 | Commercial banking | `0832342b248418cca324cebe77d86d2f90ae223c1119af9360783bdbad0b2ac0` | Academic Research Citation |
| **Desharnais** | 81 | PointsAjust (FP) | `Effort` (hours) | 1988–1989 | Business applications | `38c5d00053555cbe7f3c10c2b026990ea981612ddefd5a7e0fcf8aa52bc4fd64` | PROMISE / Open Data |
| **Maxwell** | 62 | Size (FP) | `Effort` (hours) | 1990–1996 | Aerospace & Defense | `1adb2b23c638a553a2b2e2d83476d983d1be13d4e891c4148f2a90834472c235` | PROMISE / European Space |
| **Albrecht** | 24 | Function Points | `Effort` (hours) | 1979–1983 | IBM Corporate Systems | `cfd9713c6a0a45e318fd5345d3f45ac1cfbbf59191d91a645eabd6541890fd18` | Classic IBM Benchmark |
| **AT&T Aptness** | 104 | Adjusted FP | `Effort` (hours) | 1986–1991 | Telecommunications | `92f4495226b89a26d5b1422e679445a4078bcca9905f08354988f796e3fcf210` | JSE Archive (Matson et al.) |
| **Total Qualified** | **915** | Function Points | Real Person-Hours | | Multi-domain | Verified | Clean Licensing |

---

## 2. Excluded Candidates (`decision: OUT`)

Every candidate excluded from the core model is listed below with the empirical reason for exclusion:

1. **Finnish (38 projects):** Sizing methodology mixes national variation with standard IFPUG. Excluded to maintain measurement purity.
2. **Kemerer (15 projects):** Too small sample size; effort in person-months without audited hours per month.
3. **NASA93 & COCOMO-81 (93 & 63 projects):** Sized in KLOC (lines of code), not Function Points. Converting KLOC to FP via arbitrary conversion ratios (gearing factors) is forbidden.
4. **Miyazaki94 (48 projects):** KSLOC-based measurements in Fujitsu environments; excluded for absence of FP sizing.
5. **Tukutuku (195 projects):** Web-hypermedia sizing (page counts, graphics, media assets) rather than transactional functional components.
6. **SEERA (academic projects):** Student projects built under artificial academic constraints; unrepresentative of commercial software lifecycles.
7. **COSMIC Benchmark (Yürüm, Ünlü, Demirörs 2026, 337 projects):** High-quality modern dataset, but uses COSMIC Functional Size Units (CFP). Kept separate for a future COSMIC model track.
8. **ISBSG Development & Enhancement (13,147 projects):** Commercial license required; not purchased. Documented in `ISBSG_PLAN.md`.

---

## 3. Research-Only Granular Tracks (Non-Project-Level)

The following datasets track individual tasks, issues, or commits. Under program rules, they are **strictly prohibited** from mixing into whole-project total effort training:
- **JOSSE (Zenodo 7022735):** Open source software issue tracking data.
- **SiP (Derek Jones collection):** 10,100 task-level developer estimates and actuals.
- **TAWOS (SOLAR group):** 458,232 Jira issues with story points.
- **CESAW (Jones & Nichols):** 203,621 individual task time facts.
- **SDEE (IEEE DataPort):** Developer commit and PR activity proxies.

