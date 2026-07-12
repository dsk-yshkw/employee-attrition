# Related work — bibliography & draft

Citations below were located via web search and verified against the publisher
(AEA / NeurIPS / AAAI / NBER / IZA / JASA) where a link is given. Items marked
**[verify]** still need an author/year/venue check before the final bibliography.
Search performed 2026-07.

## Strand A — Employee attrition / turnover prediction (ML)

- **Teng, Zhu, Liu, Zhu, Xiong (2019).** "Exploiting the Contagious Effect for
  Employee Turnover Prediction." *AAAI 2019*, 33(1):1166–1173.
  https://ojs.aaai.org/index.php/AAAI/article/view/3910 — the closest ML prior:
  a contagious-effect neural network for one-year turnover using peer influence.
- **Employee Turnover Prediction: A Cross-component Attention Transformer …
  (2025).** arXiv:2502.01660. https://arxiv.org/pdf/2502.01660 — recent
  Transformer-based turnover model with competitor/contagion effects.
- **"Retention Is All You Need" (2023).** arXiv:2304.03103.
  https://arxiv.org/pdf/2304.03103 — SHAP-explained attrition prediction.
- **Predicting Employee Turnover: Scoping and Benchmarking the State-of-the-Art.**
  *Business & Information Systems Engineering* (Springer).
  https://link.springer.com/article/10.1007/s12599-024-00898-z — benchmark/survey. **[verify authors/year]**
- **Natural Language Processing for Human Resources: A Survey (2024).**
  arXiv:2410.16498. https://arxiv.org/pdf/2410.16498 — HR-analytics context.

*How we differ:* this strand does one-year binary prediction (often on the small
IBM HR dataset). We use a large nationally-representative panel, calibrate a
*generative* transition model, run a validated multi-year microsimulation with
policy counterfactuals, and connect the model to labor-supply theory.

## Strand B — Tabular ML & interpretability

- **Grinsztajn, Oyallon, Varoquaux (2022).** "Why do tree-based models still
  outperform deep learning on typical tabular data?" *NeurIPS 2022 Datasets &
  Benchmarks.* https://proceedings.neurips.cc/paper_files/paper/2022/file/0378c7692da36807bdec87ab043cdadc-Paper-Datasets_and_Benchmarks.pdf
  — supports our §5.1 (trees > GRU/Transformer here).
- **Lundberg & Lee (2017).** "A Unified Approach to Interpreting Model
  Predictions." *NeurIPS 2017.* https://neurips.cc/virtual/2017/oral/10008 —
  SHAP; our interpretability (§5.2). (Cite TreeSHAP, Lundberg et al. 2020 Nature
  Machine Intelligence, if used. **[verify]**)

## Strand C — ML in economics / prediction-policy / causal ML

- **Mullainathan & Spiess (2017).** "Machine Learning: An Applied Econometric
  Approach." *Journal of Economic Perspectives* 31(2):87–106.
  https://www.aeaweb.org/articles?id=10.1257/jep.31.2.87 — prediction vs
  estimation framing.
- **Kleinberg, Ludwig, Mullainathan, Obermeyer (2015).** "Prediction Policy
  Problems." *American Economic Review P&P* 105(5):491–495 — our
  prediction-for-policy motivation.
- **Athey (2019).** "Machine Learning Methods That Economists Should Know About."
  *Annual Review of Economics.* https://arxiv.org/pdf/1903.10075.
- **Wager & Athey (2018).** "Estimation and Inference of Heterogeneous Treatment
  Effects using Random Forests." *JASA* 113(523):1228–1242 — heterogeneity.
- **Chernozhukov et al. (2018).** "Double/Debiased Machine Learning for Treatment
  and Structural Parameters." *Econometrics Journal* 21(1):C1–C68 — cited in the
  limitations for a causal path beyond our descriptive elasticity.

## Strand D — Relative pay, fairness, and quits (labor economics)

- **Card, Mas, Moretti, Saez (2012).** "Inequality at Work: The Effect of Peer
  Salaries on Job Satisfaction." *American Economic Review* 102(6):2981–3003.
  https://www.aeaweb.org/articles?id=10.1257/aer.102.6.2981 — below-median earners
  report lower satisfaction and *higher job-search intent*; **rank matters more
  than level**. Direct antecedent of our relative-wage result (§5.4).
- **Dube, Giuliano, Leonard (2019).** "Fairness and Frictions: The Impact of
  Unequal Raises on Quit Behavior." *American Economic Review* 109(2):620–663.
  https://www.aeaweb.org/articles?id=10.1257/aer.20160232 — quits respond to
  *relative* pay/raises; after peer effects, quits are not very sensitive to own
  wage (search frictions). Strongly resonates with our asymmetric "falling
  behind the market" finding and our modest own-wage elasticity.

*How we differ:* those are firm-level natural experiments on satisfaction/quits;
we bring the relative-wage / outside-option logic to a national panel, operationalize
the market wage with **external industry×year** data, and embed it in a predictive
microsimulation with distributional policy scenarios.

## Strand E — Dynamic microsimulation / agent-based labor models

- **Li & O'Donoghue.** "A survey of dynamic microsimulation models: uses, model
  structure and methodology." *International Journal of Microsimulation.* **[verify author/year]**
- **Neugart & Richiardi.** "Agent-based models of the labor market."
  https://ideas.repec.org/p/cca/wplabo/125.html **[verify author/year/venue]**
- International Journal of Microsimulation, "Dynamic Microsimulation for Policy
  Analysis." **[verify]**

*How we differ:* classical dynamic microsimulations use reduced-form or
hand-specified transition equations; we *learn* the transition kernels with modern
ML, **calibrate** them for generative use (base-rate-accurate probabilities),
**back-test** the simulator against held-out years, and use it for
inflation/wage-indexation/minimum-wage counterfactuals.

---

## Draft prose (Section 2)

Our work sits at the intersection of five literatures. **(i) Turnover
prediction in ML** treats attrition as one-year binary classification, recently
with neural and peer/contagion effects (Teng et al. 2019, AAAI; and Transformer
variants); these optimize predictive accuracy but do not produce multi-year
trajectories, counterfactual policy answers, or economic parameters. **(ii)
Tabular ML** explains why our gradient-boosted trees beat sequence models on this
short panel (Grinsztajn et al. 2022), and SHAP (Lundberg & Lee 2017) supplies our
interpretability. **(iii) ML in economics** frames the prediction-vs-estimation
distinction and prediction-for-policy (Mullainathan & Spiess 2017; Kleinberg et
al. 2015; Athey 2019), and the causal-ML toolkit (Wager & Athey 2018;
Chernozhukov et al. 2018) marks the path from our descriptive elasticity toward
causal identification. **(iv) Relative pay and quits** in labor economics finds
that workers compare pay to peers and the market, that rank matters more than
level, and that quits track relative rather than absolute wages (Card, Mas,
Moretti & Saez 2012; Dube, Giuliano & Leonard 2019) — the theoretical anchor for
our "falling behind the market" result and our small own-wage elasticity. **(v)
Dynamic microsimulation** has long simulated labor-market policy with reduced-form
transition models; we contribute a *learned, calibrated, back-tested* microsimulation.
Our synthesis — learning calibrated transition kernels, validating them
generatively, and reading the separation model as an extensive-margin labor-supply
relation with an external relative-wage design — is, to our knowledge, new.

## To verify before submission
- Authors/year/venue for the four **[verify]** items.
- Exact page numbers for Kleinberg et al. (2015) and Athey (2019).
- Whether we cite TreeSHAP (Lundberg et al. 2020, Nature Machine Intelligence).
- Consider adding a Japan-specific JPSED / labor-mobility reference.
