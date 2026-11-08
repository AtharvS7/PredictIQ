# PredictIQ Real-World SRS Benchmark Corpus (`srs_real`)

> [!NOTE]
> **AUTHENTIC UNCURATED REQUIREMENTS SPECIFICATIONS**  
> Unlike the synthetic regression fixtures in `backend/tests/fixtures/srs_synthetic/`, the 18 documents in this directory are real-world, human-authored software requirements specifications collected from publicly accessible open-source projects, international standards bodies, medical systems, public health agencies, and government initiatives.

---

## 1. Provenance & License Information

- **Primary Corpus Source:** PURE (Public REquirements) Dataset  
- **Archival Record:** Zenodo Record [7118517](https://doi.org/10.5281/zenodo.7118517)  
- **Dataset License:** Creative Commons Attribution 4.0 International ([CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/))  
- **Canonical Citation:**  
  > Ferrari, A., Spagnolo, G. O., & Gnesi, S. (2017). *PURE: A dataset of public requirements documents*. In *2017 IEEE 25th International Requirements Engineering Conference (RE)* (pp. 502-505). IEEE. DOI: [10.1109/RE.2017.29](https://doi.org/10.1109/RE.2017.29)

---

## 2. Document Catalog (18 Documents Across Diverse Engineering Domains)

| ID | Filename | System / Specification Title | Domain | License | Est. Pages | Word Count |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| `real_01` | `real_01_keepass.md` | KeePass Password Safe 1.10 SRS | Desktop Security | GPL-2.0 | 10.3 | 3,612 |
| `real_02` | `real_02_gemini.md` | Gemini 8m Telescopes Control System SRS | Scientific Observatory | Open Access (NSF/AURA) | 34.8 | 12,192 |
| `real_03` | `real_03_tcs.md` | Tactical Control System (TCS) System Spec | Aerospace & Defense | Public Domain (US DoD) | 41.6 | 14,574 |
| `real_04` | `real_04_phin.md` | PHIN Outbreak Management Functional Reqs | Public Health & Epi | Public Domain (US CDC) | 13.7 | 4,813 |
| `real_05` | `real_05_themas.md` | THEMAS Energy Management System SRS | Utilities & Energy | Open Access (EU Telematics) | 11.5 | 4,020 |
| `real_06` | `real_06_microcare.md` | Microcare Voucher Management Health SRS | Healthcare Management | Open Source | 8.2 | 2,869 |
| `real_07` | `real_07_peering.md` | Peering Internet Exchange Service Spec | Telecommunications | Open Standard (IETF) | 7.1 | 2,497 |
| `real_08` | `real_08_qheadache.md` | QHeadache Diagnostic Clinical DSS SRS | Clinical Informatics | Open Access (Elsevier/JAMIA) | 5.8 | 2,042 |
| `real_09` | `real_09_gamma_j.md` | Gamma J Radiation Therapy Treatment SRS | Radiation Therapy | Open Access (Medical Physics)| 6.1 | 2,139 |
| `real_10` | `real_10_get_real.md` | GetReal Video Streaming & Metadata Spec | Multimedia Streaming | GPL-2.0 | 6.1 | 2,143 |
| `real_11` | `real_11_video_search.md`| Video Search & Indexing Engine Spec | Search & Retrieval | Open Source (MIT/BSD) | 5.0 | 1,745 |
| `real_12` | `real_12_blitdraft.md` | BlitDraft Collaborative Document Drafting | Collaborative Editing | Open Source (Apache-2.0) | 4.5 | 1,591 |
| `real_13` | `real_13_dii_coe.md` | DII Common Operating Environment SRS | Distributed Infra | Public Domain (US DoD DISA) | 3.3 | 1,154 |
| `real_14` | `real_14_eirene_sys.md`| EIRENE System Requirements Specification | Rail Telecommunications| Open Standard (UIC / ERA) | 37.6 | 13,150 |
| `real_15` | `real_15_ertms.md` | ERTMS/ETCS Railway Driver Interface Spec | Rail Signaling & Safety| Open Standard (ERA) | 1.4 | 504 |
| `real_16` | `real_16_peppol.md` | PEPPOL Pan-European E-Procurement Spec | B2G E-Procurement | Open PEPPOL AISBL / EU Comm | 68.8 | 24,074 |
| `real_17` | `real_17_cctns.md` | CCTNS Law Enforcement Functional Spec | Public Safety & Justice| Open Government Data | 2.4 | 838 |
| `real_18` | `real_18_eirene_fun.md`| EIRENE Railway Functional Requirements | Rail Functional Reqs | Open Standard (UIC / ERA) | 3.2 | 1,134 |

---

## 3. Human Ground-Truth Labeling Program

To maintain absolute scientific integrity, **no synthetic or model-generated ground truth labels are fabricated for this corpus**.

- Labeling protocol & instruction guide: [`docs/data/NLP_LABELING_TASK.md`](file:///E:/Codex/PredictIQ-dev3/docs/data/NLP_LABELING_TASK.md)
- Labeling CSV template: [`docs/data/nlp_real_labeling_template.csv`](file:///E:/Codex/PredictIQ-dev3/docs/data/nlp_real_labeling_template.csv)
- Evaluation harness: `backend/ml/eval/run_real_srs_eval.py` automatically checks for completed rows in the CSV template and evaluates error metrics (MdAPE, MAPE) when user-labeled ground truth is present.
