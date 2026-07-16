# Draft — Abstract & Introduction

Draft prose for the Abstract and Section 1. Numbers match `paper/tables/` and
`figures/`. Citation keys follow `paper/related_work.md`.

---

## Abstract (~185 words)

Employee attrition is almost always modeled as a one-year binary prediction. That
framing cannot answer multi-year or policy questions — *how does a sustained
inflation shock change who quits, and does wage indexation help?* — and it is
disconnected from the economics of labor supply. We turn a nine-wave Japanese
household panel (JPSED, 2017–2025; ≈129k workers) into a calibrated, learning-based
microsimulation of job separation. We (i) benchmark predictors and find
gradient-boosted trees beat GRU/Transformer models on these short employment
histories; (ii) fit *calibrated* transition sub-models (separation, re-employment,
wage) and compose them into a microsimulation that reproduces held-out separation
rates; and (iii) read the separation model as an extensive-margin labor-supply
relation. The wage-elasticity of retention is positive but modest and much larger
for non-regular workers; using external industry×year market wages, we show that
*falling behind the market* — not relative position per se — raises separation,
robust to year fixed effects. In counterfactuals, a four-percentage-point
inflation shock erodes
real wages and raises separation concentrated among non-regular workers, an effect
neutralized by full wage indexation. The result is a bridge from predictive ML to
interpretable, policy-relevant labor-supply microsimulation, with public code.

---

## 1. Introduction

Japan entered the 2020s with acute labor shortages and, in 2022–2024, its sharpest
inflation in four decades. A striking feature of that episode is that **nominal
wages rose while real wages fell**: in our data, mean nominal annual earnings among
employees drifted up even as mean real earnings declined. This raises a question
that matters for firms and policymakers alike — *when inflation erodes real pay,
who leaves their job, and can wage policy change the answer?* Standard attrition
models cannot address it.

**Attrition as prediction, and its limits.** In machine learning, employee
attrition is studied as a one-year binary classification problem, increasingly
with neural architectures and peer/contagion effects (Teng et al. 2019; Transformer
variants). These models optimize predictive accuracy on a single transition. But a
one-year classifier is *descriptive*, not *generative*: it cannot be rolled forward
to produce multi-year attrition trajectories, it cannot answer counterfactual
policy questions ("what if inflation were 4 points higher, or wages were indexed
to prices?"), and its coefficients are not economic parameters. Meanwhile, a large
labor-economics literature shows that the quit decision is governed by *relative*
and *reference* wages — workers compare their pay to peers and to the market, rank
matters more than level, and quits track relative rather than absolute wages (Card,
Mas, Moretti & Saez 2012; Dube, Giuliano & Leonard 2019) — yet ML attrition models
rarely make contact with this theory or with the wage data needed to test it.

**This paper.** We bridge the two. Using JPSED — a nine-wave, nationally
representative Japanese panel of ≈129k workers (2017–2025) — we build a
*learning-based microsimulation* of job separation and use it both to forecast
multi-year attrition under policy scenarios and to recover interpretable
labor-supply quantities. The construction has three parts. First, we benchmark
one-year prediction under a strict time-based split; gradient-boosted trees are the
strongest model and, consistent with recent tabular-ML evidence (Grinsztajn et al.
2022), GRU/Transformer sequence models do not help on these short histories.
Second, and central to the paper, we fit *calibrated* transition sub-models —
separation, re-employment, and nominal wages for stayers and movers — deliberately
avoiding the class-reweighting used for ranking, so that predicted probabilities
match true base rates. Composing them yields a microsimulation that we *back-test*:
initialized on a past cohort and rolled forward, it reproduces the held-out annual
separation rate (≈0.08). Third, we read the separation model as the extensive
margin of labor supply (a random-utility quit choice), summarize the
wage-elasticity of retention, and — using **external industry×year market wages**
from official statistics — test whether workers who fall behind their market
separate more, identified within year fixed effects.

**Findings.** (1) Trees beat sequence models; macro features do not raise
single-year AUC but are essential to the dynamics. (2) The wage-elasticity of
retention is modest on average but much larger for non-regular (dispatch/contract)
workers. (3) *Falling behind the market* raises separation — the effect is
asymmetric (the shortfall matters, not symmetric relative position) and survives
year fixed effects — echoing, at national scale and with external wage data, the
firm-level relative-pay results of Card et al. (2012) and Dube et al. (2019). (4)
In counterfactuals, a +4 percentage-point (pp) inflation path erodes real income (mean ≈350→296 man-yen
over four years) with a small aggregate but sharply *distributional* attrition
response — concentrated on non-regular workers (dispatch 0.175→0.207 vs regular
≈unchanged) — and full wage indexation restores both real income and attrition to
baseline, isolating real-wage erosion as the operative channel.

**Contributions.**
1. A **learning-based attrition microsimulation**: calibrated ML transition
   sub-models composed into a forward-iterating, back-tested dynamic model with
   inflation / wage-indexation / minimum-wage counterfactuals.
2. An **interpretable labor-supply reading**: an extensive-margin wage-elasticity of
   retention with contract-type heterogeneity, triangulated with SHAP.
3. A **relative-wage / reference-dependence** result using external industry×year
   market wages, identified within year fixed effects, connecting ML attrition to
   the relative-pay tradition in labor economics.
4. **Honest ML benchmarking** on a large real panel (trees > sequence models; macro
   features irrelevant to static AUC but essential to dynamics), with a fully
   reproducible pipeline and public code.

We situate the work at the intersection of ML turnover prediction, tabular-ML and
interpretability, ML-in-economics, relative-pay labor economics, and dynamic
microsimulation (§2), detail methods in §4, report results in §5, and discuss
policy implications and the descriptive-vs-causal boundary in §6–7.
