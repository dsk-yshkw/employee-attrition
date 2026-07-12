"""Generate paper-quality figures (PDF + PNG) into ``figures/``.

Colours use the Okabe-Ito colourblind-safe palette (the scientific-publication
standard). Labels are English so figures render without a CJK font. Figures:

1. fig_backtest      -- simulated vs actual attrition (model validation)
2. fig_scenarios     -- attrition & real income under inflation / COLA scenarios
3. fig_contract      -- inflation attrition response by contract type (the
                        distributional headline), as a dumbbell chart
4. fig_shap_depend   -- SHAP dependence (real income, tenure)
5. fig_importance    -- SHAP global importance
6. fig_elasticity    -- retention wage-elasticity by contract type

Run:  python scripts/make_figures.py --data-dir "/path/to/JPSED/data"
      python scripts/make_figures.py --synthetic
"""

import argparse
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt

from src.data.loader import DataLoader
from src.data.panel_builder import PanelBuilder
from src.data.transitions import TransitionFrameBuilder
from src.data.macro import MacroData
from src.models.transitions import TransitionModels
from src.models.microsim import MicroSimulator, initial_state, inflation_scenario
from src.models.attrition import AttritionModel
from src.models.elasticity import elasticity_by_group
from src.models.interpret import fit_xgb_for_shap, shap_analysis, dependence
from src.features.assembler import FeatureAssembler
from src.features.relative_wage import RelativeWageBuilder
from src.config import TARGET_SEPARATION

# Okabe-Ito palette
OI = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
      "yellow": "#F0E442", "blue": "#0072B2", "vermillion": "#D55E00", "purple": "#CC79A7"}
CONTRACT = {1: "Regular", 2: "Part-time", 3: "Dispatch", 4: "Contract"}

mpl.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
    "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5,
    "lines.linewidth": 1.9, "legend.frameon": False, "font.family": "sans-serif",
})

FIGDIR = "figures"


def save(fig, name):
    os.makedirs(FIGDIR, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIGDIR, f"{name}.{ext}"))
    plt.close(fig)
    print("wrote", os.path.join(FIGDIR, name) + ".{pdf,png}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=None)
    ap.add_argument("--synthetic", action="store_true")
    args = ap.parse_args()
    synthetic = args.synthetic or args.data_dir is None
    data_dir = "data/synthetic" if synthetic else args.data_dir

    pb = PanelBuilder(DataLoader(data_dir, synthetic=synthetic))
    fa = FeatureAssembler()
    mac = MacroData()
    tf, feats = TransitionFrameBuilder(pb, fa).build()
    panel = pb.add_targets(pb.build())
    sub = panel[pb.employee_mask(panel)]
    actual = sub.groupby("year")[TARGET_SEPARATION].mean()

    yrs = sorted(tf["year"].unique())
    init_year = max(yrs[0] + 1, yrs[-1] - 3)
    n_steps = yrs[-1] - init_year + 1
    tm = TransitionModels(feats).fit(tf[tf["year"] < init_year])
    sim = MicroSimulator(tm, feats, mac)
    init = initial_state(pb, fa, init_year)

    def run(**kw):
        return sim.simulate(init, init_year, n_steps, seed=1, wage_noise_sd=30.0, **kw)

    base = run()
    yrng = range(init_year, yrs[-1] + 1)
    hi2 = run(cpi_override=inflation_scenario(mac, 2.0, yrng))
    hi4 = run(cpi_override=inflation_scenario(mac, 4.0, yrng))
    hi4c = run(cpi_override=inflation_scenario(mac, 4.0, yrng), cola_passthrough=1.0)

    # ---- 1. backtest -----------------------------------------------------
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.plot(base["year"], base["attrition_rate"], "-o", color=OI["blue"], label="Simulated")
    ax.plot(base["year"], base["year"].map(actual), "--s", color=OI["vermillion"], label="Actual")
    ax.set_xlabel("Year"); ax.set_ylabel("Annual separation rate")
    ax.set_ylim(0, max(0.12, base["attrition_rate"].max() * 1.3))
    ax.set_xticks(list(base["year"])); ax.legend(loc="lower left")
    ax.set_title("Microsimulation backtest")
    save(fig, "fig_backtest")

    # ---- 2. scenarios ----------------------------------------------------
    scn = [("Baseline", base, OI["black"], "-o"), ("+2pp inflation", hi2, OI["sky"], "-^"),
           ("+4pp inflation", hi4, OI["vermillion"], "-s"), ("+4pp + full COLA", hi4c, OI["green"], "-D")]
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    for name, d, c, m in scn:
        ax[0].plot(d["year"], d["attrition_rate"], m, color=c, label=name, markersize=5)
        ax[1].plot(d["year"], d["mean_real_income"], m, color=c, label=name, markersize=5)
    ax[0].set_ylabel("Annual separation rate"); ax[0].set_xlabel("Year")
    ax[0].set_title("(a) Attrition by scenario"); ax[0].set_ylim(0, None)
    ax[1].set_ylabel("Mean real income (man-yen, 2020)"); ax[1].set_xlabel("Year")
    ax[1].set_title("(b) Real income by scenario")
    for a in ax:
        a.set_xticks(list(base["year"]))
    ax[1].legend(loc="lower left", fontsize=8)
    save(fig, "fig_scenarios")

    # ---- 3. contract-type response (dumbbell) ---------------------------
    bg = run(group_col="contract_type")
    bg4 = run(cpi_override=inflation_scenario(mac, 4.0, yrng), group_col="contract_type")
    rows = []
    for k, lab in CONTRACT.items():
        col = f"attrition_contract_type={k}"
        if col in bg and col in bg4:
            rows.append((lab, bg.iloc[-1][col], bg4.iloc[-1][col]))
    rows.sort(key=lambda r: r[2])
    fig, ax = plt.subplots(figsize=(6, 3.6))
    for i, (lab, b, h) in enumerate(rows):
        ax.plot([b, h], [i, i], color="#bbbbbb", lw=2, zorder=1)
        ax.scatter(b, i, color=OI["blue"], s=55, zorder=2, label="Baseline" if i == 0 else None)
        ax.scatter(h, i, color=OI["vermillion"], s=55, zorder=2, label="+4pp inflation" if i == 0 else None)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlabel("Simulated attrition rate (final year)")
    ax.set_title("Inflation attrition response by contract type"); ax.legend(loc="lower right")
    save(fig, "fig_contract")

    # ---- 4/5. SHAP -------------------------------------------------------
    TESTY = yrs[-1]
    xgb = fit_xgb_for_shap(tf[tf["year"] < TESTY][feats], tf[tf["year"] < TESTY]["separated"])
    sv, imp, expl, Xs = shap_analysis(xgb, tf[tf["year"] == TESTY][feats], max_samples=4000, seed=0)

    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    for a, feat, xlab, xlim in [(ax[0], "real_annual_income", "Real annual income (man-yen)", (0, 1200)),
                                (ax[1], "tenure_years", "Tenure (years)", (0, 40))]:
        d = dependence(sv, Xs, feat)
        a.scatter(d["value"], d["shap"], s=6, alpha=0.15, color=OI["green"])
        dd = d.dropna(); dd = dd[(dd["value"] >= xlim[0]) & (dd["value"] <= xlim[1])]
        bins = pd.cut(dd["value"], 12)
        gb = dd.groupby(bins, observed=True)["shap"].mean()
        centers = [iv.mid for iv in gb.index]
        a.plot(centers, gb.values, "-", color=OI["blue"], lw=2)
        a.axhline(0, color="k", lw=0.6); a.set_xlim(*xlim)
        a.set_xlabel(xlab); a.set_ylabel("SHAP (log-odds of separation)")
    ax[0].set_title("(a) Real income -> separation"); ax[1].set_title("(b) Tenure -> separation")
    save(fig, "fig_shap_depend")

    fig, ax = plt.subplots(figsize=(6, 4.2))
    imp.head(12)[::-1].plot(kind="barh", ax=ax, color=OI["blue"])
    ax.set_xlabel("mean |SHAP| (log-odds)"); ax.set_title("SHAP global feature importance")
    save(fig, "fig_importance")

    # ---- 6. elasticity by contract --------------------------------------
    logit = AttritionModel(model_type="logistic", class_weight=None).fit(
        tf[tf["year"] < TESTY][feats], tf[tf["year"] < TESTY]["separated"])
    te = tf[tf["year"] == TESTY].reset_index(drop=True)
    g = elasticity_by_group(lambda X: logit.predict_proba(X),
                            te[feats], te["contract_type"].fillna(-1).astype(int), 0.10)
    g = g[g["group"].isin(CONTRACT)].copy()
    g["label"] = g["group"].map(CONTRACT)
    g = g.sort_values("elasticity")
    fig, ax = plt.subplots(figsize=(6, 3.4))
    ax.barh(g["label"], g["elasticity"], color=OI["purple"])
    ax.set_xlabel("Wage elasticity of job retention")
    ax.set_title("Extensive-margin labour-supply elasticity by contract type")
    save(fig, "fig_elasticity")

    # ---- 7. relative wage growth -> separation --------------------------
    rw = RelativeWageBuilder(mac).build(tf)
    rd = tf.assign(short=-rw["relative_wage_growth"], isind=rw["market_is_industry"])
    rd = rd[rd["isind"] == 1].dropna(subset=["short"])
    if len(rd) > 1000:
        rd["q"] = pd.qcut(rd["short"], 5, labels=["lead\n(own>mkt)", "Q2", "Q3", "Q4",
                                                  "lag most\n(own<<mkt)"])
        g = rd.groupby("q", observed=True)["separated"].mean()
        fig, ax = plt.subplots(figsize=(6, 3.6))
        ax.bar(range(len(g)), g.values, color=OI["vermillion"])
        ax.set_xticks(range(len(g))); ax.set_xticklabels(g.index, fontsize=8)
        ax.set_ylabel("Separation rate")
        ax.set_xlabel("Own wage growth relative to industry market (quintile)")
        ax.set_title("Falling behind the market wage -> higher attrition")
        save(fig, "fig_relwage")

    print("all figures written to", FIGDIR + "/")


if __name__ == "__main__":
    main()
