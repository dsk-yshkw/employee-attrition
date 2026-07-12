"""Demographic and household features from canonical variables."""

import pandas as pd


class DemographicFeatureBuilder:
    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame(index=df.index)
        out["gender"] = pd.to_numeric(df.get("gender"), errors="coerce")   # 1=male, 2=female
        out["age"] = pd.to_numeric(df.get("age"), errors="coerce")
        out["education"] = pd.to_numeric(df.get("education"), errors="coerce")
        # Q9: 1 = has spouse. Q10: 1 = has child.
        out["has_spouse"] = (pd.to_numeric(df.get("has_spouse_raw"), errors="coerce") == 1).astype("int8")
        out["has_child"] = (pd.to_numeric(df.get("has_child_raw"), errors="coerce") == 1).astype("int8")
        num_children = pd.to_numeric(df.get("num_children"), errors="coerce")
        # Respondents with no child skip Q11; treat missing as 0 children.
        out["num_children"] = num_children.where(out["has_child"] == 1, 0)
        out["youngest_child_age"] = pd.to_numeric(df.get("youngest_child_age"), errors="coerce")
        return out
