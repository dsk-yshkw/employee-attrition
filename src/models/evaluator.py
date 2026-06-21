import pandas as pd
import numpy as np
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
)
import matplotlib.pyplot as plt
from sklearn.metrics import RocCurveDisplay, PrecisionRecallDisplay


class ModelEvaluator:
    def evaluate(self, y_true: pd.Series, y_prob: np.ndarray, threshold: float = 0.5) -> dict:
        y_pred = (y_prob >= threshold).astype(int)
        return {
            "auc_roc": roc_auc_score(y_true, y_prob),
            "auc_pr": average_precision_score(y_true, y_prob),
            "classification_report": classification_report(y_true, y_pred),
            "confusion_matrix": confusion_matrix(y_true, y_pred),
        }

    def plot_roc(self, y_true: pd.Series, y_prob: np.ndarray, ax=None) -> plt.Axes:
        if ax is None:
            _, ax = plt.subplots()
        RocCurveDisplay.from_predictions(y_true, y_prob, ax=ax)
        return ax

    def plot_pr(self, y_true: pd.Series, y_prob: np.ndarray, ax=None) -> plt.Axes:
        if ax is None:
            _, ax = plt.subplots()
        PrecisionRecallDisplay.from_predictions(y_true, y_prob, ax=ax)
        return ax

    def plot_feature_importance(
        self, feature_names: list, importances: np.ndarray, top_n: int = 20
    ) -> plt.Axes:
        idx = np.argsort(importances)[-top_n:]
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.barh([feature_names[i] for i in idx], importances[idx])
        ax.set_xlabel("Importance")
        ax.set_title(f"Top {top_n} Feature Importances")
        fig.tight_layout()
        return ax
