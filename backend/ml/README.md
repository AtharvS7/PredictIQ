# PredictIQ ML runtime and artifact contract

**2026-09-09: packaged model revoked.** Source comparison confirmed 481 corrupted
effort labels. Startup refuses the exact invalid artifact; estimates are
unavailable until a validated replacement is installed. The rebuilt 787-project
research candidate is not production approved. See
[reconstruction and results](../../docs/ml_rebuild_2026-09-09.md).
The contract below describes the legacy runtime, not validated model quality.

The packaged estimator is a `RandomForestRegressor`, serialized with scikit-learn **1.8.0**. The model report identifies it as `RandomForest`; older XGBoost descriptions did not describe the actual artifact. Keep deployment dependencies compatible with the serialized estimator. Version mismatch warnings now prevent loading.

The runtime reads `predictiq_best_model.pkl`, `predictiq_scaler.pkl`, and `predictiq_features.json`. Configured `ML_MODEL_PATH`, `ML_SCALER_PATH`, and `ML_FEATURES_PATH` override these paths; relative paths resolve from `backend/`. Pickles must come from the trusted build/artifact distribution, never user uploads.

Startup checks the exact 27-feature contract, estimator/scaler dimensions and available feature-name ordering, training metadata, and a preprocessing/inference smoke prediction. Missing or incompatible artifacts disable predictions. There is no automatic demo fallback. Runtime model/preprocessor errors and nonfinite results return an unavailable error, disable readiness, and cannot be persisted as plausible estimates. Missing/nonfinite request features are rejected. `/api/v1/ready` and `/api/v1/health` return 503 if the model, database, or Firebase initialization is unavailable; `/api/v1/live` is process liveness.

## Verified training/inference parity

The 740-row `predictiq_merged_dataset.csv` has these derived definitions, checked against every row by regression tests:

- `complexity_score = (T07 + T10 + T11) / 3`
- `team_skill_avg = (T12 + T13 + T14 + T15) / 4`
- `risk_score = (T08 + T09) / 2`
- `log_effort = log1p(effort_hours)`; runtime applies `expm1` after prediction.

Training fits `StandardScaler` on the training partition and uses the saved feature order. Runtime validates that order and applies the saved scaler. All 27 input features must be numeric and finite. Negative log-effort predictions are invalid rather than disguised as one-hour estimates.

### Adjustment units corrected

The dataset `Adjustment` column represents total influence, **not the value adjustment factor (VAF)**. For its 81 nonzero records, `size_fp = PointsNonAdjust * (0.65 + 0.01 * Adjustment)` matches within source rounding (80 records within one FP, one within 1.62 FP). The other 659 records contain zero. They cannot establish observed influence for those projects and remain an applicability limitation.

The service previously passed VAF (approximately 0.9) in `Adjustment`. It now converts the existing complexity-based VAF to influence with `(VAF - 0.65) / 0.01`. The existing raw-FP and complexity heuristics are retained; only the feature unit is corrected. No model was retrained.

## Interpretation and remaining limitations

`confidence_pct` is a legacy heuristic score based on aggregate R², populated features, and a size bucket. It is **not a calibrated probability of correctness**. The packaged R² and synthesized nonzero features often saturate the score at 95; the score must not be presented as 95% prediction accuracy. Runtime metadata exposes `confidence_method = heuristic_not_calibrated_probability`.

Effort minimum and maximum use fixed 0.8/1.4 multipliers plus clamps. These are scenario bounds, not statistical confidence intervals or validated coverage. Runtime metadata identifies the interval method. Reported benchmark metrics evaluate the training dataset; they do not validate performance on NLP-derived production inputs.

Dataset effort spans 1–9586.75 hours; runtime retains the documented 1–9587 likely-effort clamp. Dataset size spans 7.03125–17518 FP; the confidence heuristic's 50–3643 bucket is not the complete observed training range. It is retained as a legacy scoring rule, not evidence that inputs outside it are valid or invalid.

Transactions/entities, experience proxies, T-factors, complexity-based VAF, and NLP function-point estimates remain inferred product features. Their real-world accuracy and cross-source missing-value semantics need representative labeled projects and calibration work. The repository contains the merged CSV and training script but no verified complete source-to-merged-data reconstruction. Do not claim production predictive accuracy from schema parity alone.

Run focused verification from `backend/` with `python -m pytest tests/test_inference.py tests/test_ml_service.py tests/test_health.py`. The packaged-artifact test exercises actual inference under installed dependencies; deterministic fakes separately cover failure modes. `python -m ml.train` explicitly retrains and replaces model artifacts and should be treated as a separate validated model release.
