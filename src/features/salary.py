"""Salary level and year-over-year salary-growth features.

Income is ``annual_income`` (main job, previous calendar year, unit: man-yen /
10,000 JPY). The growth rate compares a worker's income to their own income in
the previous wave, matched by ``pkey``.

Note on "excluding scheduled pay raises": JPSED does not record a base-pay vs.
scheduled-increment breakdown, so ``salary_growth_rate`` is the raw
year-over-year change. It therefore mixes scheduled raises (定期昇給) with
promotions, job changes and hours changes. This is documented as a known
limitation; downstream models can still use it as a relative-change signal.
"""

import numpy as np
import pandas as pd

from src.config import PKEY


class SalaryFeatureBuilder:
    def build(self, panel: pd.DataFrame) -> pd.DataFrame:
        """Compute income level, previous-wave income and YoY growth rate.

        Expects a long panel with ``pkey``, ``year`` and ``annual_income``.
        Returns a frame aligned to ``panel.index``.
        """
        work = panel[[PKEY, "year"]].copy()
        work["annual_income"] = pd.to_numeric(panel["annual_income"], errors="coerce")
        work = work.sort_values([PKEY, "year"])

        work["prev_year"] = work.groupby(PKEY)["year"].shift(1)
        work["prev_annual_income"] = work.groupby(PKEY)["annual_income"].shift(1)
        # Only treat the previous wave as valid if it is exactly one year earlier.
        consecutive = work["prev_year"] == work["year"] - 1
        work.loc[~consecutive, "prev_annual_income"] = np.nan

        prev = work["prev_annual_income"]
        growth = (work["annual_income"] - prev) / prev.replace(0, np.nan)

        out = pd.DataFrame(index=panel.index)
        out["annual_income"] = work["annual_income"].reindex(panel.index)
        out["prev_annual_income"] = prev.reindex(panel.index)
        out["salary_growth_rate"] = growth.reindex(panel.index)
        # Winsorise extreme growth to reduce leverage from tiny denominators.
        out["salary_growth_rate"] = out["salary_growth_rate"].clip(-1.0, 3.0)
        return out
