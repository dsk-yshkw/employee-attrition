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


class RelativeWageBuilder:
    def __init__(self, macro: MacroData = None):
        self.macro = macro or MacroData()

    def build(self, frame: pd.DataFrame, year_col: str = "year",
              own_growth_col: str = "salary_growth_rate") -> pd.DataFrame:
        """Return own/market/relative nominal wage growth aligned to ``frame``."""
        wg = self.macro.wage_growth()                      # calendar_year -> fraction
        own = pd.to_numeric(frame[own_growth_col], errors="coerce")
        market = (pd.to_numeric(frame[year_col], errors="coerce") - 1).map(wg)
        out = pd.DataFrame(index=frame.index)
        out["own_wage_growth"] = own
        out["market_wage_growth"] = market.values
        out["relative_wage_growth"] = own - market.values
        out["fell_behind_market"] = (out["relative_wage_growth"] < 0).astype("float")
        out.loc[own.isna() | market.isna(), "fell_behind_market"] = np.nan
        return out
