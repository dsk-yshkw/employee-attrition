# AAAI Reproducibility Checklist — filled answers (draft)

Answers keyed to the AAAI-26/27 checklist wording. Each item: **answer** +
justification. Items marked ⚠ can be upgraded cheaply before submission (see
"Cheap upgrades" at the end). Transcribe into `ReproducibilityChecklist.tex`
from the author kit.

## General

1. Conceptual outline / pseudocode of AI methods introduced — **yes**
   (Algorithm 1: the microsimulation; sub-models specified as equations).
2. Opinions/hypotheses delineated from facts — **yes**
   (descriptive-vs-causal boundary stated repeatedly; Limitations paragraph).
3. Pedagogical references for less-familiar readers — **yes**
   (SHAP, tabular-ML evidence, relative-pay economics all cited).

## Theoretical contributions — **no**
(No theorems; the paper is empirical/methodological. Skip the block.)

## Datasets — **yes**

1. Motivation for selected datasets — **yes** (JPSED is the national panel
   linking individual income, employment states and quit events; CPI/MHLW are
   the official price and market-wage series).
2. Novel datasets included in a data appendix — **yes**, conditional ⚠:
   upload the anonymized code+data snapshot (synthetic panel + derived macro
   CSVs) as supplementary material at submission. Without the upload: partial.
3. Novel datasets publicly available upon publication with research license —
   **yes** ⚠ (synthetic data and macro CSVs are in the public repo; ADD A
   LICENSE FILE — see upgrades).
4. Existing datasets cited — **yes** (JPSED cited in text; SSJDA DOIs in the
   camera-ready acknowledgments; CPI and MHLW sources cited).
5. Existing datasets publicly available — **partial**
   (macro series: public; JPSED microdata: not public, available to qualified
   researchers via SSJDA application — stated in the paper).
6. Non-public datasets described in detail + why public alternatives are
   unsuitable — **yes** (Methods describes waves, screening, labels, features;
   no public dataset links Japanese individual income, employment states and
   quit events in a multi-year panel at this scale).

## Computational experiments — **yes**

1. Number/range of hyperparameter values tried + selection criterion —
   **partial** (no systematic search was performed; all models use fixed,
   disclosed settings — state this explicitly, e.g. "we performed no
   hyperparameter search; all settings are library defaults or the fixed values
   in Appendix X").
2. Pre-processing code included — **yes** (public repo: variable map, loaders,
   feature builders).
3. All source code for experiments included in a code appendix — **yes**,
   conditional ⚠ (upload anonymized repo snapshot as supplementary; else
   partial).
4. Source code publicly available upon publication with research license —
   **yes** ⚠ (public GitHub repo; ADD LICENSE).
5. Source code commented with references to the paper — **partial**
   (modules have docstrings explaining each modeling choice, but no
   line-by-line mapping to paper sections).
6. Seed-setting described — **yes** (fixed seeds throughout: simulation
   seed stated; sequence models torch.manual_seed(0); sklearn/XGBoost
   random_state=42).
7. Computing infrastructure specified — **no → yes** ⚠ after adding one
   sentence (suggested text below).
8. Evaluation metrics formally described + motivated — **yes** (ROC-AUC and
   PR-AUC for rare-event ranking; calibration pred/obs for generative use;
   R²/MAE for wage models; elasticity defined in Methods).
9. Number of algorithm runs per reported result stated — **yes** ⚠ after
   adding: "each reported result is a single run with the fixed seed" (and the
   simulation-seed stability note in Robustness).
10. Analysis beyond single-dimensional summaries (variation/confidence) —
    **yes** (computed 2026-07 via `scripts/compute_uncertainty.py`: simulation
    dispersion over 10 seeds — annual separation sd ≤ 0.0016, end-year real
    income sd 0.36 man-yen — and paired 1,000-resample bootstrap 95% CIs for
    all six test AUCs; add the Robustness sentences to the paper).
11. Significance judged with appropriate statistical tests — **yes**
    (paired bootstrap: XGBoost's AUC gap excludes zero vs every alternative,
    e.g. +0.019 [0.014, 0.024] over HistGBM, +0.022 [0.015, 0.029] over the
    MLP; cluster-robust t-tests in Table 5).
12. All final hyperparameters listed — **partial → yes** ⚠ with a short
    appendix table (values below).

## Cheap upgrades before submission

A. DONE: MIT LICENSE added to the repo (data-attribution note included).
B. DONE (2026-07): anonymized snapshot built and verified (0 identifying
   strings; LICENSE copyright and notebook repo-URL/paths scrubbed; 53 files,
   ~0.6 MB zip). Location:
   `My Drive/ColabNotebooks/employee-attrition/supplementary_code_anonymized.zip`
   — upload this as supplementary material at submission.
C. DONE: infrastructure paragraph drafted (Apple M1, 16 GB, macOS 15.3,
   Python 3.9, sklearn 1.6.1 / XGBoost 2.1.4 / statsmodels 0.14.6 /
   PyTorch 2.8.0 / SHAP 0.49.1; <1 h end-to-end) — in the
   "Reproducibility Details" appendix block (see session notes / manuscript).
D. DONE: runs-and-seeds paragraph drafted (single run, fixed seeds; dispersion
   and bootstrap reported under Robustness) — same appendix block.
E. DONE: hyperparameters consolidated in the "Reproducibility Details"
   appendix block (values below verified against code):
   - XGBoost: n_estimators 400, learning_rate 0.05, max_depth 5,
     subsample 0.8, colsample_bytree 0.8.
   - HistGradientBoosting (benchmark & transition models): learning_rate 0.05,
     max_iter 300–400, L2 regularization 1.0; no class re-weighting in
     transition models.
   - Logistic: scikit-learn defaults, max_iter 2000 (balanced class weights in
     the benchmark only).
   - MLP/GRU: hidden 64; Transformer: d_model 64, 4 heads, 2 layers,
     dropout 0.1; all: Adam lr 1e-3, batch 512, 8 epochs, pos-weighted BCE.
   - Microsimulation: wage noise sd 30 man-yen; horizon 4; seed 1.
F. DONE (2026-07): `scripts/compute_uncertainty.py` computed the simulation
   seed-dispersion and the paired bootstrap AUC CIs (results in HANDOFF and in
   the suggested Robustness prose). Items C10 and C11 upgraded to yes.
