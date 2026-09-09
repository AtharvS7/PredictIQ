# ML data reconstruction and research candidate — 2026-09-09

## Critical correction

The 740-row `backend/ml/predictiq_merged_dataset.csv` is **not valid training data**.
Named-column comparison against China source records identifies **481 rows** where
`effort_hours` equals the source `Resource` code rather than `Effort` person-hours.
For example, China project 1 has AFP 1587 and effort 7490 hours; the merged CSV
stores 4 hours. Matching also uses Transactions (Input + Output + Enquiry) and
Entities (File + Interface), not just row position. Another 108 targets equal
9586.75, consistent with the earlier clipping pipeline. Source labels are retained
without clipping in the reconstruction.

The old R² 0.8953 is invalid evidence of real-world accuracy. Earlier completed
runtime and integration checks proved software execution, not label correctness.
The previous overall repair estimate must not be interpreted as ML readiness.

The exact shipped model SHA-256 is revoked in `ml/artifact_safety.py`. Loading it
fails closed, so estimates/readiness are unavailable until a validated compatible
replacement is supplied. Original model/data remain intact for investigation.
The legacy trainer rejects the known corrupted CSV before writing new model files.
Contract integration tests use an explicitly synthetic serialized sklearn fixture;
they do not claim to validate model accuracy. No production replacement is approved.

## Rebuilt experiment

`ml/rebuild_dataset.py` reads named fields, validates positive finite size/effort,
retains source/project identity, groups identical size/effort observations across
splits, and records source URLs plus SHA-256 checksums.

| Source | Project rows | Size field | Observed target |
|---|---:|---|---|
| China | 499 | AFP | Effort |
| Desharnais | 81 | PointsAjust | Effort |
| Maxwell | 62 | Size | Effort |
| Kitchenham | 145 | Adjusted.function.points | Actual.effort |
| Total | **787** | Function points | Person-hours |

Files came from the [author-maintained public dataset collection](https://github.com/Derek-Jones/Software-estimation-datasets).
The experiment is local research only: licenses and differences in FP counting
methods still require source-level clearance. Recorded completed-project FP is
also not equivalent to prospective NLP-estimated FP. Neither source identity,
actual duration, productivity, nor target-derived features enter the model.
NASA KLOC/person-months, Finnish size-method ambiguity, and unlabeled Huijgens rows
are excluded instead of inventing conversions or labels.

Run from the repository root with the pinned backend environment:

```powershell
backend/.venv/Scripts/python.exe backend/ml/rebuild_dataset.py
backend/.venv/Scripts/python.exe backend/ml/train_research.py
```

Raw research inputs live in `backend/ml/data/research/`. Their filenames and source
URLs are in `SOURCES`/`SOURCE_URL` in the reconstruction script. Outputs are isolated
in `backend/ml/experiments/reconstructed-v1/`: projects, source audit/checksums,
split membership, test predictions, serialized pipeline and evaluation JSON.
Raw downloads and experiments are excluded from git and Docker contexts. Download
these public source files to reproduce locally; verify the recorded hashes before
comparing runs. No serving artifact is overwritten by the experiment scripts.

Five fixed candidates: median baseline, ridge power law, robust Huber power law,
random forest, histogram gradient boosting. All preprocessing is inside the fitted
pipeline. Seed 20260909; 471 train, 158 interval calibration, 158 untouched test.
Candidate choice minimizes equally weighted leave-one-source-out RMSLE using only
the training partition. Calibration/test never choose the winning model. Test
results are now observed: further tuning requires fresh external validation.

Winner: **Huber power law**, a deliberately small one-feature baseline.

| Test measure | Candidate | Median baseline |
|---|---:|---:|
| MAE, hours | 1740.08 | 2075.70 |
| Median absolute percentage error | 51.29% | 61.46% |
| Predictions within 25% | 24.05% | 18.35% |
| RMSLE | 0.8726 | 1.0788 |
| R² on hours | 0.2998 | -0.0712 |

MAE is 16.17% lower than the baseline, **not** proven better than a trustworthy
production model. Nominal 90% split-conformal intervals cover 89.24% of test rows
but median interval width is 9011 hours: uncertainty is too large for confident
commercial quoting. Measured local p95 single-row latency ~10.3 ms (environment
dependent). No accuracy percentage or production promotion is justified.

## Larger sources researched

| Source | Actual scale/grain | Fit and constraints |
|---|---|---|
| [ISBSG Development & Enhancement](https://www.isbsg.org/development-and-enhancement-data/) | Published 2025 release: 13,147 projects | Best direct expansion candidate; paid license and model-use rights must be checked. 2026 release announcement exists; do not assume its count. |
| [TAWOS](https://github.com/SOLAR-group/TAWOS) | Current v1.1: 458,232 issues, 39 projects | Separate task/story estimation; story points are not person-hours. Terms restrict research use despite Apache licensing text. |
| [SiP](https://arxiv.org/abs/1901.01621) | 10,100 unique task estimates, 22 developers | Real industrial tasks; different entity grain from project totals. |
| [CESAW](https://arxiv.org/abs/2106.03679) | 61,817 tasks, 45 projects | 203,621 time facts are not 203,621 projects; aggregation and rights need verification. |
| [SDEE](https://arxiv.org/abs/2109.05843) | ~13,000 GitHub repositories | Derived developer-activity effort proxies, not audited hour labels. |

More records alone cannot repair feature definitions or provide missing actual
hours. Next useful experiment requires compatible richer prospective features,
measurement harmonization and modern independently held-out project outcomes.
ISBSG purchase, credential rotation and any external deployment remain outstanding;
no purchase, contact, push or deployment was performed.
