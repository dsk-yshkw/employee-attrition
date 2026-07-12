"""Transition sub-models for the multi-year attrition microsimulation.

Four models describe how a worker moves from one year to the next:

- ``separation``  P(separated | state)          -- among employees
- ``reemployment`` P(employed next | separated)  -- among separators
- ``wage_stay``   E[nominal income next | stayed] -- regression
- ``wage_move``   E[nominal income next | moved]  -- regression (new-job wage)

Each is a scikit-learn HistGradientBoosting model (native NaN + categorical
support). The simulator (see the microsimulation module) samples from these to
propagate a synthetic population forward year by year.

The classifiers use **no class re-weighting**: the simulation needs calibrated
probabilities that reproduce the true base rates (e.g. ~8% separation), whereas
the AUC-oriented :class:`~src.models.attrition.AttritionModel` uses balanced
weights for ranking. Wage models predict **nominal** income so the simulator can
deflate by a scenario CPI path.
"""

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
)
from sklearn.metrics import roc_auc_score, r2_score, mean_absolute_error

from src.config import CATEGORICAL_FEATURES


def _to_category(X, cat_cols):
    X = X.copy()
    for c in cat_cols:
        if c in X.columns:
            X[c] = X[c].astype("category")
    return X


def _make(estimator, feature_cols, random_state=42):
    cat = [c for c in CATEGORICAL_FEATURES if c in feature_cols]
    cast = FunctionTransformer(_to_category, kw_args={"cat_cols": cat},
                               feature_names_out="one-to-one")
    return Pipeline([("cast", cast), ("est", estimator)])


class TransitionModels:
    def __init__(self, feature_cols, random_state=42):
        self.feature_cols = list(feature_cols)
        self.random_state = random_state
        self.models = {}

    # -- fitting ------------------------------------------------------------
    def _clf(self):
        # No class_weight: keep probabilities calibrated to the true base rate,
        # which the simulation relies on.
        return _make(HistGradientBoostingClassifier(
            learning_rate=0.05, max_iter=300, l2_regularization=1.0,
            categorical_features="from_dtype",
            random_state=self.random_state), self.feature_cols)

    def _reg(self):
        return _make(HistGradientBoostingRegressor(
            learning_rate=0.05, max_iter=300, l2_regularization=1.0,
            categorical_features="from_dtype", loss="absolute_error",
            random_state=self.random_state), self.feature_cols)

    def fit(self, frame: pd.DataFrame) -> "TransitionModels":
        X = frame[self.feature_cols]

        # 1) separation among all employees
        self.models["separation"] = self._clf().fit(X, frame["separated"])

        # 2) re-employment among separators
        sep = frame["separated"] == 1
        self.models["reemployment"] = self._clf().fit(
            X[sep], frame.loc[sep, "employed_next"])

        # 3) nominal wage of stayers (not separated & employed next, income obs.)
        stay = (frame["separated"] == 0) & (frame["employed_next"] == 1) \
            & frame["income_next"].notna()
        self.models["wage_stay"] = self._reg().fit(
            X[stay], frame.loc[stay, "income_next"])

        # 4) nominal wage of movers who re-employed
        move = (frame["separated"] == 1) & (frame["employed_next"] == 1) \
            & frame["income_next"].notna()
        self.models["wage_move"] = self._reg().fit(
            X[move], frame.loc[move, "income_next"])
        return self

    # -- prediction ---------------------------------------------------------
    def p_separate(self, X):
        return self.models["separation"].predict_proba(X[self.feature_cols])[:, 1]

    def p_reemploy(self, X):
        return self.models["reemployment"].predict_proba(X[self.feature_cols])[:, 1]

    def wage_stay(self, X):
        return self.models["wage_stay"].predict(X[self.feature_cols])

    def wage_move(self, X):
        return self.models["wage_move"].predict(X[self.feature_cols])

    # -- validation ---------------------------------------------------------
    def validate(self, frame: pd.DataFrame) -> dict:
        X = frame[self.feature_cols]
        out = {}
        y = frame["separated"]
        out["separation_auc"] = roc_auc_score(y, self.p_separate(X))
        sep = frame["separated"] == 1
        if sep.sum() > 0 and frame.loc[sep, "employed_next"].nunique() > 1:
            out["reemployment_auc"] = roc_auc_score(
                frame.loc[sep, "employed_next"], self.p_reemploy(X[sep]))
        # separation calibration: mean predicted vs observed base rate
        out["separation_pred_rate"] = float(self.p_separate(X).mean())
        out["separation_obs_rate"] = float(y.mean())
        stay = (frame["separated"] == 0) & (frame["employed_next"] == 1) \
            & frame["income_next"].notna()
        out["wage_stay_r2"] = r2_score(frame.loc[stay, "income_next"],
                                       self.wage_stay(X[stay]))
        out["wage_stay_mae"] = mean_absolute_error(
            frame.loc[stay, "income_next"], self.wage_stay(X[stay]))
        move = (frame["separated"] == 1) & (frame["employed_next"] == 1) \
            & frame["income_next"].notna()
        out["wage_move_r2"] = r2_score(frame.loc[move, "income_next"],
                                       self.wage_move(X[move]))
        out["wage_move_mae"] = mean_absolute_error(
            frame.loc[move, "income_next"], self.wage_move(X[move]))
        return out
