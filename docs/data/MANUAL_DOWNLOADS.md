# Manual Dataset Downloads & Login-Gated Sources

**Purpose:** Documenting external sources that cannot be automatically downloaded via standard anonymous HTTP requests due to required authentication, payment, or interactive terms acceptance.

---

## 1. Login-Gated Research Datasets

### A. SDEE (Software Development Effort Estimation)
- **Status:** Requires IEEE Account Login
- **URL:** [IEEE DataPort SDEE](https://ieee-dataport.org/documents/sdee-software-development-effort-estimation-dataset)
- **DOI:** `10.21227/d6qp-2n13`
- **File Name:** `sdee_dataset.zip`
- **Expected Size:** ~125 MB
- **Target Destination:** `backend/ml/data/research/sdee/` (gitignored)
- **Manual Download Steps:**
  1. Open the IEEE DataPort URL in a modern browser.
  2. Log in with IEEE credentials or create a free IEEE account.
  3. Accept data usage terms.
  4. Download `sdee_dataset.zip`.
  5. Extract into `backend/ml/data/research/sdee/`.
  6. *Note:* Used strictly for developer activity research; excluded from core project training.

---

## 2. Commercially Licensed Datasets

### B. ISBSG D&E (Development & Enhancement Repository)
- **Status:** Requires Commercial License / Corporate Sponsorship
- **URL:** [ISBSG Official Portal](https://www.isbsg.org/development-and-enhancement-data/)
- **File Name:** `ISBSG_D&E_Release_Current.xlsx`
- **Expected Size:** ~45 MB
- **Target Destination:** `backend/ml/data/private/isbsg_export.xlsx` (gitignored)
- **Manual Download Steps:**
  1. Procure corporate or academic license at isbsg.org.
  2. Download official release spreadsheet.
  3. Place in `backend/ml/data/private/isbsg_export.xlsx`.
  4. Run `python backend/ml/ingest_isbsg.py` (see `docs/data/ISBSG_PLAN.md`).

---

## 3. Academic Archive Mirrors

### C. COSMIC FSM Literature Benchmark (Yürüm, Ünlü, Demirörs 2026)
- **Status:** Academic Institutional Repository / Author Request
- **DOI:** `10.1016/j.jss.2025.112591`
- **Repository Handle:** `http://hdl.handle.net/20.500.14034/3391`
- **File Name:** `cosmic_literature_benchmark_337.csv`
- **Expected Size:** ~250 KB
- **Target Destination:** `backend/ml/data/research/cosmic/` (gitignored)
- **Manual Download Steps:**
  1. Access the institutional handle or request replication package from authors on ResearchGate.
  2. Place CSV into `backend/ml/data/research/cosmic/`.
  3. *Note:* Reserved for dedicated COSMIC model track.

