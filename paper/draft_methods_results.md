# Draft — Methods & Results

Draft prose for Sections 4–5. Numbers match `paper/tables/` and `figures/`
(real JPSED data, 2017–2025). `[Fig X]` / `[Table X]` mark insertion points.
Notation kept light for a mixed AI/economics audience.

---

## 4. Methods

We study wage/salary employees in the Japanese Panel Study of Employment Dynamics
(JPSED), waves 2017–2025 (nine annual waves, ≈129k distinct persons). Each wave
records a respondent's December employment state and the previous calendar year's
income and job events; we link individuals across waves by their panel id. We
define an employee-year as a person who, in a given wave, was employed in December
(Q17 ∈ {working, on leave}) and worked for a company or organization (Q18 = wage
employee), excluding executives, the self-employed, family workers and home
workers. Two attrition labels are used [Table 1].

**Actual separation** comes from JPSED's retrospective job-event battery
("events at work during the past year", multiple answer; Q57/Q58 in recent
waves), whose first item is *"I quit / left a job"* (仕事を辞めた・退職した). The
timing makes this a genuine forward-looking label: the wave-*t* survey records
employment as of December of year *t−1*, and the wave-*t+1* survey asks about
events during calendar year *t* — exactly the interval between the two December
snapshots. For a worker employed at the wave-*t* baseline, we therefore code
separation = 1 if they report the quit event in wave *t+1* (base rate ≈8%/yr).
This is a self-report of the worker's own action rather than an inference from
changed job attributes; its one caveat is that "quit / left" need not be purely
voluntary (§7).

**Turnover intention** is stated in the current wave (Q106/Q105): *"currently
want to change jobs and am searching"* (1), *"currently want to change jobs but
am not searching"* (2), *"would like to change jobs eventually"* (3), *"no
intention of changing jobs"* (4). We code intention = 1 for responses 1–2 — a
present-tense desire to move, with or without active search — and 0 for the
vaguer "eventually" and "no intention" responses (≈19%). (The pipeline also
supports the broader coding that includes response 3; we report the stricter
definition.)

Because JPSED renumbers questions and changes its column-naming convention
across waves (e.g. the event battery is Q50/Q55/Q59/Q53/Q59/Q57/Q58 across
2017–2025), we harmonize every variable to a stable canonical name via a
per-wave map before any modeling.

Each employee-year is described by 23 features in four blocks: demographics and
household (7: sex, age, education, has-spouse, has-child, number of children,
youngest-child age), employment (8: contract type, a regular-employment dummy,
industry, firm size, occupation, managerial rank, weekly hours, tenure), nominal
pay (3: annual income, prior-year income, income growth), and macro/real terms
(5: CPI, inflation, real income, prior-year real income, real income growth).
Real income deflates nominal income by the consumer price index of its reference
calendar year (Statistics Bureau of Japan). Separately from these model features,
the relative-wage analysis of §4.4 uses external nominal wage growth —
economy-wide and by industry×year — from the MHLW Monthly Labour Survey (sources
in `data/macro/REFERENCES.md`); the market rate enters that analysis as a
reference series, not as a predictor in the feature matrix.

### 4.1 Prediction benchmark

We first benchmark one-year attrition prediction under a **time-based split**:
models train on waves strictly before a held-out test wave (separation test =
2024, intention test = 2025), so evaluation is genuinely out-of-time. We compare
a regularized logistic regression, two gradient-boosted tree ensembles
(scikit-learn `HistGradientBoosting`, XGBoost), and three neural models on
per-worker sequences of feature vectors ordered by wave — an MLP on the latest
state, a GRU, and a Transformer encoder — reading each worker's history up to its
length (≤8 steps). Categorical features use native handling (tree ensembles) or
embeddings/one-hot (neural, linear). We report ROC-AUC and PR-AUC.

### 4.2 Transition sub-models

The simulation needs the *joint* one-year dynamics, not just a quit probability.
For each employee-year with a following wave we fit four calibrated sub-models:

- **Separation** `p_s(x) = P(quit within the year | x)`;
- **Re-employment** `p_r(x) = P(employed next December | quit, x)`;
- **Stayer wage** `w_stay(x) = E[nominal income next | stayed, x]`;
- **Mover wage** `w_move(x) = E[nominal income next | quit & re-employed, x]`.

All four are gradient-boosted tree models (scikit-learn `HistGradientBoosting`),
which fit our data without preprocessing: missing values are routed by a learned
per-split direction rather than imputed — much of our missingness is structural
(e.g., youngest-child age is asked only of parents) — and nominal codes such as
industry are split as categorical sets rather than forced into a spurious numeric
order. Crucially, the classifiers here use **no class re-weighting**. Up-weighting
rare positives is standard when probabilities are used only to *rank* workers by
risk, as in the prediction benchmark of §4.1 [Table 2], but it inflates predicted
probabilities far above the observed base rate. The simulation instead *draws*
separation events from these probabilities and rolls the cohort forward — a
generative use — so they must be calibrated: with re-weighted classifiers the
simulated annual separation rate comes out several times the actual ≈8%. Wage models
predict **nominal** income so that the simulator can deflate by a scenario-specific
price path (a sticky-nominal-wage assumption). We validate each sub-model on a
held-out wave [Table 3].

### 4.3 Microsimulation

We compose the sub-models into a discrete-time microsimulation (Algorithm 1). A
base-year cohort of employees is initialized with its observed feature vectors;
each simulated year, every still-employed worker faces a separation draw, then —
if separated — a re-employment draw; wages are set by the stayer or mover wage
model, the policy levers (indexation, wage floor) are applied to the nominal
wage, and real income is obtained by deflating with the scenario CPI.

```latex
\begin{algorithm}[tb]
\caption{Multi-year attrition microsimulation}
\label{alg:microsim}
\textbf{Input}: base-year employee states $\mathcal{X}=\{x_i\}$; fitted
sub-models $p_s, p_r, w_{\mathrm{stay}}, w_{\mathrm{move}}$; scenario CPI path
$\{P_t\}$ with inflation $\{\pi_t\}$\\
\textbf{Parameter}: horizon $T$; COLA pass-through $\kappa\in[0,1]$; optional
nominal wage floor $\underline{w}$\\
\textbf{Output}: yearly aggregates $\{A_t\}_{t=1}^{T}$ (separation and exit
rates, mean nominal and real income, cohort size)
\begin{algorithmic}[1]
\FOR{$t = 1$ \TO $T$}
  \FORALL{workers $i \in \mathcal{X}$}
    \STATE draw $s_i \sim \mathrm{Bernoulli}\big(p_s(x_i)\big)$
    \IF{$s_i = 0$}
      \STATE $w_i \leftarrow w_{\mathrm{stay}}(x_i)$;\quad
             $\mathrm{tenure}_i \leftarrow \mathrm{tenure}_i + 1$
    \ELSE
      \STATE draw $r_i \sim \mathrm{Bernoulli}\big(p_r(x_i)\big)$
      \IF{$r_i = 1$}
        \STATE $w_i \leftarrow w_{\mathrm{move}}(x_i)$;\quad
               $\mathrm{tenure}_i \leftarrow 0$
      \ELSE
        \STATE remove $i$ from $\mathcal{X}$ \COMMENT{exits employment}
      \ENDIF
    \ENDIF
    \STATE $w_i \leftarrow \max\{\, w_i (1 + \kappa \pi_t),\ \underline{w} \,\}$
           \COMMENT{indexation; wage floor}
    \STATE $\mathrm{age}_i \leftarrow \mathrm{age}_i + 1$;\quad
           real income $\leftarrow w_i / (P_t / 100)$;\quad update growth features
  \ENDFOR
  \STATE record $A_t$
\ENDFOR
\STATE \textbf{return} $\{A_t\}$
\end{algorithmic}
\end{algorithm}
```

Static attributes (education, industry, occupation, firm size, contract type,
family) are held fixed; predicted wages receive small Gaussian noise;
the cohort is closed (no new entrants). We **back-test** by training the
sub-models on the earliest waves, initializing on the last training wave, and
comparing the simulated annual separation rate to the actual rate in the held-out
years [Fig backtest].

Counterfactual **scenarios** override Algorithm 1's inputs: the CPI path
$\{P_t\}$ (e.g. +2/+4 pp inflation), the COLA pass-through $\kappa$ (0 = sticky
nominal wages, 1 = wages fully track prices), the nominal wage floor
$\underline{w}$ (minimum wage), and per-group breakdowns [Table 4, Fig
scenarios, Fig contract].

### 4.4 Labor-supply interpretation

We read the separation model as the extensive margin of labor supply: a worker
stays if the utility of the current job exceeds that of the outside option, so
`p_s` is a random-utility choice probability. We summarize the **wage-elasticity
of retention** as the percentage change in the retention probability `1 − p_s`
for a one-percent change in real wage, averaged over the test population, and
report it overall and by contract type [Fig elasticity]. Because tree ensembles
are piecewise-constant (locally zero gradient), the elasticity uses a logit
specification; SHAP on the tree model (§5.2) provides an independent read of
direction and shape.

**Relative wage.** The outside option is the market wage, which rises with
economy-wide pay. We therefore construct, for each worker, the gap between their
own nominal wage growth and the market rate for the same period — using the
**industry×year** market rate where available (leave-one-out at the JSIC-division
level), which supplies within-year variation. We estimate linear probability
models of separation on own growth, the market rate, the signed relative gap, and
the rectified **shortfall** `(market − own)₊` (how far a worker has fallen behind),
with **year fixed effects** and person-clustered standard errors [Table 5]. This
is a descriptive/reduced-form identification: year FE absorb macro shocks and the
market rate is set above the individual, but we do not claim a structural causal
elasticity (§7).

---

## 5. Results

### 5.1 Prediction: trees beat sequence models

Gradient-boosted trees give the best out-of-time prediction [Table 2]. For actual
separation, XGBoost reaches ROC-AUC 0.728 (PR-AUC 0.195) vs 0.709 for
HistGradientBoosting and 0.657 for logistic regression; turnover intention is
harder (XGBoost 0.668). The sequence models do **not** help: the GRU and
Transformer match or trail a plain MLP on the latest state and all trail the tree
ensembles, because JPSED histories are short (≤8 steps) and the signal is
cross-sectional rather than sequential. We also find that the macro/real-income
features leave single-year AUC essentially unchanged: within one test wave, CPI
and inflation are constant and real income is a monotone transform of nominal
income, so they carry no cross-sectional rank information. Their value is dynamic,
not static (§5.6). These are useful negative results for practitioners: on
tabular employment panels of this size, well-tuned trees remain the strong
baseline, and history/deep architecture buys little.

### 5.2 What drives separation (SHAP)

TreeSHAP on the XGBoost separation model orders global importance as **tenure ≫
occupation > age > industry > contract type > real income**, with the macro
features near zero [Fig importance]. Dependence is signed and interpretable [Fig
shap_depend]: the contribution of **real income is monotonically decreasing** —
higher real pay lowers separation risk — and **tenure is U-shaped**, strongly
protective through mid-career but rising again near retirement age. Because
tenure, age and income are correlated, SHAP splits credit among them; we read them
as a group. The real-income dependence is the micro-level counterpart of the
labor-supply elasticity below.

### 5.3 Wage-elasticity of retention

The extensive-margin wage-elasticity of retention is positive but modest overall
(≈0.013): higher real wages retain workers, but the average employee's stay
decision is not very wage-sensitive. The elasticity is strongly **heterogeneous
by contract type** [Fig elasticity]: non-regular workers are far more
wage-responsive than regular employees (dispatch ≈0.029 vs regular ≈0.014),
consistent with weaker attachment and thinner non-wage ties to the firm.

### 5.4 Falling behind the market

Separation rises sharply for workers whose pay has fallen behind their industry's
market wage [Fig relwage]. Sorting employees by own-minus-market wage growth, the
"lag most" quintile separates at ≈0.10 versus ≈0.06 in the middle. In linear
probability models with year fixed effects and person-clustered errors [Table 5],
the **shortfall** `(market − own)₊` carries a coefficient of 0.083 (SE 0.005):
falling ten percentage points behind the market raises the annual separation
probability by ≈0.8 points. The effect is **asymmetric** — the signed relative
gap alone is weak, but the rectified shortfall is strong — so it is falling
behind, not merely relative position, that drives quitting. The market rate itself
enters positively (0.121, SE 0.067): separations are procyclical, rising when the
outside option improves.

### 5.5 Microsimulation backtest

Trained on the earliest waves and initialized on the last training wave, the
microsimulation reproduces the held-out separation trajectory: simulated annual
attrition tracks the actual rate around 0.08 across the test years [Fig backtest],
and the separation sub-model is well calibrated (predicted 0.086 vs observed 0.083
at the held-out wave [Table 3]). This validates using the model generatively for
multi-year and counterfactual questions.

### 5.6 Inflation and policy scenarios

A sustained inflation shock erodes real pay with only a small *aggregate* attrition
response but a sharp *distributional* one [Table 4, Figs scenarios, contract]. A
+4pp inflation path lowers the cohort's mean real income from ≈350 to ≈296 man-yen
over four years while the aggregate separation rate barely moves; **full wage
indexation (COLA) restores both** real income (≈345) and attrition to baseline,
isolating real-wage erosion as the operative channel. The attrition response is
concentrated among **non-regular workers**: under +4pp inflation dispatch-worker
separation rises from 0.175 to 0.207 and contract workers from 0.110 to 0.121,
while regular employees are essentially unchanged (0.055→0.057). Inflation's
separation cost is thus borne by precarious workers and is a policy lever
(indexation, wage floors), not a uniform shock — the same heterogeneity seen in
the elasticity (§5.3) and relative-wage results (§5.4).

### 5.7 Robustness

Applying JPSED's prior-year panel-attrition weights (which re-weight the two-year
continuing sample to the population; 99.4% coverage) leaves conclusions intact:
attrition-weighted separation rates are 0.2–0.5 pp higher than unweighted
(continuers slightly under-state attrition) and the retention elasticity is
unchanged (0.0132→0.0129). Results are stable across simulation seeds and
alternative market-reference groups (economy-wide vs industry×year).
