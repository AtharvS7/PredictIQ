# PredictIQ Synthetic SRS Regression Fixtures

> [!IMPORTANT]
> **SYNTHETIC REGRESSION FIXTURES ONLY — NOT REAL-WORLD GROUND TRUTH**  
> The 36 documents in this directory and their corresponding annotations in `annotations.json` were authored synthetically by an automated agent during Checkpoint R09 to serve as deterministic regression fixtures.  
> **A functional size MdAPE of 0.00% on this synthetic test suite reflects template-aligned syntax by construction and DOES NOT represent real-world extraction accuracy.** Real-world requirements specifications feature narrative variance, missing headers, ambiguous scoping, and diverse architectural patterns that introduce substantial estimation error.

---

## 1. Purpose and Role in the Test Suite

These fixtures exist strictly to provide deterministic regression coverage for the NLP extractor pipeline (`backend.app.services.nlp_extractor`):
1. **Pipeline Invariant Testing:** Ensure changes to regexes, tokenization, or heuristic rules do not break basic extraction across 6 target software domains.
2. **Crash & Non-Finite Invariant Defense:** Guarantee that structured requirements documents can be parsed without unhandled exceptions or NaN/infinite numeric representations.
3. **Quantile Monotonicity Verification:** Validate that calibrated uncertainty quantiles satisfy strict non-crossing invariants ($0 < P_{10} \le P_{50} \le P_{90}$).

---

## 2. Corpus Taxonomy (36 Documents Across 6 Domains)

The corpus covers 6 software domains, each with 6 documents spanning complexity tiers from Minimal Viable Product (Low) to Complex Enterprise (Very High):

| Domain | Files | Description |
| :--- | :--- | :--- |
| **Web Applications** | `web_01` to `web_06` | E-commerce, SaaS Analytics, Patient Portal, LMS, CRM, Real Estate MVP |
| **Mobile Applications** | `mobile_01` to `mobile_06` | Fitness Tracker, Ridesharing, Digital Banking, Food Delivery, Event Wallet, Field Inspection |
| **Cloud / REST APIs** | `api_01` to `api_06` | Payment Gateway, Notification Broker, Identity SSO, Inventory API, Document Converter, API Gateway |
| **Data & Analytics Pipelines** | `data_01` to `data_06` | Lakehouse ETL, Fraud Detection, Recommendation ANN, Log Aggregator, Clickstream, Market Ticker MVP |
| **Enterprise / ERP Systems** | `erp_01` to `erp_06` | Supply Chain ERP, HRIS Payroll, Warehouse WMS, Billing Engine, Vendor Portal, Asset Maintenance MVP |
| **Embedded / IoT / Systems** | `iot_01` to `iot_06` | Smart Thermostat, Fleet Telematics, Drone Telemetry, Industrial Sensors, Smart Grid, Medical Gateway |

---

## 3. Ground Truth Annotations Schema (`annotations.json`)

Each entry in `annotations.json` maps a document key to:
- `filename`: Filename relative to this directory.
- `domain`: One of the 6 canonical domains.
- `complexity_tier`: Nominal complexity rating (`Low`, `Medium`, `High`, `Very High`).
- `ground_truth`:
  - `functional_size`: Nominal point functional size ($S_{\text{FP}}^* = \text{feature\_count} \times 8.0 + \text{integration\_count} \times 5.0$).
  - `tech_stack`: List of declared technologies.
  - `feature_count`: Number of explicitly enumerated user stories or features.
  - `integration_count`: Number of external third-party interface touchpoints.
  - `complexity_level`: Target ordinal complexity label.

---

## 4. Real-World Validation Contrast

For actual empirical validation against uncurated real-world software requirements specifications, see:
- Real-world corpus: `backend/tests/fixtures/srs_real/`
- User labeling task & guidelines: `docs/data/NLP_LABELING_TASK.md`
- Labeling template: `docs/data/nlp_real_labeling_template.csv`
