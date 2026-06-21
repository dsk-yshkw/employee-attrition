import pandas as pd
from src.config import PKEY


class SalaryFeatureBuilder:
    def build(self, panel: pd.DataFrame) -> pd.DataFrame:
        """Compute salary level and growth rate from annual income (Q85_1, unit: 10,000 JPY)."""
        out = pd.DataFrame(index=panel.index)
        out["annual_income"] = pd.to_numeric(panel["Q85_1"], errors="coerce")

        panel_sorted = panel[[PKEY, "wave", "Q85_1"]].copy()
        panel_sorted["annual_income"] = pd.to_numeric(panel_sorted["Q85_1"], errors="coerce")
        panel_sorted = panel_sorted.sort_values([PKEY, "wave"])

        panel_sorted["prev_income"] = panel_sorted.groupby(PKEY)["annual_income"].shift(1)
        panel_sorted["salary_growth_rate"] = (
            (panel_sorted["annual_income"] - panel_sorted["prev_income"])
            / panel_sorted["prev_income"]
        )

        growth = panel_sorted[[PKEY, "wave", "salary_growth_rate", "prev_income"]]
        out = out.join(
            growth.set_index([panel.index])[["salary_growth_rate", "prev_income"]],
            how="left",
        )
        return out

    def build_from_merged(self, panel: pd.DataFrame) -> pd.DataFrame:
        """Use when panel already has a single index aligned to the feature dataframe."""
        income = pd.to_numeric(panel["Q85_1"], errors="coerce")
        prev_income = panel.groupby(PKEY)["Q85_1"].transform(
            lambda s: pd.to_numeric(s, errors="coerce").shift(1)
        )
        growth_rate = (income - prev_income) / prev_income

        out = pd.DataFrame(index=panel.index)
        out["annual_income"] = income
        out["prev_annual_income"] = prev_income
        out["salary_growth_rate"] = growth_rate
        return out
