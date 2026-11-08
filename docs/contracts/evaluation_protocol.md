Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# PredictIQ Evaluation Protocol & Decision Rule (v2.0-FROZEN)

**Status:** FROZEN  
**Hash Anchor:** Recorded in `docs/evidence/CP01.md` prior to model exploration.  
**Rule:** This evaluation protocol and the CP10 decision rule are permanently frozen. They must not be modified, tuned, or re-run after viewing validation results.

---

## 1. Validation Strategy

1. **Primary Protocol — Leave-One-Source-Out (LOSO) Cross-Validation:**
   - In each fold, all projects from one historical data source (e.g., China, Desharnais, Maxwell, Kitchenham, etc.) are completely held out as the test set.
   - All feature scalers, hyperparameter tuning (nested CV), and preprocessors are fit exclusively on the remaining training sources.
   - Evaluates true out-of-domain transferability rather than in-sample memorization.
2. **Secondary Protocol — Repeated Grouped K-Fold:**
   - 5-fold cross-validation repeated with 5 random seeds, grouped by source or project cluster to prevent duplicate observation leakage.

---

## 2. Frozen Evaluation Metrics

For every model candidate and fold, the following metrics are computed:
1. **`MdAPE` (Primary Metric)**: Median Absolute Percentage Error:
   $$\text{MdAPE} = \text{median}\left(\frac{|\hat{y}_i - y_i|}{y_i}\right) \times 100\%$$
   Robust to heavy-tailed software project outliers.
2. **`MAE`**: Mean Absolute Error in person-hours.
3. **`RMSLE`**: Root Mean Squared Logarithmic Error.
4. **`PRED25`**: Percentage of estimates within 25% of actual effort:
   $$\text{PRED25} = \frac{1}{N} \sum_{i=1}^N \mathbf{1}\left[\frac{|\hat{y}_i - y_i|}{y_i} \le 0.25\right] \times 100\%$$
5. **`PRED50`**: Percentage of estimates within 50% of actual effort.
6. **Log-space bias**: Mean difference $\text{mean}(\log(\hat{y}_i) - \log(y_i))$.
7. **Standardized Accuracy (SA)**:
   $$\text{SA} = \left(1 - \frac{\text{MAE}_{\text{model}}}{\text{MAE}_{\text{random\_guessing}}}\right) \times 100\%$$
8. **`MMRE`**: Mean Magnitude of Relative Error (explicitly labelled *'misleading alone'* due to asymmetric penalty on underestimates).
9. **Breakdowns**:
   - Per-source breakdown table.
   - Size-bucket breakdown (Small: < 100 FP, Medium: 100–500 FP, Large: > 500 FP).
10. **Statistical Rigor**:
    - Bootstrap 95% Confidence Intervals (1,000 resamples) for MdAPE and MAE.
    - Paired two-sided Wilcoxon signed-rank test between candidate absolute percentage errors.

---

## 3. Always-Run Baselines

Every evaluation execution must report comparison against four fixed baselines:
1. **Global Median Effort**: Predicts constant median of training fold.
2. **Median Productivity Multiplier**: Predicts $(\text{median}(y / \text{size})) \times \text{size}$.
3. **Log-Log OLS Power Law**: $\log(y) = \beta_0 + \beta_1 \log(\text{size})$.
4. **Huber Robust Power Law**: HuberRegressor fit on log-log transform.

---

## 4. Frozen CP10 Decision Rule

When selecting between Track 1 (Simple / Transparent Power Law & Monotone Models) and Track 2 (Flexible HistGB / Ensemble Models):

> **Challenger Rule:**  
> The Track 2 challenger model (or an ensemble of Track 1 + Track 2) shall be selected for production deployment over the Track 1 simple baseline **IF AND ONLY IF ALL FOUR OF THE FOLLOWING CONDITIONS ARE MET**:
> 1. **LOSO MdAPE improves by at least 5% relative** over the best Track 1 model:
>    $$\frac{\text{MdAPE}_{\text{Track1}} - \text{MdAPE}_{\text{Track2}}}{\text{MdAPE}_{\text{Track1}}} \ge 0.05$$
> 2. **Paired Wilcoxon signed-rank test** on absolute errors yields $p < 0.05$.
> 3. **No individual data source suffers a degradation greater than 10% relative** in MdAPE:
>    $$\forall s \in \text{Sources}, \quad \frac{\text{MdAPE}_{\text{Track2}, s} - \text{MdAPE}_{\text{Track1}, s}}{\text{MdAPE}_{\text{Track1}, s}} \le 0.10$$
> 4. **Empirical conformal interval coverage is not worse** (coverage within nominal $\pm 5\%$).

If any of conditions (1)-(4) fails, **Track 1 simple baseline MUST be shipped**.  
The decision evaluation is executed **EXACTLY ONCE** on the finalized validation folds; re-tuning or repeating the decision rule after inspection is strictly forbidden.

