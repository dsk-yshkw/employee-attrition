"""Compute the paper's Tables 1-5 from real data and write Markdown + LaTeX.

Outputs to ``paper/tables/``:
  table1_data, table2_prediction, table3_transition, table4_scenarios,
  table5_relwage   (each as .md and .tex), plus a combined tables.md.

Run:  python scripts/make_tables.py --data-dir "/path/to/JPSED/data"
      python scripts/make_tables.py --synthetic
"""

import argparse
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd

from src.data.loader import DataLoader
from src.data.panel_builder import PanelBuilder
from src.data.transitions import TransitionFrameBuilder
from src.data.macro import MacroData
from src.features.assembler import FeatureAssembler
from src.features.relative_wage import RelativeWageBuilder
from src.models.attrition import AttritionModel
from src.models.evaluator import ModelEvaluator
from src.models.transitions import TransitionModels
from src.models.microsim import MicroSimulator, initial_state, inflation_scenario
from src.config import TARGET_SEPARATION, TARGET_INTENTION

OUT = "paper/tables"
CONTRACT = {1: "Regular", 2: "Part-time", 3: "Dispatch", 4: "Contract"}


def write(df, name, caption, index=False):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + ".md"), "w") as f:
        f.write(f"**{caption}**\n\n")
        f.write(df.to_markdown(index=index))
        f.write("\n")
    with open(os.path.join(OUT, name + ".tex"), "w") as f:
        f.write(df.to_latex(index=index, caption=caption, label="tab:" + name,
                            float_format="%.3f"))
    print("wrote", name)
    return df


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
    ev = ModelEvaluator()

    panel = pb.add_targets(pb.build())
    sub = panel[pb.employee_mask(panel)]
    tf, feats = TransitionFrameBuilder(pb, fa).build()
    yrs = sorted(tf["year"].unique())

    # ---- Table 1: data ---------------------------------------------------
    t1 = sub.groupby("year").agg(
        employees=("pkey", "size"),
        separation_rate=(TARGET_SEPARATION, "mean"),
        intention_rate=(TARGET_INTENTION, "mean"),
    ).reset_index()
    t1["separation_rate"] = t1["separation_rate"].round(3).map(
        lambda v: "—" if pd.isna(v) else f"{v:.3f}")   # 2025 has no following wave
    t1["intention_rate"] = t1["intention_rate"].round(3)
    t1.columns = ["Year", "Employees", "Separation rate", "Intention rate"]
    write(t1, "table1_data", "Table 1: Sample size and attrition base rates by wave (employees).")

    # ---- Table 2: prediction benchmark -----------------------------------
    rows = []
    for target, name, ty in [(TARGET_SEPARATION, "Separation", 2024),
                             (TARGET_INTENTION, "Intention", 2025)]:
        fr = pb.build_modeling_frame(target)
        X = fa.build(fr); y = fr[target]
        tr = fr["year"] < ty; te = fr["year"] == ty
        for m in ["logistic", "histgbm", "xgboost"]:
            try:
                mod = AttritionModel(model_type=m).fit(X[tr], y[tr])
                met = ev.evaluate(y[te], mod.predict_proba(X[te]))
                rows.append({"Target": name, "Model": m,
                             "Base rate": round(float(y[te].mean()), 3),
                             "ROC-AUC": round(met["auc_roc"], 3),
                             "PR-AUC": round(met["auc_pr"], 3)})
            except Exception as e:
                print("skip", name, m, e)
    write(pd.DataFrame(rows), "table2_prediction",
          "Table 2: Next-year attrition prediction, time-based split (test = latest usable wave).")

    # ---- Table 3: transition sub-models ----------------------------------
    split = yrs[-1] - 1
    tm = TransitionModels(feats).fit(tf[tf["year"] < split])
    val = tm.validate(tf[tf["year"] == split])
    t3 = pd.DataFrame([
        ("Separation", "ROC-AUC", val.get("separation_auc")),
        ("Separation", "pred/obs rate", f"{val.get('separation_pred_rate'):.3f} / {val.get('separation_obs_rate'):.3f}"),
        ("Re-employment", "ROC-AUC", val.get("reemployment_auc")),
        ("Wage (stayers)", "R^2", val.get("wage_stay_r2")),
        ("Wage (stayers)", "MAE (man-yen)", val.get("wage_stay_mae")),
        ("Wage (movers)", "R^2", val.get("wage_move_r2")),
        ("Wage (movers)", "MAE (man-yen)", val.get("wage_move_mae")),
    ], columns=["Sub-model", "Metric", "Value"])
    t3["Value"] = t3["Value"].apply(lambda v: round(v, 3) if isinstance(v, float) else v)
    write(t3, "table3_transition", f"Table 3: Transition sub-model validation (test = {split}).")

    # ---- Table 4: scenarios ----------------------------------------------
    init_year = max(yrs[0] + 1, yrs[-1] - 3)
    n_steps = yrs[-1] - init_year + 1
    tms = TransitionModels(feats).fit(tf[tf["year"] < init_year])
    sim = MicroSimulator(tms, feats, mac)
    init = initial_state(pb, fa, init_year)
    yrng = range(init_year, yrs[-1] + 1)

    def run(**kw):
        return sim.simulate(init, init_year, n_steps, seed=1, wage_noise_sd=30.0, **kw)

    scn = [("Baseline", run()),
           ("+2pp inflation", run(cpi_override=inflation_scenario(mac, 2.0, yrng))),
           ("+4pp inflation", run(cpi_override=inflation_scenario(mac, 4.0, yrng))),
           ("+4pp + full COLA", run(cpi_override=inflation_scenario(mac, 4.0, yrng), cola_passthrough=1.0)),
           ("Min wage (200)", run(min_wage_nominal=200.0))]
    t4 = pd.DataFrame([{
        "Scenario": n,
        "End attrition": round(d.iloc[-1]["attrition_rate"], 3),
        "Cumulative attrition": round(d["attrition_rate"].sum(), 3),
        "End real income": round(d.iloc[-1]["mean_real_income"], 1),
    } for n, d in scn])
    write(t4, "table4_scenarios",
          f"Table 4: Microsimulation scenarios (cohort {init_year}, {n_steps} years).")

    # ---- Table 5: relative-wage regression -------------------------------
    import statsmodels.formula.api as smf
    rw = RelativeWageBuilder(mac).build(tf)
    reg = tf[["separated", "year", "industry", "pkey"]].copy()
    reg["own"] = rw["own_wage_growth"].values
    reg["market"] = rw["market_wage_growth"].values
    reg["relative"] = rw["relative_wage_growth"].values
    reg["shortfall"] = np.clip(-reg["relative"], 0, None)   # how far below market
    reg = reg.dropna(subset=["own", "market", "separated"])
    reg["C_year"] = reg["year"].astype("category")

    specs = {
        "(1) own": "separated ~ own + C_year",
        "(2) own+market": "separated ~ own + market + C_year",
        "(3) relative": "separated ~ relative + C_year",
        "(4) shortfall": "separated ~ shortfall + C_year",
    }
    terms = ["own", "market", "relative", "shortfall"]
    tbl = {}
    for label, formula in specs.items():
        res = smf.ols(formula, data=reg).fit(
            cov_type="cluster", cov_kwds={"groups": reg["pkey"]})
        col = {}
        for term in terms:
            if term in res.params.index:
                col[term] = f"{res.params[term]:.3f} ({res.bse[term]:.3f})"
            else:
                col[term] = ""
        col["Year FE"] = "Yes"
        col["N"] = f"{int(res.nobs):,}"
        col["R^2"] = f"{res.rsquared:.3f}"
        tbl[label] = col
    t5 = pd.DataFrame(tbl).reindex(terms + ["Year FE", "N", "R^2"])
    t5.index = ["Own wage growth", "Market wage growth", "Relative (own-market)",
                "Shortfall (market-own)+", "Year FE", "N", "R^2"]
    t5 = t5.reset_index().rename(columns={"index": "Term"})
    write(t5, "table5_relwage",
          "Table 5: Linear probability models of separation on wage growth relative "
          "to the industry market (cluster-robust SE by person in parentheses).", index=False)

    # combined
    with open(os.path.join(OUT, "tables.md"), "w") as f:
        for name in ["table1_data", "table2_prediction", "table3_transition",
                     "table4_scenarios", "table5_relwage"]:
            f.write(open(os.path.join(OUT, name + ".md")).read() + "\n\n")
    print("wrote combined paper/tables/tables.md")


if __name__ == "__main__":
    main()
