"""Relative-wage-growth feature: own wage growth vs the external market rate.

Motivation: a worker's outside option rises with the market wage. Someone whose
own pay stagnates while the market pays more has fallen behind and faces a
stronger incentive to quit. We measure this as

    relative_wage_growth = own_nominal_growth - market_nominal_growth

where the market rate is the MHLW society-wide total-cash-earnings growth for the
period the worker's own growth spans (see ``src/data/macro.py``). Because JPSED
wave ``t`` reports income for calendar ``t-1``, own growth at transition-year
``t`` spans calendar ``(t-2)->(t-1)`` and the matching market rate is the MHLW
year ``t-1`` figure.

Caveats: JPSED annual income is coarse (median YoY change is 0), so own growth is
noisy; and the society-wide market rate is year-level (little within-year
variation). An industry×year market rate (JSIC divisions from the same survey) is
the planned refinement for cleaner within-year identification.
"""

import numpy as np
import pandas as pd

from src.data.macro import MacroData
from src.features.industry_map import to_jsic


class RelativeWageBuilder:
    def __init__(self, macro: MacroData = None):
        self.macro = macro or MacroData()

    def build(self, frame: pd.DataFrame, year_col: str = "year",
              own_growth_col: str = "salary_growth_rate",
              industry_col: str = "industry", by_industry: bool = True) -> pd.DataFrame:
        """Return own/market/relative nominal wage growth aligned to ``frame``.

        The market rate matches the worker's own-growth period (calendar
        ``year-1``). When ``by_industry`` is True and industry wage data is
        available, the market rate is the worker's JSIC-division rate for that
        year (giving within-year variation for identification), falling back to
        the all-industry rate where the mapping/data is missing.
        """
        wg = self.macro.wage_growth()                       # calendar_year -> fraction
        ref_year = pd.to_numeric(frame[year_col], errors="coerce") - 1
        own = pd.to_numeric(frame[own_growth_col], errors="coerce")

        market_all = ref_year.map(wg)
        market = market_all.copy()
        used_industry = pd.Series(False, index=frame.index)

        iwg = self.macro.industry_wage_growth() if by_industry else pd.Series(dtype=float)
        if not iwg.empty and industry_col in frame.columns:
            jsic = frame[industry_col].map(to_jsic)
            keys = list(zip(ref_year.astype("Int64"), jsic))
            ind_rate = pd.Series(
                [iwg.get((int(y), s)) if (pd.notna(y) and s is not None) else None
                 for y, s in keys], index=frame.index, dtype="float")
            used_industry = ind_rate.notna()
            market = ind_rate.where(used_industry, market_all)

        out = pd.DataFrame(index=frame.index)
        out["own_wage_growth"] = own
        out["market_wage_growth"] = market.values
        out["market_is_industry"] = used_industry.astype("int8").values
        out["relative_wage_growth"] = own - market.values
        out["fell_behind_market"] = (out["relative_wage_growth"] < 0).astype("float")
        out.loc[own.isna() | market.isna(), "fell_behind_market"] = np.nan
        return out
