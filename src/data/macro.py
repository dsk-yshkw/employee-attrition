"""Macro data (CPI / inflation) loading and real-income feature construction.

The CPI table (``data/macro/japan_cpi.csv``, 2020=100) is bundled with the repo
because it is public official statistics. It is merged onto the person-year panel
to deflate nominal income into real terms and to expose inflation as a feature.

Timing: JPSED wave ``Y`` reports income for calendar year ``Y-1``. So wave ``Y``'s
income is deflated by CPI of ``Y-1``, and the real income growth between waves
``Y-1`` and ``Y`` subtracts the inflation of year ``Y-1``.
"""

import os
import numpy as np
import pandas as pd

from src.config import PKEY

# Default to the repo-bundled CPI file, resolved relative to this module so it
# works from any working directory (including a fresh Colab clone).
_DEFAULT_CPI_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "macro", "japan_cpi.csv",
)


class MacroData:
    def __init__(self, cpi_path: str = _DEFAULT_CPI_PATH):
        self.cpi_path = cpi_path
        self.cpi = pd.read_csv(cpi_path)

    def frame(self) -> pd.DataFrame:
        return self.cpi

    def lookup(self) -> pd.DataFrame:
        """CPI indexed by calendar_year for fast joins."""
        return self.cpi.set_index("calendar_year")


class MacroFeatureBuilder:
    """Real-income and inflation features aligned to the panel index.

    Expects a long panel with ``pkey``, ``year`` (survey year) and
    ``annual_income`` (nominal, man-yen). Deflates using the CPI of the income's
    reference calendar year (``year - 1``).
    """

    def __init__(self, macro: MacroData = None):
        self.macro = macro or MacroData()

    def build(self, panel: pd.DataFrame) -> pd.DataFrame:
        cpi = self.macro.lookup()
        ref_year = pd.to_numeric(panel["year"], errors="coerce") - 1

        cpi_all = ref_year.map(cpi["cpi_all_items"])
        inflation = ref_year.map(cpi["inflation_all_items"])
        nominal = pd.to_numeric(panel["annual_income"], errors="coerce")
        real_income = nominal / (cpi_all / 100.0)

        work = panel[[PKEY, "year"]].copy()
        work["real_income"] = real_income.values
        work = work.sort_values([PKEY, "year"])
        work["prev_year"] = work.groupby(PKEY)["year"].shift(1)
        work["prev_real_income"] = work.groupby(PKEY)["real_income"].shift(1)
        consecutive = work["prev_year"] == work["year"] - 1
        work.loc[~consecutive, "prev_real_income"] = np.nan
        prev_real = work["prev_real_income"].reindex(panel.index)

        real_growth = (real_income - prev_real) / prev_real.replace(0, np.nan)

        out = pd.DataFrame(index=panel.index)
        out["cpi"] = cpi_all.values                       # price level (ref year)
        out["inflation_rate"] = inflation.values          # YoY %, ref year
        out["real_annual_income"] = real_income.values
        out["real_prev_annual_income"] = prev_real.values
        out["real_salary_growth_rate"] = real_growth.clip(-1.0, 3.0).values
        return out
