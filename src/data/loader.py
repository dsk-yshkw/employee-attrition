"""Load JPSED main-survey waves and harmonise them to canonical variable names."""

import os
from typing import Dict, Optional

import pandas as pd

from src.config import MISSING_VALUES
from src.variable_map import WAVES, rename_map, canonical_columns


class DataLoader:
    """Read one CSV per survey wave and rename year-specific columns.

    Parameters
    ----------
    data_dir:
        Directory that contains one sub-directory per survey number
        (e.g. ``.../data/1523/1523.csv``). For the bundled synthetic data,
        each wave is a flat file ``<year>.csv`` already using canonical names.
    synthetic:
        When True, expect files named ``<year>.csv`` with canonical columns and
        skip the rename/missing-value step.
    """

    def __init__(self, data_dir: str, synthetic: bool = False):
        self.data_dir = data_dir
        self.synthetic = synthetic

    # -- public API ---------------------------------------------------------
    def load_wave(self, year: int) -> pd.DataFrame:
        path = self._find_csv(year)
        df = self._read_csv(path)
        if not self.synthetic:
            df = self._harmonise(df, year)
        df["year"] = year
        return df

    def load_all_waves(self) -> Dict[int, pd.DataFrame]:
        waves = {}
        for year in sorted(WAVES):
            try:
                waves[year] = self.load_wave(year)
            except FileNotFoundError:
                continue
        if not waves:
            raise FileNotFoundError(f"No wave CSVs found under {self.data_dir}")
        return waves

    # -- internals ----------------------------------------------------------
    def _read_csv(self, path: str) -> pd.DataFrame:
        last_err: Optional[Exception] = None
        for enc in ("utf-8-sig", "cp932", "shift-jis"):
            try:
                df = pd.read_csv(path, encoding=enc, low_memory=False)
                if df.shape[1] <= 1:
                    raise pd.errors.EmptyDataError(f"only {df.shape[1]} column(s)")
                return df
            except (UnicodeDecodeError, pd.errors.EmptyDataError) as err:
                last_err = err
                continue
        raise RuntimeError(f"Could not read {path}: {last_err}")

    def _harmonise(self, df: pd.DataFrame, year: int) -> pd.DataFrame:
        mapping = rename_map(year)
        present = {src: dst for src, dst in mapping.items() if src in df.columns}
        missing = sorted(set(mapping.values()) - set(present.values()))
        renamed = df.rename(columns=present)
        keep = [c for c in canonical_columns() if c in renamed.columns]
        out = renamed[keep].copy()
        if missing:
            out.attrs["missing_canonical"] = missing
        return self._replace_missing(out)

    def _replace_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        for col, sentinels in MISSING_VALUES.items():
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").replace(
                    {s: pd.NA for s in sentinels}
                )
        return df

    def _find_csv(self, year: int) -> str:
        if self.synthetic:
            path = os.path.join(self.data_dir, f"{year}.csv")
            if os.path.isfile(path):
                return path
            raise FileNotFoundError(path)

        survey_number = WAVES[year]
        root = os.path.join(self.data_dir, str(survey_number))
        # Real data may live in the wave directory directly or under japanese/.
        for base in (root, os.path.join(root, "japanese")):
            if not os.path.isdir(base):
                continue
            csvs = sorted(f for f in os.listdir(base) if f.endswith(".csv"))
            if csvs:
                return os.path.join(base, csvs[0])
        raise FileNotFoundError(f"No CSV for survey {survey_number} under {root}")
