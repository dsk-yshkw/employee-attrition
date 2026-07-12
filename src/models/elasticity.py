"""Extensive-margin labour-supply elasticity from the separation model.

We treat the fitted separation model as the choice probability of a random-utility
discrete-choice model of job continuation: a worker stays if the utility of
staying (increasing in the wage) exceeds the outside option. The *retention*
probability is ``P(stay) = 1 - P(separate)``. The wage elasticity of retention is
an extensive-margin labour-supply response.

We estimate it by counterfactual perturbation: raise every worker's real wage by
a small percentage, recompute retention, and measure the response — overall and
by subgroup (the heterogeneity is the economically interesting part).

``p_separate`` is any callable ``X -> array`` of separation probabilities
(e.g. a calibrated ``TransitionModels.p_separate``).
"""

import numpy as np
import pandas as pd

# Wage columns that move together when the real wage shifts.
_WAGE_COLS = ("real_annual_income", "annual_income")


def _bump(X: pd.DataFrame, pct: float, wage_cols=_WAGE_COLS) -> pd.DataFrame:
    Xp = X.copy()
    for c in wage_cols:
        if c in Xp.columns:
            Xp[c] = pd.to_numeric(Xp[c], errors="coerce") * (1 + pct)
    return Xp


def retention_elasticity(p_separate, X: pd.DataFrame, pct: float = 0.10,
                         weights=None, wage_cols=_WAGE_COLS) -> dict:
    """Wage elasticity of job retention (extensive-margin labour supply).

    Returns both the elasticity ``(%Δ P(stay)) / (%Δ wage)`` and the
    semi-elasticity ``ΔP(stay) / Δln(wage)`` (percentage-point change in
    retention per log-point of wage), averaged over the population.
    """
    w = np.ones(len(X)) if weights is None else np.asarray(weights, dtype=float)
    w = w / w.sum()

    stay0 = 1 - np.asarray(p_separate(X))
    stay1 = 1 - np.asarray(p_separate(_bump(X, pct, wage_cols)))

    p0 = float(np.sum(w * stay0))
    p1 = float(np.sum(w * stay1))
    dP = float(np.sum(w * (stay1 - stay0)))
    return {
        "pct_wage_change": pct,
        "retention_base": p0,
        "retention_bumped": p1,
        "d_retention": dP,
        "semi_elasticity": dP / np.log(1 + pct),          # ΔP(stay) per log-wage
        "elasticity": (p1 - p0) / p0 / pct,               # %ΔP(stay) / %Δwage
        "separation_semi_elasticity": -dP / np.log(1 + pct),
    }


def elasticity_by_group(p_separate, X: pd.DataFrame, group, pct: float = 0.10,
                        weights=None) -> pd.DataFrame:
    """Retention elasticity computed within each level of ``group``."""
    X = X.reset_index(drop=True)
    g = pd.Series(np.asarray(group)).reset_index(drop=True)
    w = None if weights is None else np.asarray(weights, dtype=float)
    rows = []
    for key in pd.unique(g):
        sel = np.where(g.values == key)[0]
        sub_w = None if w is None else w[sel]
        res = retention_elasticity(p_separate, X.iloc[sel], pct=pct, weights=sub_w)
        res["group"] = key
        res["n"] = int(len(sel))
        rows.append(res)
    cols = ["group", "n", "retention_base", "d_retention", "semi_elasticity", "elasticity"]
    return pd.DataFrame(rows)[cols].sort_values("group").reset_index(drop=True)
