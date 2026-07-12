"""End-to-end attrition experiment: panel -> features -> time-split -> evaluate.

Run directly to reproduce the headline results:

    python -m src.pipeline --data-dir "/path/to/data"          # real JPSED data
    python -m src.pipeline --synthetic                          # bundled synthetic data
"""

import argparse
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.data.loader import DataLoader
from src.data.panel_builder import PanelBuilder
from src.features.assembler import FeatureAssembler
from src.models.attrition import AttritionModel
from src.models.evaluator import ModelEvaluator
from src.config import TARGET_SEPARATION, TARGET_INTENTION


@dataclass
class ExperimentResult:
    target: str
    model_type: str
    test_year: int
    n_train: int
    n_test: int
    train_pos_rate: float
    test_pos_rate: float
    metrics: dict = field(default_factory=dict)
    importance: pd.Series = None
    model: AttritionModel = None


def _xgboost_available() -> bool:
    try:
        import xgboost  # noqa: F401
        return True
    except Exception:
        return False


def _time_split(frame: pd.DataFrame, test_year: int):
    train = frame[frame["year"] < test_year]
    test = frame[frame["year"] == test_year]
    return train, test


def run_experiment(
    panel_builder: PanelBuilder,
    assembler: FeatureAssembler,
    target: str,
    test_year: int,
    model_type: str = "histgbm",
    intention_scope: str = "active",
) -> ExperimentResult:
    frame = panel_builder.build_modeling_frame(target, intention_scope=intention_scope)
    X_all = assembler.build(frame)
    y_all = frame[target]

    tr_idx, te_idx = _time_split(frame, test_year)
    X_tr, y_tr = X_all.loc[tr_idx.index], y_all.loc[tr_idx.index]
    X_te, y_te = X_all.loc[te_idx.index], y_all.loc[te_idx.index]

    model = AttritionModel(model_type=model_type).fit(X_tr, y_tr)
    y_prob = model.predict_proba(X_te)

    metrics = ModelEvaluator().evaluate(y_te, y_prob)
    try:
        importance = model.feature_importance(X_te, y_te)
    except Exception:
        importance = None

    return ExperimentResult(
        target=target, model_type=model_type, test_year=test_year,
        n_train=len(X_tr), n_test=len(X_te),
        train_pos_rate=float(y_tr.mean()), test_pos_rate=float(y_te.mean()),
        metrics=metrics, importance=importance, model=model,
    )


def run_all(data_dir: str, synthetic: bool = False):
    loader = DataLoader(data_dir, synthetic=synthetic)
    pb = PanelBuilder(loader)
    fa = FeatureAssembler()

    # Separation label is only defined for waves that have a following wave;
    # intention label is defined for every wave. Choose the latest usable
    # year as the held-out test set for each target.
    plans = [
        (TARGET_SEPARATION, 2024),
        (TARGET_INTENTION, 2025),
    ]
    model_types = ["logistic", "histgbm"]
    if _xgboost_available():
        model_types.append("xgboost")

    results = []
    for target, test_year in plans:
        for model_type in model_types:
            res = run_experiment(pb, fa, target, test_year, model_type=model_type)
            results.append(res)
            print(
                f"[{target:24s} | {model_type:9s} | test={test_year}] "
                f"n_train={res.n_train:6d} n_test={res.n_test:6d} "
                f"pos(tr/te)={res.train_pos_rate:.3f}/{res.test_pos_rate:.3f} "
                f"AUC={res.metrics['auc_roc']:.3f} PR-AUC={res.metrics['auc_pr']:.3f}"
            )
    return results


def main():
    parser = argparse.ArgumentParser(description="JPSED attrition experiment")
    parser.add_argument("--data-dir", default=None, help="Directory of raw JPSED waves")
    parser.add_argument("--synthetic", action="store_true", help="Use bundled synthetic data")
    args = parser.parse_args()

    if args.synthetic or args.data_dir is None:
        data_dir = "data/synthetic"
        synthetic = True
    else:
        data_dir = args.data_dir
        synthetic = False

    run_all(data_dir, synthetic=synthetic)


if __name__ == "__main__":
    main()
