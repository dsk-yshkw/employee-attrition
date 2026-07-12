# Draft — Discussion, Limitations, Conclusion

Draft prose for Sections 6–8. Numbers match `paper/tables/` and `figures/`;
citation keys follow `paper/related_work.md`.

---

## 6. Discussion

**Three lenses, one story.** Our interpretability results are mutually
reinforcing. SHAP on the separation model shows real income lowering separation
risk monotonically (§5.2); the extensive-margin elasticity puts a number on that
gradient and shows it is steeper for non-regular workers (§5.3); and the
relative-wage analysis shows that what bites is a worker's pay *relative to the
market*, asymmetrically, when they fall behind (§5.4). Read together, they
describe a coherent extensive-margin labor-supply response: the value of staying
falls as real and relative pay deteriorate, and the marginal worker who quits is
disproportionately non-regular. That the same heterogeneity appears in the
*dynamic* inflation scenarios (§5.6) — where the attrition response concentrates
on dispatch and contract workers — is evidence that the microsimulation inherits,
rather than distorts, the structure found in the static analyses.

**Policy implications.** Three follow directly. (i) *Inflation's separation cost
is distributional.* A general price shock barely moves the aggregate quit rate but
raises separation sharply for precarious workers, so the labor-market cost of
inflation is borne unevenly — a fact invisible to an aggregate or single-year
model. (ii) *Wage indexation is an effective lever.* Because full cost-of-living
adjustment restores both real income and attrition to baseline, the operative
channel is real-wage erosion, not inflation per se; indexing pay (or targeted
raises for lagging groups) neutralizes the attrition effect. (iii) *Retention is
about relative standing.* Firms whose pay merely keeps its nominal level while the
market rises will lose workers; retention policy should track the market and the
distribution of raises, not just the wage bill — echoing, with national data and
external market wages, the firm-level lessons of Card et al. (2012) and Dube et al.
(2019).

**Methodological takeaway.** The recipe — learn calibrated one-step transition
kernels with modern ML, validate them *generatively* against held-out years, then
iterate them for multi-year forecasts and counterfactuals — is not specific to
attrition. It offers dynamic microsimulation (Strand E) a data-driven alternative
to hand-specified transition equations while preserving interpretability and
policy use, and it gives ML attrition work (Strand A) a path from one-year scoring
to multi-year, decision-relevant simulation. Calibration is the crux: the same
model that ranks well for prediction (with class reweighting) is miscalibrated for
simulation, and only base-rate-accurate probabilities reproduce observed dynamics.

## 7. Limitations

**Descriptive, not causal.** Our elasticity and relative-wage coefficients are
conditional associations, not structural causal parameters. Wages are not randomly
assigned; unobserved worker quality can drive both pay and separation, and reverse
causality is possible (workers likely to leave may receive — or be denied —
raises). Year (and industry) fixed effects and the leave-one-out *market* wage,
which is set above the individual, mitigate these threats, and the asymmetric
shortfall result is hard to rationalize as pure reverse causality; but we do not
claim identification of a causal labor-supply elasticity. A causal treatment
(worker fixed-effects conditional logit, instrumenting own-wage growth with the
market component, or double/debiased ML in the spirit of Wager & Athey 2018 and
Chernozhukov et al. 2018) is left to future work.

**Simulation assumptions.** The microsimulation holds static attributes
(education, industry, occupation, firm size, contract type, family) fixed, models
wages by their conditional mean plus noise, treats the cohort as closed (no new
entrants), and assumes sticky nominal wages absent an explicit indexation
scenario. These are transparent, conservative choices; richer versions would let
industry/occupation and contract type transition, add heteroskedastic wage draws,
and open the cohort. The back-test horizon is four years, bounded by data.

**Measurement.** JPSED annual income is coarse (the median year-on-year change is
zero), so own wage growth is noisy; separation is self-reported ("quit/left a
job") and may bundle voluntary and involuntary exits; and the external wage series
is establishment-based (MHLW), a reference *trend* rather than an individual-level
counterfactual. The 2016 wave, with a different question structure, is not yet
integrated, which would extend histories and the back-test.

**Model scope.** The sequence-model comparison is limited by short histories
(≤8 waves); on longer panels the ranking could change. And attrition is one margin
of labor supply — hours (the intensive margin) and labor-force entry are outside
our current scope.

## 8. Conclusion

We recast employee attrition from a one-year prediction task into a calibrated,
learning-based microsimulation, and used it both to forecast multi-year separation
under policy scenarios and to recover interpretable labor-supply quantities on a
large national panel. Gradient-boosted trees are the strongest predictors and
sequence models add little; the wage-elasticity of retention is modest overall but
concentrated among non-regular workers; workers who fall behind their industry's
market wage separate more; and a simulated inflation shock erodes real pay and
raises separation for precarious workers unless wages are indexed. The through-line
— from prediction, to calibrated generative dynamics, to an extensive-margin
labor-supply reading, to distributional policy analysis — connects the ML and
labor-economics literatures that have largely studied attrition apart. Future work
will pursue causal identification, integrate the earliest wave and longer
industry×year histories for a decade-plus panel, and enrich the destination states
(intensive margin, non-employment spells). Code, the public macro data, and
synthetic data are released for reproducibility.
