"""Assemble the full feature matrix from the person-year panel."""

import pandas as pd

from src.features.demographics import DemographicFeatureBuilder
from src.features.employment import EmploymentFeatureBuilder
from src.features.salary import SalaryFeatureBuilder
from src.config import DEMOGRAPHIC_FEATURES, EMPLOYMENT_FEATURES, SALARY_FEATURES


class FeatureAssembler:
    """Produce the model-ready feature matrix ``X`` aligned to the panel index."""

    def __init__(self):
        self.demographics = DemographicFeatureBuilder()
        self.employment = EmploymentFeatureBuilder()
        self.salary = SalaryFeatureBuilder()

    def build(self, panel: pd.DataFrame) -> pd.DataFrame:
        demo = self.demographics.build(panel)
        # employment tenure needs the survey year column from the panel.
        emp_input = panel.copy()
        emp = self.employment.build(emp_input)
        sal = self.salary.build(panel)
        X = pd.concat([demo, emp, sal], axis=1)
        return X

    @property
    def feature_names(self) -> list:
        return DEMOGRAPHIC_FEATURES + EMPLOYMENT_FEATURES + SALARY_FEATURES
