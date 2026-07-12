"""Longitudinal (panel-attrition) survey weights for the transition frame.

JPSED ships *attrition weights* (脱落ウェイト) in separate SSJDA datasets. The
"prior-year comparison" weight ``xa{Y}_l{Y-1}`` re-weights the two-year continuing
sample (respondents present in both year ``Y-1`` and ``Y``) back to the ``Y-1``
population — exactly the sample underlying a transition from ``t = Y-1`` to
``t+1 = Y``. Applying it corrects for panel attrition (selective drop-out), the
main selection-bias threat to the transition models and backtest.

Source column per transition year ``t`` (weight ``xa{t+1}_l{t}``) and the SSJDA
weight directory that carries it:
"""

import os
import pandas as pd

# transition from-year t -> (weight survey-number dir, weight column xa{t+1}_l{t})
WEIGHT_SOURCE = {
    2017: ("1430", "xa18_l17"),
    2018: ("1524", "xa19_l18"),
    2019: ("1524", "xa20_l19"),
    2020: ("1524", "xa21_l20"),
    2021: ("1524", "xa22_l21"),
    2022: ("1731", "xa23_l22"),
    2023: ("1776", "xa24_l23"),
    2024: ("1776", "xa25_l24"),
}


class AttritionWeights:
    """Load and attach JPSED prior-year attrition weights, keyed by pkey/year."""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self._cache = {}

    def _weight_series(self, survey_dir: str, column: str) -> pd.Series:
        key = (survey_dir, column)
        if key in self._cache:
            return self._cache[key]
        root = os.path.join(self.data_dir, survey_dir)
        csv = None
        for base in (root, os.path.join(root, "japanese")):
            if os.path.isdir(base):
                for f in sorted(os.listdir(base)):
                    if f.endswith(".csv"):
                        csv = os.path.join(base, f)
                        break
            if csv:
                break
        if csv is None:
            raise FileNotFoundError(f"No weight CSV under {root}")
        for enc in ("utf-8-sig", "cp932", "shift-jis"):
            try:
                df = pd.read_csv(csv, usecols=["pkey", column], encoding=enc)
                break
            except (UnicodeDecodeError, ValueError):
                continue
        s = pd.Series(pd.to_numeric(df[column], errors="coerce").values,
                      index=pd.to_numeric(df["pkey"], errors="coerce").values)
        s = s[~s.index.duplicated()]
        self._cache[key] = s
        return s

    def attach(self, transition_frame: pd.DataFrame, pkey_col="pkey",
               year_col="year", out_col="attrition_weight") -> pd.Series:
        """Return a weight Series aligned to ``transition_frame`` rows.

        For each row (person, from-year t) the weight is ``xa{t+1}_l{t}`` for that
        person; rows whose year has no weight source, or persons absent from the
        weight file, get NaN.
        """
        w = pd.Series(index=transition_frame.index, dtype=float)
        pk = pd.to_numeric(transition_frame[pkey_col], errors="coerce")
        for t, (survey_dir, column) in WEIGHT_SOURCE.items():
            mask = transition_frame[year_col] == t
            if not mask.any():
                continue
            try:
                s = self._weight_series(survey_dir, column)
            except FileNotFoundError:
                continue
            w.loc[mask] = pk[mask].map(s).values
        return w.rename(out_col)
