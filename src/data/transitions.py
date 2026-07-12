"""Build a one-year transition frame: worker state at t -> outcomes at t+1.

For every employee observed in wave ``t`` who also has a following wave ``t+1``,
we record their feature state at ``t`` together with what happened by ``t+1``:

- ``separated``      : reported quitting/leaving a job during the year (ev_quit).
- ``employed_next``  : had a job in December of the next wave (emp_status 1-6).
- ``income_next``     : *nominal* annual income observed in wave ``t+1`` (man-yen).
- ``real_income_next``: real (CPI-deflated) annual income observed in wave ``t+1``.

Wage sub-models are trained on the *nominal* next income so that the simulator
can deflate by a scenario CPI path (sticky-nominal-wage assumption): higher
inflation then mechanically erodes real income.

These feed the transition sub-models (separation, re-employment, wage) that the
multi-year microsimulation iterates forward.
"""

import numpy as np
import pandas as pd

from src.config import PKEY, EMPLOYED_STATUS_CODES
from src.data.macro import MacroFeatureBuilder
from src.features.assembler import FeatureAssembler


class TransitionFrameBuilder:
    def __init__(self, panel_builder, assembler: FeatureAssembler = None,
                 macro: MacroFeatureBuilder = None):
        self.pb = panel_builder
        self.assembler = assembler or FeatureAssembler()
        self.macro = macro or MacroFeatureBuilder()

    def build(self) -> pd.DataFrame:
        panel = self.pb.build()
        panel = panel.reset_index(drop=True)

        # Real income for every person-year (current-wave outcome).
        real_income = self.macro.build(panel)["real_annual_income"]
        panel = panel.assign(
            real_income=real_income.values,
            nominal_income=pd.to_numeric(panel["annual_income"], errors="coerce").values,
        )

        # Next-wave outcomes, aligned onto the current row by (pkey, year).
        nxt = panel[[PKEY, "year", "emp_status", "ev_quit",
                     "real_income", "nominal_income"]].copy()
        nxt["year"] = nxt["year"] - 1
        nxt = nxt.rename(columns={
            "emp_status": "emp_status_next",
            "ev_quit": "ev_quit_next",
            "real_income": "real_income_next",
            "nominal_income": "income_next",
        })
        panel = panel.merge(nxt, on=[PKEY, "year"], how="left")

        has_next = panel["emp_status_next"].notna() | panel["ev_quit_next"].notna()
        panel = panel[has_next].copy()

        # Restrict base population to employees at t.
        panel = panel[self.pb.employee_mask(panel)].copy()

        panel["separated"] = (
            pd.to_numeric(panel["ev_quit_next"], errors="coerce") == 1
        ).astype(int)
        panel["employed_next"] = (
            pd.to_numeric(panel["emp_status_next"], errors="coerce")
            .isin(EMPLOYED_STATUS_CODES).astype(int)
        )

        # Feature matrix at t (aligned to the surviving rows).
        X = self.assembler.build(panel)
        X.index = panel.index
        out = pd.concat(
            [panel[[PKEY, "year", "separated", "employed_next",
                    "real_income", "real_income_next", "income_next"]], X],
            axis=1,
        )
        return out.reset_index(drop=True), list(X.columns)
