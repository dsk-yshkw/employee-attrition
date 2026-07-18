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
    **partial** (cluster-robust SEs for Table 5; simulation stability across
    seeds asserted but without dispersion numbers; no CIs on AUCs).
    Upgradable — see below.
11. Significance judged with appropriate statistical tests — **partial**
    (t-tests implicit in Table 5's clustered SEs; no tests for AUC
    differences between models).
12. All final hyperparameters listed — **partial → yes** ⚠ with a short
    appendix table (values below).

## Cheap upgrades before submission

A. **LICENSE file** in the repo (MIT or CC-BY for data) → items D3, C4 fully yes.
B. **Supplementary zip** (anonymized repo snapshot: src/, scripts/, synthetic
   data, macro CSVs) uploaded with the submission → D2, C3 fully yes.
C. **One sentence on infrastructure** (→ C7 yes), e.g.:
   "All experiments run on a single consumer laptop (Apple-silicon CPU, 16 GB
   RAM, macOS; Python 3.9) with scikit-learn 1.6, XGBoost 2.1, statsmodels
   0.14 and PyTorch 2.8 (CPU); no GPUs required. End-to-end runtime is under
   one hour."
D. **One sentence on runs** (→ C9 yes): "Each reported result is a single run
   with a fixed seed; simulation aggregates are stable across seeds."
E. **Appendix hyperparameter table** (→ C12 yes):
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
F. (Optional, turns C10 into yes) Report dispersion: run the simulation over
   ~10 seeds and report the sd of the annual separation rate, and/or bootstrap
   95% CIs for the AUC gaps in Table 2. Can be computed on request.
