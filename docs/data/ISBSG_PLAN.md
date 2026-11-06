# ISBSG Data Expansion Plan (Future Sponsored Track)

**Status:** Documented Future Option (Not Purchased in Current Release)  
**Target Repository:** International Software Benchmarking Standards Group (ISBSG) — Development & Enhancement Repository (2025/2026 Release)

---

## 1. Context & Commercial Status

The ISBSG Development & Enhancement dataset contains over 13,000 completed software projects contributed by multinational corporations, defense agencies, and software houses across 30+ countries. 

For the current open-source / independent development phase of PredictIQ, commercial licensing fees for the raw database are out of scope. No purchase was made. This document pre-registers the architectural ingestion specification so that when organizational sponsorship or an academic partnership is secured, the pipeline can immediately assimilate the dataset without redesigning the ML architecture.

---

## 2. Required Fields to Request from ISBSG

When acquiring the ISBSG D&E data extract, the following standard fields should be licensed and requested:

| ISBSG Field Name | Target PredictIQ Field | Description & Filter Criteria |
|---|---|---|
| `Project ID` | `project_id` | Unique tracking identifier |
| `Data Quality Rating` | `quality_rating` | **Filter:** Must be rating `A` (sound data) or `B` (good data). Ratings C and D rejected. |
| `Unadjusted Function Points` (or `Adjusted FP`) | `size_value` | Standard IFPUG functional sizing measurement |
| `Functional Size Method` | `size_unit` | **Filter:** `IFPUG 4.x` (or `COSMIC` for separate COSMIC model track) |
| `Summary Work Effort` | `effort_hours` | Total actual person-hours across the project lifecycle |
| `Summary Work Effort Scope` | `effort_scope` | **Filter:** Must cover full development lifecycle (specification, design, code, test) |
| `Project Elapsed Time` | `duration_months` | Project calendar duration in months |
| `Max Team Size` | `team_size` | Peak full-time equivalent software staff |
| `Development Type` | `dev_type` | `New Development`, `Enhancement`, or `Re-development` |
| `Primary Programming Language` | `language` | Categorical classification (Java, Python, C#, TypeScript, COBOL, etc.) |
| `Architecture` | `platform` | Standalone, Client-Server, Multi-tier, Cloud / Web |
| `Year of Project` | `year` | Year project was completed |

---

## 3. Ingestion Pipeline Architecture

The ingestion pipeline will be implemented in `backend/ml/ingest_isbsg.py`:

```
┌─────────────────────────────────┐
│ ISBSG Raw Excel / CSV Extract   │
└────────────────┬────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ Quality & Integrity Filter                             │
│ • Data Quality Rating in ['A', 'B']                    │
│ • Sizing Method == 'IFPUG 4.x' (or 'COSMIC')           │
│ • Summary Work Effort > 0 AND Size > 0                 │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ Cross-Source Deduplication Guard                       │
│ • Screen against existing China/Kitchenham/Desharnais  │
│   projects that were historically submitted to ISBSG   │
│   via size+effort+year fingerprinting                  │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ Harmonized Output                                      │
│ • Append into unified `projects_v2` schema             │
│ • Update provenance manifest with ISBSG license digest │
└────────────────────────────────────────────────────────┘
```

---

## 4. Next Steps for Sponsors

1. Secure corporate or institutional data license through [ISBSG Official Portal](https://www.isbsg.org/).
2. Place licensed export under secure offline path `backend/ml/data/private/isbsg_export.xlsx` (gitignored).
3. Execute `python backend/ml/ingest_isbsg.py --path backend/ml/data/private/isbsg_export.xlsx`.
4. Re-run pre-registered evaluation protocol (`backend/ml/eval/run_eval.py`) to verify transferability and check against baseline.
