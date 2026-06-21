import pandas as pd
from src.config import DEMOGRAPHIC_VARS


class DemographicFeatureBuilder:
    EDUCATION_ORDER = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}  # Q12 value labels

    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame(index=df.index)
        out["gender"] = df["Q1"]                   # 1=male, 2=female
        out["age"] = pd.to_numeric(df["Q2"], errors="coerce")
        out["birth_year"] = pd.to_numeric(df["Q3_1"], errors="coerce")
        out["education"] = df["Q12"].map(self.EDUCATION_ORDER)
        out["has_spouse"] = (df["Q5"] == 1).astype(int)
        out["has_child"] = (df["Q6"] == 1).astype(int)
        return out
