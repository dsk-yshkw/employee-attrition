import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
import joblib


class AttritionModel:
    SUPPORTED_MODELS = ("logistic", "xgboost")

    def __init__(self, model_type: str = "xgboost", random_state: int = 42):
        if model_type not in self.SUPPORTED_MODELS:
            raise ValueError(f"model_type must be one of {self.SUPPORTED_MODELS}")
        self.model_type = model_type
        self.random_state = random_state
        self.pipeline = self._build_pipeline()
        self.feature_names_ = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "AttritionModel":
        self.feature_names_ = list(X.columns)
        self.pipeline.fit(X, y)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.pipeline.predict_proba(X)[:, 1]

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.pipeline.predict(X)

    def save(self, path: str) -> None:
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: str) -> "AttritionModel":
        return joblib.load(path)

    def _build_pipeline(self) -> Pipeline:
        imputer = SimpleImputer(strategy="median")
        scaler = StandardScaler()

        if self.model_type == "logistic":
            clf = LogisticRegression(max_iter=1000, random_state=self.random_state)
            return Pipeline([("imputer", imputer), ("scaler", scaler), ("clf", clf)])

        clf = XGBClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=self.random_state,
        )
        return Pipeline([("imputer", imputer), ("clf", clf)])
