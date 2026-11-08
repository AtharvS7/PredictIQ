Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# NLP Real-Document Human Ground-Truth Labeling Task

> [!IMPORTANT]
> **NO FABRICATED LABELS POLICY**  
> Under PredictIQ checkpoint S05 quality guidelines, machine learning and engineering agents are strictly prohibited from inventing, fabricating, or auto-generating synthetic "ground truth" labels for real-world documents. True empirical assessment of NLP feature extraction requires independent human expert ground truth.

---

## 1. Overview & Goal

The purpose of this labeling program is to evaluate the extraction accuracy of the PredictIQ NLP Service (`backend/app/services/nlp_extractor.py`) against 15 authentic, publicly available Software Requirements Specification (SRS) documents located in:
`backend/tests/fixtures/srs_real/`

The human annotator inspects each document and records:
1. `user_stories_count`: Number of distinct functional user stories or discrete functional requirements.
2. `integrations_count`: Number of external system touchpoints (third-party APIs, external hardware interfaces, protocols, external services).
3. `functional_size_estimate_fp`: Human expert functional size estimate in IFPUG/COSMIC Function Points (FP).

The completed annotations are entered into:
`docs/data/nlp_real_labeling_template.csv`

---

## 2. Document Inventory (15 Target Specifications)

| ID | Document File | System / Domain | Focus Areas |
| :--- | :--- | :--- | :--- |
| `real_01` | [`real_01_keepass.md`](file:///E:/Codex/PredictIQ-dev3/backend/tests/fixtures/srs_real/real_01_keepass.md) | KeePass Password Safe (Desktop Security) | Database crypto, auto-type, search, export/import |
| `real_02` | [`real_02_gemini.md`](file:///E:/Codex/PredictIQ-dev3/backend/tests/fixtures/srs_real/real_02_gemini.md) | Gemini Telescopes (Observatory Control) | Instrument control, telescope mount, telemetry, sensors |
| `real_03` | [`real_03_tcs.md`](file:///E:/Codex/PredictIQ-dev3/backend/tests/fixtures/srs_real/real_03_tcs.md) | Tactical Control System (Defense/Aerospace) | Mission control, telemetry downlink, flight payload |
| `real_04` | [`real_04_phin.md`](file:///E:/Codex/PredictIQ-dev3/backend/tests/fixtures/srs_real/real_04_phin.md) | PHIN Outbreak Management (Public Health/CDC) | Case reporting, contact tracing, lab data interchange |
| `real_05` | [`real_05_themas.md`](file:///E:/Codex/PredictIQ-dev3/backend/tests/fixtures/srs_real/real_05_themas.md) | THEMAS Energy Management (Utilities/Smart Grid) | Power metering, grid monitoring, alarm routing |
| `real_06` | [`real_06_microcare.md`](file:///E:/Codex/PredictIQ-dev3/backend/tests/fixtures/srs_real/real_06_microcare.md) | Microcare Voucher System (Healthcare) | Patient registration, voucher redemption, billing |
| `real_07` | [`real_07_peering.md`](file:///E:/Codex/PredictIQ-dev3/backend/tests/fixtures/srs_real/real_07_peering.md) | Peering Internet Exchange (Telecommunications) | BGP peering, traffic telemetry, IXP provisioning |
| `real_08` | [`real_08_qheadache.md`](file:///E:/Codex/PredictIQ-dev3/backend/tests/fixtures/srs_real/real_08_qheadache.md) | QHeadache Diagnostic DSS (Clinical DSS) | Clinical questionnaire, decision tree, diagnostic rules |
| `real_09` | [`real_09_gamma_j.md`](file:///E:/Codex/PredictIQ-dev3/backend/tests/fixtures/srs_real/real_09_gamma_j.md) | Gamma J Radiation Therapy (Medical Oncology) | Radiation dose calculation, beam collimation, imaging |
| `real_10` | [`real_10_get_real.md`](file:///E:/Codex/PredictIQ-dev3/backend/tests/fixtures/srs_real/real_10_get_real.md) | GetReal Video Streaming (Multimedia) | RTP streaming, codec negotiation, metadata index |
| `real_11` | [`real_11_video_search.md`](file:///E:/Codex/PredictIQ-dev3/backend/tests/fixtures/srs_real/real_11_video_search.md) | Video Search Engine (Search/IR) | Video ingestion, indexing, transcript search |
| `real_12` | [`real_12_blitdraft.md`](file:///E:/Codex/PredictIQ-dev3/backend/tests/fixtures/srs_real/real_12_blitdraft.md) | BlitDraft Collaborative Drafting (Collab SaaS) | Operational transform, revision history, comments |
| `real_13` | [`real_13_dii_coe.md`](file:///E:/Codex/PredictIQ-dev3/backend/tests/fixtures/srs_real/real_13_dii_coe.md) | DII COE Infrastructure (Distributed Infra) | Common operating environment, API contracts, security |
| `real_14` | [`real_14_eirene_sys.md`](file:///E:/Codex/PredictIQ-dev3/backend/tests/fixtures/srs_real/real_14_eirene_sys.md) | EIRENE Railway Telecommunications (Rail/GSM-R) | Voice cab dispatch, trackside radio, emergency broadcast |
| `real_15` | [`real_15_ertms.md`](file:///E:/Codex/PredictIQ-dev3/backend/tests/fixtures/srs_real/real_15_ertms.md) | ERTMS Railway Driver Interface (Signaling/Safety) | Driver desk display, speed supervision, braking curve |

---

## 3. Detailed Counting Rules

### 3.1. User Stories / Functional Requirements (`user_stories_count`)
- **What to count:** Discrete, actionable end-user or system capabilities. For example:
  - "User can generate composite master password key" $\rightarrow$ 1
  - "System shall calculate radiation beam fluence matrix" $\rightarrow$ 1
  - "System shall ingest DICOM image slice" $\rightarrow$ 1
- **What NOT to count:**
  - High-level chapter headings ("3. Functional Requirements")
  - Non-functional requirements (performance latency $< 200\text{ms}$, backup policy, license agreement)
  - Architectural overview prose or general glossary terms.

### 3.2. External Integrations (`integrations_count`)
- **What to count:** Distinct external boundary systems or external software components interfacing with the application.
  - Payment rails, third-party auth (OAuth/SAML), external databases outside application boundary, physical hardware bus interfaces (CAN bus, serial, GSM-R radio transceiver), external public registries (e.g. CDC national reporting, PEPPOL directory).
- **What NOT to count:**
  - Internal language modules or internal subroutines.

### 3.3. Functional Size Estimate (`functional_size_estimate_fp`)
- Provide an estimated functional size in IFPUG Function Points (FP).
- **Recommended sizing approaches:**
  - Standard IFPUG 4.3.1 count (Internal Logical Files, External Interface Files, External Inputs, External Outputs, External Inquiries).
  - High-level agile heuristic: $(\text{user\_stories} \times \text{FP\_per\_story}) + (\text{integrations} \times \text{FP\_per\_integration})$. Typical sizing factors: simple user story = 4–6 FP, medium = 7–10 FP, complex = 11–15 FP; external interface = 4–7 FP.

---

## 4. How the Automated Harness Uses Human Ground Truth

1. The test runner `backend/ml/eval/run_real_srs_eval.py` automatically checks for values in `docs/data/nlp_real_labeling_template.csv`.
2. When fields are empty or blank, the runner logs `UNLABELED` and computes runtime profiling, crash-safety checks, and unsupervised feature distributions.
3. When any row contains valid numerical user labels, the runner automatically calculates:
   - Median Absolute Percentage Error (MdAPE) vs human functional size.
   - Mean Absolute Error (MAE) for user stories and integration counts.
   - PRED(25) and PRED(30) accuracy metrics.
4. Run the evaluation anytime via:
   ```powershell
   python backend/ml/eval/run_real_srs_eval.py
   ```
