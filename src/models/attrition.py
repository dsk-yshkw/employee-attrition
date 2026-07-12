"""Attrition probability model.

Primary gradient-boosting backend is scikit-learn's
``HistGradientBoostingClassifier`` (no native-library dependency, handles NaNs
and categoricals directly). ``logistic`` and ``xgboost`` backends are also
available; xgboost is imported lazily so the package is optional.
"""

import numpy as np
import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier

from src.config import CATEGORICAL_FEATURES


def _to_category(X, cat_cols):
    """Cast the given columns to pandas 'category' dtype for HistGBM."""
    X = X.copy()
    for c in cat_cols:
        if c in X.columns:
            X[c] = X[c].astype("category")
    return X


class AttritionModel:
    SUPPORTED_MODELS = ("histgbm", "logistic", "xgboost")

    def __init__(self, model_type: str = "histgbm", random_state: int = 42, **kwargs):
        if model_type not in self.SUPPORTED_MODELS:
            raise ValueError(f"model_type must be one of {self.SUPPORTED_MODELS}")
        self.model_type = model_type
        self.random_state = random_state
        self.kwargs = kwargs
        self.pipeline = None
        self.feature_names_ = None

    # -- training / inference ----------------------------------------------
    def fit(self, X: pd.DataFrame, y) -> "AttritionModel":
        self.feature_names_ = list(X.columns)
        self.pipeline = self._build_pipeline(X)
        self.pipeline.fit(X, y)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.pipeline.predict_proba(X[self.feature_names_])[:, 1]

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.pipeline.predict(X[self.feature_names_])

    # -- persistence --------------------------------------------------------
    def save(self, path: str) -> None:
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: str) -> "AttritionModel":
        return joblib.load(path)

    # -- feature importance -------------------------------------------------
    def feature_importance(self, X, y):
        """Permutation importance on the held-in data (backend-agnostic)."""
        from sklearn.inspection import permutation_importance

        result = permutation_importance(
            self.pipeline, X[self.feature_names_], y,
            n_repeats=5, random_state=self.random_state, scoring="roc_auc",
        )
        return pd.Series(result.importances_mean, index=self.feature_names_).sort_values()

    # -- pipeline construction ---------------------------------------------
    def _categorical_cols(self, X: pd.DataFrame) -> list:
        return [c for c in CATEGORICAL_FEATURES if c in X.columns]

    def _build_pipeline(self, X: pd.DataFrame) -> Pipeline:
        cat_cols = self._categorical_cols(X)
        num_cols = [c for c in X.columns if c not in cat_cols]

        if self.model_type == "logistic":
            pre = ColumnTransformer(
                [
                    ("num", Pipeline([
                        ("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]), num_cols),
                    ("cat", Pipeline([
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("oh", OneHotEncoder(handle_unknown="ignore")),
                    ]), cat_cols),
                ]
            )
            kwargs = dict(self.kwargs)
            class_weight = kwargs.pop("class_weight", "balanced")
            clf = LogisticRegression(
                max_iter=2000, class_weight=class_weight,
                random_state=self.random_state, **kwargs,
            )
            return Pipeline([("pre", pre), ("clf", clf)])

        if self.model_type == "xgboost":
            from xgboost import XGBClassifier

            # xgboost needs numeric input; one-hot the categoricals.
            pre = ColumnTransformer(
                [
                    ("num", "passthrough", num_cols),
                    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
                ]
            )
            clf = XGBClassifier(
                n_estimators=400, learning_rate=0.05, max_depth=5,
                subsample=0.8, colsample_bytree=0.8, eval_metric="logloss",
                random_state=self.random_state, **self.kwargs,
            )
            return Pipeline([("pre", pre), ("clf", clf)])

        # histgbm (default): native NaN + categorical support.
        cast = FunctionTransformer(
            _to_category, kw_args={"cat_cols": cat_cols}, feature_names_out="one-to-one",
        )
        clf = HistGradientBoostingClassifier(
            learning_rate=0.05, max_iter=400, max_depth=None,
            l2_regularization=1.0, categorical_features="from_dtype",
            class_weight="balanced", random_state=self.random_state, **self.kwargs,
        )
        return Pipeline([("cast", cast), ("clf", clf)])
