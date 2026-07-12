"""Assemble the full feature matrix from the person-year panel."""

import pandas as pd

from src.features.demographics import DemographicFeatureBuilder
from src.features.employment import EmploymentFeatureBuilder
from src.features.salary import SalaryFeatureBuilder
from src.data.macro import MacroFeatureBuilder
from src.config import (
    DEMOGRAPHIC_FEATURES, EMPLOYMENT_FEATURES, SALARY_FEATURES, MACRO_FEATURES,
)


class FeatureAssembler:
    """Produce the model-ready feature matrix ``X`` aligned to the panel index.

    Parameters
    ----------
    include_macro:
        When True (default), append CPI / real-income features. Set False to
        reproduce the nominal-only prototype.
    """

    def __init__(self, include_macro: bool = True):
        self.include_macro = include_macro
        self.demographics = DemographicFeatureBuilder()
        self.employment = EmploymentFeatureBuilder()
        self.salary = SalaryFeatureBuilder()
        self.macro = MacroFeatureBuilder() if include_macro else None

    def build(self, panel: pd.DataFrame) -> pd.DataFrame:
        parts = [
            self.demographics.build(panel),
            self.employment.build(panel),
            self.salary.build(panel),
        ]
        if self.include_macro:
            parts.append(self.macro.build(panel))
        return pd.concat(parts, axis=1)

    @property
    def feature_names(self) -> list:
        names = DEMOGRAPHIC_FEATURES + EMPLOYMENT_FEATURES + SALARY_FEATURES
        if self.include_macro:
            names = names + MACRO_FEATURES
        return names
