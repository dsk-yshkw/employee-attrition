"""Employment features from canonical variables."""

import pandas as pd


class EmploymentFeatureBuilder:
    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame(index=df.index)
        out["contract_type"] = pd.to_numeric(df.get("contract_type"), errors="coerce")  # Q19 1=regular..
        out["industry"] = pd.to_numeric(df.get("industry"), errors="coerce")            # Q30
        out["firm_size"] = pd.to_numeric(df.get("firm_size"), errors="coerce")          # Q31 ordinal
        out["occupation"] = pd.to_numeric(df.get("occupation"), errors="coerce")        # Q32
        out["position"] = pd.to_numeric(df.get("position"), errors="coerce")            # Q33 managerial rank
        out["weekly_hours"] = pd.to_numeric(df.get("weekly_hours"), errors="coerce")    # Q37
        out["is_regular"] = (out["contract_type"] == 1).astype("int8")

        # Tenure = reference year (survey year - 1) minus current-job start year.
        start_year = pd.to_numeric(df.get("current_job_start_year"), errors="coerce")
        ref_year = pd.to_numeric(df.get("year"), errors="coerce") - 1
        tenure = ref_year - start_year
        out["tenure_years"] = tenure.where((tenure >= 0) & (tenure < 70))
        return out
