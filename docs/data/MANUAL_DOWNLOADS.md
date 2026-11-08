Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# Manual Dataset Downloads & Login-Gated Sources

**Purpose:** Comprehensive instructions for downloading and staging external software estimation datasets that cannot be automatically acquired via anonymous, open HTTP requests due to interactive authentication, academic NDAs, institutional campus repositories, or commercial licensing.

---

## 1. Academic NDA & Collaboration Gated Sources

### A. Tukutuku Database (Mendes et al. Web Development Benchmark)
- **Status:** Gated by Academic Multi-Company Non-Disclosure Agreement (NDA)
- **Maintainer:** Prof. Emilia Mendes (Blekinge Institute of Technology / University of Auckland)
- **Project URL:** [Tukutuku Project](https://www.cs.auckland.ac.nz/~emilia/tukutuku/)
- **Expected Data Files:** `tukutuku_web_projects.csv` or `.arff`
- **Expected Size:** ~195 web development projects (~150 KB)
- **Target Destination:** `backend/ml/data/research/tukutuku/` (gitignored)
- **Manual Request & Staging Instructions:**
  1. Draft a formal academic data request email to Prof. Emilia Mendes detailing the empirical research context (software effort estimation benchmarking).
  2. Complete and return the required academic Non-Disclosure Agreement affirming that individual company metrics will remain anonymized.
  3. Upon receiving the replication archive from the author, extract the files into `backend/ml/data/research/tukutuku/`.
  4. Note on Usage: Sizing metrics in Tukutuku are Web Objects, Page Counts (static/dynamic), and Media counts. Under PredictIQ zero-fabrication policies, these metrics reside in the dedicated Web Objects track and must never be converted to IFPUG Function Points.

---

## 2. Institutional Repository & Campus-Gated Sources

### B. COSMIC FSM Literature Benchmark (Yürüm, Ünlü, Demirörs 2025/2026)
- **Status:** Institutional DSpace Repository / Author Replication Request
- **DOI:** `10.1016/j.jss.2025.112591`
- **Institutional Handle:** `http://hdl.handle.net/20.500.14034/3391`
- **Host Institution:** İzmir Bakırçay University Açık Erişim Sistemi (`acikerisim.bakircay.edu.tr`)
- **File Name:** `cosmic_literature_benchmark_337.csv`
- **Expected Size:** ~250 KB (337 projects compiled across 18 literature studies)
- **Target Destination:** `backend/ml/data/research/cosmic/` (gitignored)
- **Manual Download Steps:**
  1. Access the institutional handle URL (`http://hdl.handle.net/20.500.14034/3391`) using a web browser with institutional credentials or campus proxy if direct access is restricted.
  2. If the institutional repository endpoint times out or is unreachable off-campus, access the publication on [Elsevier ScienceDirect (DOI: 10.1016/j.jss.2025.112591)](https://doi.org/10.1016/j.jss.2025.112591) and check the "Supplementary Data / Replication Package" tab.
  3. Alternatively, request the replication dataset directly from the corresponding authors (Dr. Ozan Raşit Yürüm or Prof. Onur Demirörs) via ResearchGate.
  4. Place the downloaded CSV into `backend/ml/data/research/cosmic/cosmic_literature_benchmark_337.csv`.
  5. Note on Usage: Functional size is measured in COSMIC Function Points (CFP, ISO/IEC 19761). These 2nd-generation units are structurally distinct from IFPUG Function Points and are reserved strictly for the dedicated COSMIC model track.

---

## 3. Account-Gated Academic Portals

### C. SDEE (Software Development Effort Estimation)
- **Status:** Requires Free IEEE Account Login & Terms Acceptance
- **Portal URL:** [IEEE DataPort SDEE](https://ieee-dataport.org/documents/sdee-software-development-effort-estimation-dataset)
- **DOI:** `10.21227/d6qp-2n13`
- **File Name:** `sdee_dataset.zip`
- **Expected Size:** ~125 MB
- **Target Destination:** `backend/ml/data/research/sdee/` (gitignored)
- **Manual Download Steps:**
  1. Open the IEEE DataPort URL in your web browser.
  2. Sign in with your IEEE credentials or register for a free account.
  3. Accept the IEEE DataPort Terms of Use.
  4. Click the download button for `sdee_dataset.zip`.
  5. Extract the archive into `backend/ml/data/research/sdee/`.
  6. Note on Usage: SDEE consists of developer commit and pull request activity proxies, not whole-project audited effort. It is strictly excluded from macro project-level estimation.

---

## 4. Commercially Licensed Industry Repositories

### D. ISBSG D&E (Development & Enhancement Repository)
- **Status:** Requires Commercial License Purchase / Academic Research Partnership
- **Portal URL:** [ISBSG Official Portal](https://www.isbsg.org/development-and-enhancement-data/)
- **File Name:** `ISBSG_D&E_Release_Current.xlsx`
- **Expected Size:** ~45 MB (~13,147 projects)
- **Target Destination:** `backend/ml/data/private/isbsg_export.xlsx` (gitignored)
- **Manual Download & Ingestion Steps:**
  1. Procure a corporate license or apply for an academic research license at isbsg.org.
  2. Download the official release spreadsheet (.xlsx).
  3. Place the file at `backend/ml/data/private/isbsg_export.xlsx`.
  4. Execute the verified ingestion pipeline documented in `docs/data/ISBSG_PLAN.md`:
     ```bash
     python backend/ml/ingest_isbsg.py --file backend/ml/data/private/isbsg_export.xlsx --quality A,B
     ```
  5. The pipeline extracts IFPUG and COSMIC functional size, filters for Data Quality rating A or B, validates Summary Work Effort person-hours, and outputs partitioned clean tables.
