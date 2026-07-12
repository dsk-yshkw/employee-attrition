"""Feature-importance analysis: TreeSHAP (primary) + permutation (cross-check).

SHAP is computed on an XGBoost model fitted directly on the 23 canonical features
with native categorical support (``enable_categorical=True``), so SHAP values keep
clean per-feature names (no one-hot expansion of industry/occupation). This gives
signed, non-linear attributions and dependence relationships — in particular the
real-wage -> separation dependence that visualises the labour-supply story.

Caveat: with correlated predictors (tenure, age, income) SHAP splits credit among
them, so read tenure/age/income as a group rather than in isolation.
"""

import numpy as np
import pandas as pd

from src.config import CATEGORICAL_FEATURES


def _cast_categoricals(X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()
    for c in CATEGORICAL_FEATURES:
        if c in X.columns:
            X[c] = X[c].astype("category")
    return X


def fit_xgb_for_shap(X: pd.DataFrame, y, random_state: int = 42):
    """Fit an XGBoost classifier with native categoricals for TreeSHAP."""
    from xgboost import XGBClassifier

    Xc = _cast_categoricals(X)
    model = XGBClassifier(
        n_estimators=400, learning_rate=0.05, max_depth=5,
        subsample=0.8, colsample_bytree=0.8, eval_metric="logloss",
        tree_method="hist", enable_categorical=True,
        random_state=random_state,
    )
    model.fit(Xc, y)
    return model


def shap_analysis(model, X: pd.DataFrame, max_samples: int = 5000, seed: int = 0):
    """Return (shap_values_df, global_importance, explainer, X_sample).

    ``shap_values_df`` holds per-instance SHAP values (log-odds units) aligned to
    ``X_sample``; ``global_importance`` is mean(|SHAP|) per feature (descending).
    """
    import shap

    Xc = _cast_categoricals(X)
    if len(Xc) > max_samples:
        Xc = Xc.sample(max_samples, random_state=seed)
    explainer = shap.TreeExplainer(model)
    sv = explainer.shap_values(Xc)
    sv_df = pd.DataFrame(sv, columns=list(Xc.columns), index=Xc.index)
    importance = sv_df.abs().mean().sort_values(ascending=False)
    return sv_df, importance, explainer, Xc


def dependence(sv_df: pd.DataFrame, X_sample: pd.DataFrame, feature: str) -> pd.DataFrame:
    """Feature value vs its SHAP contribution (for a dependence scatter/plot)."""
    return pd.DataFrame({
        "value": pd.to_numeric(X_sample[feature], errors="coerce").to_numpy(),
        "shap": sv_df[feature].to_numpy(),
    })


def permutation_importance_auc(model, X: pd.DataFrame, y, n_repeats: int = 5,
                               seed: int = 42) -> pd.Series:
    """Permutation importance (AUC drop) as a cross-check. Model must expose the
    same categorical handling as ``X`` (use the SHAP xgboost model)."""
    from sklearn.inspection import permutation_importance
    from sklearn.metrics import roc_auc_score

    Xc = _cast_categoricals(X)

    class _Wrap:
        def fit(self, *a, **k):
            return self

        def predict_proba(self, Xin):
            return model.predict_proba(Xin)

    def scorer(est, Xin, yin):
        return roc_auc_score(yin, model.predict_proba(Xin)[:, 1])

    res = permutation_importance(_Wrap(), Xc, y, scoring=scorer,
                                 n_repeats=n_repeats, random_state=seed)
    return pd.Series(res.importances_mean, index=list(Xc.columns)).sort_values()
