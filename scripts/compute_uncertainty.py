"""Uncertainty quantification for the paper (reproducibility item 4.10).

Computes:
1. Microsimulation dispersion: the backtest simulation repeated over 10 seeds;
   reports per-year mean +/- sd of the annual separation rate and end-year mean
   real income.
2. Paired bootstrap (1,000 resamples) 95% CIs for test-set ROC-AUCs of all six
   separation models (logistic, HistGBM, XGBoost, MLP, GRU, Transformer) and
   for the AUC gaps of XGBoost over each alternative.

Run:  python scripts/compute_uncertainty.py --data-dir "/path/to/JPSED/data"
"""

import argparse
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np

from src.data.loader import DataLoader
from src.data.panel_builder import PanelBuilder
from src.data.transitions import TransitionFrameBuilder
from src.data.macro import MacroData
from src.features.assembler import FeatureAssembler
from src.models.transitions import TransitionModels
from src.models.microsim import MicroSimulator, initial_state
from src.models.attrition import AttritionModel
from src.models.sequence import build_sequences, standardise, train_eval
from src.config import PKEY
from sklearn.metrics import roc_auc_score

TEST_YEAR = 2024
N_SEEDS = 10
N_BOOT = 1000


def sim_dispersion(pb, fa, tf, feats):
    tm = TransitionModels(feats).fit(tf[tf["year"] <= 2020])
    sim = MicroSimulator(tm, feats, MacroData())
    init = initial_state(pb, fa, 2021)
    rates, incomes = [], []
    for seed in range(1, N_SEEDS + 1):
        out = sim.simulate(init, 2021, 4, seed=seed, wage_noise_sd=30.0)
        rates.append(out["attrition_rate"].to_numpy())
        incomes.append(out.iloc[-1]["mean_real_income"])
    rates = np.stack(rates)                       # [seeds, years]
    years = list(out["year"])
    print("\n=== Simulation dispersion over %d seeds ===" % N_SEEDS)
    for j, y in enumerate(years):
        print(f"  {y}: separation mean={rates[:, j].mean():.4f}  sd={rates[:, j].std(ddof=1):.4f}")
    print(f"  end-year mean real income: mean={np.mean(incomes):.1f}  sd={np.std(incomes, ddof=1):.2f}")


def auc_bootstrap(tf, feats):
    # Sort so tree-model test rows align with sequence-sample order (pkey, year).
    tfs = tf.sort_values([PKEY, "year"]).reset_index(drop=True)
    tr, te = tfs["year"] < TEST_YEAR, tfs["year"] == TEST_YEAR
    ytr, yte = tfs.loc[tr, "separated"].to_numpy(), tfs.loc[te, "separated"].to_numpy()

    probs = {}
    for m in ("logistic", "histgbm", "xgboost"):
        mod = AttritionModel(model_type=m).fit(tfs.loc[tr, feats], ytr)
        probs[m] = mod.predict_proba(tfs.loc[te, feats])

    X, mask, y, yrs = build_sequences(tfs, feats, max_len=8)
    str_, ste = yrs < TEST_YEAR, yrs == TEST_YEAR
    assert ste.sum() == te.sum() and np.array_equal(y[ste], yte.astype(np.float32)), \
        "sequence/test alignment failed"
    Xtr, Xte = standardise(X[str_], X[ste], mask[str_], mask[ste])
    for kind in ("mlp", "gru", "transformer"):
        _, p = train_eval(kind, Xtr, mask[str_], y[str_], Xte, mask[ste], y[ste],
                          max_len=8, epochs=8, seed=0, return_probs=True)
        probs[kind] = p

    names = list(probs)
    n = len(yte)
    rng = np.random.default_rng(0)
    boot = {k: np.empty(N_BOOT) for k in names}
    for b in range(N_BOOT):
        idx = rng.integers(0, n, n)
        yb = yte[idx]
        if yb.sum() in (0, n):
            idx = rng.integers(0, n, n); yb = yte[idx]
        for k in names:
            boot[k][b] = roc_auc_score(yb, probs[k][idx])

    print("\n=== Test-set ROC-AUC, paired bootstrap (%d resamples) ===" % N_BOOT)
    for k in names:
        lo, hi = np.percentile(boot[k], [2.5, 97.5])
        print(f"  {k:12s} AUC={roc_auc_score(yte, probs[k]):.3f}  95% CI [{lo:.3f}, {hi:.3f}]")
    print("  --- AUC gaps (XGBoost minus alternative) ---")
    for k in names:
        if k == "xgboost":
            continue
        gap = boot["xgboost"] - boot[k]
        lo, hi = np.percentile(gap, [2.5, 97.5])
        sig = "excludes 0" if lo > 0 or hi < 0 else "includes 0"
        print(f"  xgboost - {k:12s} mean={gap.mean():+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]  ({sig})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    args = ap.parse_args()
    pb = PanelBuilder(DataLoader(args.data_dir))
    fa = FeatureAssembler()
    tf, feats = TransitionFrameBuilder(pb, fa).build()
    sim_dispersion(pb, fa, tf, feats)
    auc_bootstrap(tf, feats)


if __name__ == "__main__":
    main()
