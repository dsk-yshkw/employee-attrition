# Paper outline — AAAI submission

**Status**: outline for drafting. Numbers below are the current pipeline results
(real JPSED data, 2017–2025); re-run `scripts/make_figures.py` and `src.pipeline`
before freezing final digits.

## Working titles

1. *From Prediction to Policy: A Learning-Based Microsimulation of Employee
   Attrition and the Wage-Elasticity of Retention*
2. *Falling Behind the Market: Relative Wages, Inflation, and Job Separation in a
   Learned Labor-Supply Microsimulation*
3. *Learning a Dynamic Labor-Supply Model of Attrition from Japanese Panel Data*

Recommended: **#1** (states method + economic payoff). Keep "microsimulation",
"attrition", "labor supply" in the title for searchability.

## Venue / track

- Target: AAAI main track, or **AI for Social Impact** track (better fit — the
  contribution is an AI method applied to a social/economic question with a
  policy payoff). Decide based on the CFP; AISI reviewers reward the
  policy-scenario and distributional-equity angle.
- One-line pitch: *We turn a panel of individual employment histories into a
  calibrated, ML-driven microsimulation that predicts multi-year attrition,
  recovers an interpretable wage-elasticity of job retention, and runs
  inflation / wage-policy counterfactuals — showing inflation's separation cost
  falls on non-regular workers and is neutralized by wage indexation.*

## Abstract (draft skeleton, ~180 words)

- Problem: attrition is usually modeled as a one-year binary prediction; that
  can't answer multi-year or policy ("what if inflation / minimum wage")
  questions, and doesn't connect to labor-supply theory.
- What we do: on a 9-wave Japanese household panel (JPSED, 2017–2025, ~129k
  workers) we (i) benchmark predictors, (ii) fit calibrated transition
  sub-models (separation, re-employment, wage), (iii) compose them into a
  microsimulation validated against held-out years, and (iv) read the separation
  model as an extensive-margin labor-supply relation.
- Findings: gradient-boosted trees beat GRU/Transformer on this short-sequence
  tabular panel; retention has a positive wage-elasticity that is larger for
  non-regular workers; inflation erodes real wages and raises separation
  concentrated among non-regular workers, neutralized by wage indexation; workers
  who fall behind their industry's market wage separate more.
- Takeaway: a bridge from predictive ML to interpretable, policy-relevant
  labor-supply microsimulation.

## 1. Introduction

- Hook: labor shortages + the 2022–2024 inflation shock in Japan → real wages
  fell even as nominal wages rose; who quits, and does inflation change it?
- Gap 1 (method): one-year attrition classifiers can't do multi-year trajectories
  or counterfactual policy; they're descriptive, not generative.
- Gap 2 (interpretation): ML attrition models rarely connect to the economics of
  labor supply (the quit decision as a discrete choice on the extensive margin).
- Our approach in one paragraph + the four contributions.
- Preview of headline results (backtest fig, distributional inflation result).

### Contributions (bulleted)

1. A **learning-based attrition microsimulation**: calibrated ML transition
   sub-models composed into a forward-iterating dynamic model, back-tested on
   held-out years, with wage-policy / inflation counterfactuals.
2. An **interpretable labor-supply reading**: extensive-margin wage-elasticity of
   retention from the (RUM/logit) separation model, with heterogeneity by
   contract type, triangulated with SHAP.
3. A **relative-wage / reference-dependence** result using external industry×year
   market wages: falling behind the market raises separation, identified within
   year fixed effects.
4. **Honest ML benchmarking on a real panel**: trees > GRU/Transformer on short
   sequences; macro features don't help static prediction but are essential to
   the dynamics — with a reproducible pipeline and public code.

## 2. Related work

- Employee/turnover attrition prediction (HR analytics, IBM-attrition-style ML).
- Survival / discrete-time hazard models of job separation (econometrics).
- Microsimulation & agent-based models in labor economics / dynamic
  microsimulation (policy simulation tradition).
- Labor supply & quit behavior: random-utility discrete choice, reservation
  wages, relative/reference wages (Akerlof-Yellen fair-wage, relative income).
- ML interpretability (SHAP) and its use for social-science inference.
- Sequence models on tabular/panel data; why trees still win.
- Position: we connect the predictive-ML and structural-microsimulation strands.

## 3. Data

- JPSED (Japanese Panel Study of Employment Dynamics, RIKEN/Recruit; SSJDA),
  9 waves 2017–2025, ~129k persons, employees only (Q17 employed × Q18 = wage
  employee). Table: waves, N, attrition base rates.
- Variable harmonization across waves (question renumbering + casing) →
  `variable_map`. Two labels: actual separation (Q57/Q58 "quit/left", ~8%/yr)
  and turnover intention (Q106/Q105, ~19%).
- External macro data (cite `data/macro/REFERENCES.md`): CPI (Statistics Bureau);
  society-wide and **industry×year** nominal wage growth (MHLW Monthly Labour
  Survey). Real income = nominal / CPI(ref year).
- Ethics/reproducibility: microdata access via SSJDA; public code + synthetic
  data + bundled public macro data.

## 4. Methods

### 4.1 Prediction benchmark
- Features (23): demographics, household, employment, tenure, nominal + real
  wage & growth, CPI/inflation. Time-based split (train < test year).
- Models: logistic, HistGBM, XGBoost; GRU / Transformer / MLP on per-worker
  sequences (≤ history length). Metric: ROC-AUC, PR-AUC.

### 4.2 Transition sub-models (calibrated)
- separation P(quit); re-employment P(job next Dec | quit); nominal wage
  regressions for stayers and movers. No class-reweighting → calibrated to base
  rates (needed by the simulation). Validate 1-year (AUC / R²).

### 4.3 Microsimulation
- State = feature vector; each year draw separation → stay (wage_stay, tenure+1)
  / move→re-employ (wage_move, tenure=0) / exit; age+1; deflate nominal wage by
  the (scenario) CPI. Assumptions stated (static attributes, closed cohort,
  sticky nominal wages). Backtest vs actual attrition on held-out years.
- Scenarios: inflation path (±pp), wage indexation (COLA passthrough), minimum
  wage floor, by-group breakdown.

### 4.4 Labor-supply interpretation
- Separation logit as extensive-margin random-utility choice; wage-elasticity of
  retention = %Δ P(stay) per %Δ real wage; heterogeneity by contract type.
- **Relative wage**: own vs industry×year market wage growth (leave-one-out);
  identification within year (and industry) fixed effects; descriptive framing
  with FE robustness, threats stated (endogeneity, ability).

## 5. Results

- **5.1 Prediction**: Table (target × model AUC/PR-AUC). Trees best (separation
  XGB ≈ 0.73; intention ≈ 0.67); GRU/Transformer ≈ MLP < trees → history adds
  little on ≤8-step sequences. Macro features leave static AUC unchanged
  (explain why). → *fig: (optional) AUC bars.*
- **5.2 What drives attrition (SHAP)**: importance tenure ≫ occupation > age >
  industry > contract > real income; dependence monotone in real income; tenure
  U-shaped (protective until near retirement). → *fig_importance, fig_shap_depend.*
- **5.3 Wage-elasticity of retention**: overall ≈ 0.013; non-regular >> regular
  (dispatch ≈ 0.029 vs regular ≈ 0.014). → *fig_elasticity.*
- **5.4 Relative wage / falling behind**: separation rises for workers whose wage
  growth lags their industry's market (quintile gradient; "lag most" ≈ 0.10 vs
  ≈ 0.06 mid); shortfall coefficient positive within year FE. → *fig_relwage.*
- **5.5 Microsimulation backtest**: simulated attrition tracks actual (~0.08)
  over held-out years. → *fig_backtest.*
- **5.6 Inflation & policy scenarios**: +4pp inflation erodes mean real income
  ~350→296 man-yen, small aggregate attrition rise; full wage indexation restores
  both; effect concentrates on non-regular workers (dispatch 0.175→0.207 vs
  regular ~flat). → *fig_scenarios, fig_contract.*
- **5.7 Robustness**: panel-attrition weighting (weighted separation ~0.3pp
  higher, elasticity unchanged); seeds; alternative reference groups.

## 6. Discussion

- The three interpretation angles (SHAP dependence, elasticity, relative wage)
  agree: real/relative wages govern the extensive margin — a coherent
  labor-supply story.
- Policy: inflation's separation cost is distributional (non-regular workers);
  wage indexation is an effective lever; retention policy should target relative
  standing, not just level.
- Method: calibrated ML sub-models + microsimulation generalizes beyond attrition
  to other dynamic labor outcomes.

## 7. Limitations

- Descriptive, not causal: elasticity is a conditional association; FE and the
  market-wage design reduce but don't eliminate endogeneity (ability, reverse
  causality via retention offers).
- Simulation assumptions (static attributes, closed cohort, sticky nominal wages,
  no firm switching of industry/occupation); wage models are conditional means.
- Establishment-based external wages are a reference trend, not individual-level.
- Short sequences limit the sequence-model comparison; y16 not yet integrated.

## 8. Conclusion

- Recap: prediction → calibrated dynamics → interpretable labor supply → policy.
- Future: causal identification (IV / worker FE conditional logit), longer panel
  (add y16; more industry×year history), richer destination states.

## Figures (in `figures/`, Okabe-Ito, PDF+PNG)

| Figure | Result | Section |
|---|---|---|
| fig_backtest | sim vs actual attrition | 5.5 |
| fig_scenarios | attrition & real income by scenario | 5.6 |
| fig_contract | inflation response by contract type | 5.6 |
| fig_shap_depend | SHAP dependence (income, tenure) | 5.2 |
| fig_importance | SHAP global importance | 5.2 |
| fig_elasticity | elasticity by contract | 5.3 |
| fig_relwage | falling behind market → attrition | 5.4 |

## Tables to build

1. Data: waves × N × base rates (separation, intention).
2. Prediction: target × model × {AUC, PR-AUC}.
3. Transition sub-models: validation (AUC, R², MAE).
4. Scenario summary: scenario × {end attrition, cumulative, end real income}.
5. Relative-wage regression: separation ~ own growth + market growth + shortfall
   (+ year/industry FE), coefficients.

## Drafting order (2-week plan)

1. Freeze numbers: re-run pipeline + figures, fill Tables 1–5.
2. Methods (4) + Results (5) first — they're closest to the code.
3. Intro + contributions + abstract.
4. Related work + discussion + limitations.
5. Polish, page limit, appendix (reproducibility, extra robustness).
