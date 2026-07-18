# HANDOFF — Project briefing for AI assistants (and future sessions)

Purpose: a self-contained briefing so that an assistant (e.g. Claude on
claude.ai with this repo connected) can help with **paper structure, prose and
polishing** without access to the original working sessions. Written 2026-07.

---

## 1. What this project is

**Goal**: AAAI submission (deadline ~late July 2026). Public repo:
https://github.com/dsk-yshkw/employee-attrition

**One-line pitch**: We turn a nine-wave Japanese employment panel (JPSED,
2017–2025, ~129k workers) into a *calibrated, learning-based microsimulation* of
job separation — validated by back-testing, used for inflation/wage-policy
counterfactuals, and read as an extensive-margin labor-supply model
(wage-elasticity of retention, relative-wage effects).

**Central thesis**: the multi-year attrition **microsimulation** is the core
contribution; the labor-supply elasticity is the economic interpretation layer;
the prediction benchmark (trees vs GRU/Transformer) is supporting material.

**Working title (preferred)**: *From Prediction to Policy: A Learning-Based
Microsimulation of Employee Attrition and the Wage-Elasticity of Retention.*

## 2. Where everything is

| Content | File |
|---|---|
| Full outline, section plan, figure/table map | `paper/OUTLINE.md` |
| Abstract + Introduction draft | `paper/draft_abstract_intro.md` |
| Related work (5 strands, DOIs/arXiv IDs for Zotero) | `paper/related_work.md` |
| Methods + Results draft (§4–5) | `paper/draft_methods_results.md` |
| Discussion, Limitations, Conclusion draft (§6–8) | `paper/draft_discussion.md` |
| Tables 1–5 (Markdown + LaTeX) | `paper/tables/` |
| Figures (7, PDF+PNG, Okabe-Ito palette) | `figures/` |
| External data sources & citations | `data/macro/REFERENCES.md` |
| Reproducibility statement material | README "Data" section; synthetic data in `data/synthetic/` |
| Code pipeline | `src/` (see README) |

Tables and figures are **generated** by `scripts/make_tables.py` and
`scripts/make_figures.py` from the licensed microdata (not in the repo).

## 3. Canonical numbers (frozen 2026-07; regenerate scripts before final freeze)

**Data**: JPSED via SSJDA (surveys 1164/1227/1279/1349/1429/1523/1598/1730/1775),
9 waves 2017–2025, ~129k persons, ~500k person-years; employees only.
Separation base rate ≈ 0.08/yr (self-reported quit, Q57/Q58 battery); turnover
intention ≈ 0.19 (Q106/Q105 codes 1–2).

**Prediction (time-split; separation test=2024, intention test=2025)**:
- Separation: XGBoost ROC-AUC **0.728** / PR-AUC 0.195; HistGBM 0.709; logistic 0.657.
- Intention: XGBoost 0.668 / PR-AUC 0.305.
- Sequence models (≤8-step histories, separation test=2024): MLP (current state)
  ROC-AUC 0.707 / PR-AUC 0.174; GRU 0.705 / 0.160; Transformer 0.704 / 0.166.
  History adds nothing over the current-state MLP; all trail XGBoost (0.728),
  though MLP ≈ HistGBM (0.709) — say "trail the best tree ensemble", not "trail
  trees". Macro features leave single-year AUC unchanged (year-constant /
  monotone transforms) — their role is dynamic, not static.

**Transition sub-models (train <2023, test 2023)**: separation AUC 0.708,
**calibrated** (pred 0.086 vs obs 0.083); re-employment AUC 0.703; stayer wage
R² 0.786 (MAE ≈49 man-yen); mover wage R² 0.639 (MAE ≈72). No class-reweighting
(calibration is required for simulation).

**Microsimulation (cohort 2021, models trained ≤2020, 4 years)**: simulated
attrition tracks actual ≈0.08 (backtest). Scenarios: +4pp inflation → mean real
income ≈350→**296** man-yen, aggregate attrition nearly flat; **full COLA
restores both** (≈345). Distributional: dispatch separation 0.175→**0.207**,
contract 0.110→0.121, regular ≈unchanged (0.055→0.057).

**Elasticity (logit/RUM, test 2024)**: retention wage-elasticity ≈**0.013**
overall; dispatch ≈0.029 > contract/part > regular ≈0.014. (Trees give ~0 —
piecewise constant — hence logit for this quantity.)

**Relative wage (external industry×year market from MHLW Monthly Labour Survey,
2021–2024; JPSED industry → JSIC mapping)**: separation by own-vs-market growth
quintile: "lag most" ≈**0.102** vs mid ≈0.06 (lead ≈0.083, reflects job-change
raises). LPM with year FE, person-clustered SE: **shortfall (market−own)₊
coefficient 0.083 (SE 0.005)**; signed relative gap weak → the effect is
**asymmetric** (falling behind is what matters). Market growth itself +0.121
(SE 0.067) → procyclical quits. Interaction shortfall×market is *negative*
(the falling-behind penalty is larger in low-growth industries) — a nuanced
result; do not claim "amplified in booms".

**Robustness**: JPSED prior-year attrition weights (xa{t+1}_l{t}, 99.4%
coverage): weighted separation ~0.2–0.5pp higher; elasticity unchanged
(0.0132→0.0129). SHAP (TreeSHAP on XGBoost): importance tenure ≫ occupation >
age > industry > contract > real income; real-income dependence monotone
decreasing; tenure U-shaped (protective until near retirement).

**Uncertainty (computed 2026-07, `scripts/compute_uncertainty.py`)**:
simulation over 10 seeds — annual separation sd 0.0012–0.0016 (2024: 0.0755 ±
0.0015), end-year real income sd 0.36 man-yen (effectively deterministic at
cohort scale). Paired bootstrap (1,000 resamples, test=2024) ROC-AUC 95% CIs:
XGBoost 0.728 [0.718, 0.738]; HistGBM 0.709 [0.698, 0.720]; MLP 0.707 [0.695,
0.718]; GRU 0.705 [0.695, 0.716]; Transformer 0.704 [0.693, 0.714]; logistic
0.657 [0.645, 0.668]. XGBoost's gap excludes zero vs EVERY alternative
(vs HistGBM +0.019 [0.014, 0.024]; vs MLP +0.022 [0.015, 0.029]; vs GRU
+0.023; vs Transformer +0.025; vs logistic +0.072) — "trees beat sequence
models" is now a tested claim, and even vs HistGBM the XGBoost edge is
significant.

## 4. Framing decisions already made (do not relitigate silently)

- **Descriptive, not causal**: elasticity/relative-wage results are conditional
  associations with FE-based mitigation; causal ID (worker-FE conditional logit,
  IV, double-ML) is future work. Limitations section reflects this.
- **Employees only** (Q17 employed & Q18 wage employee); executives/self-employed excluded.
- Separation label = self-reported quit event (next wave), **not** the noisy
  job-start-year change (kept as diagnostic only).
- Wage sub-models predict **nominal** income; the simulator deflates by scenario
  CPI (sticky-nominal assumption; COLA scenario relaxes it).
- Venue angle: AAAI (possibly AI for Social Impact); the distributional/equity
  finding is a headline.
- Ethics statement drafted (data via SSJDA agreement, de-identified, aggregate
  reporting, synthetic+public data only in repo, dual-use caution). Short and
  minimal versions exist in session notes; integrate as space allows.

## 5. Division of labor (important for assistants)

- **Prose, structure, polishing**: safe to do anywhere (claude.ai etc.).
- **Any number in the text**: comes from `scripts/make_tables.py` /
  `make_figures.py` outputs. **Do not invent or "correct" numbers in prose** —
  if a number looks wrong, flag it for re-computation in the code environment
  (Claude Code on the author's machine, where the licensed microdata lives).
- Real microdata is **not** in the repo and cannot be shared; reproducibility is
  via public code + synthetic data + SSJDA application (see README).

## 6. Open items (as of handoff)

- Integrate the five drafts into one manuscript (author is doing this).
- §3 Data section: outline exists in OUTLINE.md; prose not yet drafted.
- `[verify]` citations in `related_work.md` (microsimulation survey, agent-based
  chapter, BISE benchmark survey authors/years).
- Optional analyses if requested: worker-FE conditional logit (within-person
  identification of the shortfall effect); 2017–2020 industry wage PDFs
  (different MHLW URL pattern, h29/h30); y16 wave for a 10-year panel.
- Final freeze: re-run `make_tables.py` + `make_figures.py`, re-check every
  number in the text against `paper/tables/`.
