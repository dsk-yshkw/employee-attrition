# Related work — bibliography & draft

Citations located via web search and verified against the publisher (AEA /
NeurIPS / AAAI / NBER / IZA / JASA / Wiley / Oxford) where a link is given. Items
marked **[verify]** still need an author/year/venue check. Search performed
2026-07.

## Note on Zotero identifiers (read me)

Most entries here are **journal articles or conference papers — they do not have
an ISBN** (ISBNs are for books; a proceedings *volume* may carry one, but the
per-paper identifier is not an ISBN). For Zotero's *Add Item by Identifier*, use,
in order of preference:

- **DOI** — works for all the journal articles and the AAAI paper below;
- **arXiv ID** — for the preprints / NeurIPS papers (enter e.g. `arXiv:2207.08815`);
- **ISSN** — identifies the *journal*, not the article; given for convenience.

Each entry lists its identifiers on an `→ ids:` line, ready to paste into Zotero.

## Strand A — Employee attrition / turnover prediction (ML)

- **Teng, M., Zhu, H., Liu, C., Zhu, C., Xiong, H. (2019).** "Exploiting the
  Contagious Effect for Employee Turnover Prediction." *AAAI 2019*, 33(1):1166–1173.
  https://ojs.aaai.org/index.php/AAAI/article/view/3910
  → ids: DOI 10.1609/aaai.v33i01.33011166
- **Employee Turnover Prediction: A Cross-component Attention Transformer …
  (2025).** Preprint. https://arxiv.org/abs/2502.01660
  → ids: arXiv:2502.01660
- **"Retention Is All You Need" (2023).** Preprint (SHAP-explained attrition).
  https://arxiv.org/abs/2304.03103
  → ids: arXiv:2304.03103
- **Predicting Employee Turnover: Scoping and Benchmarking the State-of-the-Art.**
  *Business & Information Systems Engineering* (Springer).
  https://link.springer.com/article/10.1007/s12599-024-00898-z
  → ids: DOI 10.1007/s12599-024-00898-z; ISSN 2363-7005 (print) / 1867-0202 (online).
  **[verify authors/year]**
- **Natural Language Processing for Human Resources: A Survey (2024).** Preprint.
  https://arxiv.org/abs/2410.16498
  → ids: arXiv:2410.16498

*How we differ:* this strand does one-year binary prediction (often on the small
IBM HR dataset). We use a large nationally-representative panel, calibrate a
*generative* transition model, run a validated multi-year microsimulation with
policy counterfactuals, and connect the model to labor-supply theory.

## Strand B — Tabular ML & interpretability

- **Grinsztajn, L., Oyallon, E., Varoquaux, G. (2022).** "Why do tree-based models
  still outperform deep learning on typical tabular data?" *NeurIPS 2022 Datasets
  & Benchmarks.* https://arxiv.org/abs/2207.08815
  → ids: arXiv:2207.08815 (NeurIPS proceedings; no journal DOI — use arXiv).
  Supports §5.1.
- **Lundberg, S. M., Lee, S.-I. (2017).** "A Unified Approach to Interpreting
  Model Predictions." *NeurIPS 2017*, 4766–4777. https://arxiv.org/abs/1705.07874
  → ids: arXiv:1705.07874. (If TreeSHAP is cited: Lundberg et al. 2020, *Nature
  Machine Intelligence* 2:56–67, DOI 10.1038/s42256-019-0138-9. **[verify]**)

## Strand C — ML in economics / prediction-policy / causal ML

- **Mullainathan, S., Spiess, J. (2017).** "Machine Learning: An Applied
  Econometric Approach." *Journal of Economic Perspectives* 31(2):87–106.
  https://www.aeaweb.org/articles?id=10.1257/jep.31.2.87
  → ids: DOI 10.1257/jep.31.2.87; ISSN 0895-3309
- **Kleinberg, J., Ludwig, J., Mullainathan, S., Obermeyer, Z. (2015).**
  "Prediction Policy Problems." *American Economic Review P&P* 105(5):491–495.
  https://www.aeaweb.org/articles?id=10.1257/aer.p20151023
  → ids: DOI 10.1257/aer.p20151023; ISSN 0002-8282
- **Athey, S., Imbens, G. W. (2019).** "Machine Learning Methods That Economists
  Should Know About." *Annual Review of Economics* 11:685–725.
  https://www.annualreviews.org/content/journals/10.1146/annurev-economics-080217-053433
  → ids: DOI 10.1146/annurev-economics-080217-053433; ISSN 1941-1383;
  arXiv:1903.10075
- **Wager, S., Athey, S. (2018).** "Estimation and Inference of Heterogeneous
  Treatment Effects using Random Forests." *JASA* 113(523):1228–1242.
  https://www.tandfonline.com/doi/full/10.1080/01621459.2017.1319839
  → ids: DOI 10.1080/01621459.2017.1319839; ISSN 0162-1459; arXiv:1510.04342
- **Chernozhukov, V., Chetverikov, D., Demirer, M., Duflo, E., Hansen, C., Newey,
  W., Robins, J. (2018).** "Double/Debiased Machine Learning for Treatment and
  Structural Parameters." *The Econometrics Journal* 21(1):C1–C68.
  https://academic.oup.com/ectj/article/21/1/C1/5056401
  → ids: DOI 10.1111/ectj.12097; ISSN 1368-423X

## Strand D — Relative pay, fairness, and quits (labor economics)

- **Card, D., Mas, A., Moretti, E., Saez, E. (2012).** "Inequality at Work: The
  Effect of Peer Salaries on Job Satisfaction." *American Economic Review*
  102(6):2981–3003. https://www.aeaweb.org/articles?id=10.1257/aer.102.6.2981
  → ids: DOI 10.1257/aer.102.6.2981; ISSN 0002-8282. Below-median earners report
  more job search; **rank matters more than level**. Antecedent of §5.4.
- **Dube, A., Giuliano, L., Leonard, J. (2019).** "Fairness and Frictions: The
  Impact of Unequal Raises on Quit Behavior." *American Economic Review*
  109(2):620–663. https://www.aeaweb.org/articles?id=10.1257/aer.20160232
  → ids: DOI 10.1257/aer.20160232; ISSN 0002-8282. Quits respond to *relative*
  raises; after peer effects, quits are not very sensitive to own wage
  (frictions). Resonates with our asymmetric shortfall result and modest own-wage
  elasticity.

*How we differ:* those are firm-level natural experiments on satisfaction/quits;
we bring the relative-wage / outside-option logic to a national panel, operationalize
the market wage with **external industry×year** data, and embed it in a predictive
microsimulation with distributional policy scenarios.

## Strand E — Dynamic microsimulation / agent-based labor models

- **Li, J., O'Donoghue, C.** "A survey of dynamic microsimulation models: uses,
  model structure and methodology." *International Journal of Microsimulation.*
  → ids: **[verify year/volume/DOI]** (likely 2013, IJM 6(2):3–55)
- **Neugart, M., Richiardi, M.** "Agent-based models of the labor market."
  https://ideas.repec.org/p/cca/wplabo/125.html
  → ids: **[verify — LABORatorio R. Revelli WP 125; also a handbook chapter]**

*How we differ:* classical dynamic microsimulations use reduced-form or
hand-specified transition equations; we *learn* the transition kernels with modern
ML, **calibrate** them for generative use (base-rate-accurate probabilities),
**back-test** the simulator against held-out years, and use it for
inflation/wage-indexation/minimum-wage counterfactuals.

---

## Draft prose (Section 2)

Our work sits at the intersection of five literatures. **(i) Turnover prediction
in ML** treats attrition as one-year binary classification, recently with neural
and peer/contagion effects (Teng et al. 2019; and Transformer variants); these
optimize predictive accuracy but do not produce multi-year trajectories,
counterfactual policy answers, or economic parameters. **(ii) Tabular ML**
explains why our gradient-boosted trees beat sequence models on this short panel
(Grinsztajn et al. 2022), and SHAP (Lundberg & Lee 2017) supplies our
interpretability. **(iii) ML in economics** frames the prediction-vs-estimation
distinction and prediction-for-policy (Mullainathan & Spiess 2017; Kleinberg et
al. 2015; Athey & Imbens 2019), and the causal-ML toolkit (Wager & Athey 2018;
Chernozhukov et al. 2018) marks the path from our descriptive elasticity toward
causal identification. **(iv) Relative pay and quits** in labor economics finds
that workers compare pay to peers and the market, that rank matters more than
level, and that quits track relative rather than absolute wages (Card, Mas,
Moretti & Saez 2012; Dube, Giuliano & Leonard 2019) — the theoretical anchor for
our "falling behind the market" result and our small own-wage elasticity. **(v)
Dynamic microsimulation** has long simulated labor-market policy with reduced-form
transition models; we contribute a *learned, calibrated, back-tested*
microsimulation. Our synthesis — learning calibrated transition kernels,
validating them generatively, and reading the separation model as an
extensive-margin labor-supply relation with an external relative-wage design — is,
to our knowledge, new.

## To verify before submission
- Author/year/venue/DOI for the **[verify]** items (Strand A benchmark survey;
  Strand E microsimulation survey and agent-based chapter).
- Whether we cite TreeSHAP (Lundberg et al. 2020, *Nature Machine Intelligence*,
  DOI 10.1038/s42256-019-0138-9).
- Confirm ISSN 1368-423X (online) vs 1368-4221 (print) for *Econometrics Journal*.
- Consider adding a Japan-specific JPSED / labor-mobility reference.
