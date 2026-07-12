"""Build a long person-year panel and derive attrition target labels."""

import numpy as np
import pandas as pd

from src.data.loader import DataLoader
from src.config import (
    PKEY,
    EMPLOYED_STATUS_CODES,
    EMPLOYEE_WORK_STYLE,
    INTENTION_ACTIVE,
    INTENTION_ANY,
    TARGET_SEPARATION,
    TARGET_INTENTION,
)


class PanelBuilder:
    """Assemble waves into a person-year panel and attach attrition labels.

    Row grain: one respondent (``pkey``) per survey ``year``. Features describe
    the worker's situation *as of* that wave; the separation target describes
    whether they left their job by the *next* wave.
    """

    def __init__(self, loader: DataLoader):
        self.loader = loader

    # -- assembly -----------------------------------------------------------
    def build(self) -> pd.DataFrame:
        waves = self.loader.load_all_waves()
        panel = pd.concat(waves.values(), ignore_index=True)
        panel[PKEY] = pd.to_numeric(panel[PKEY], errors="coerce")
        panel = panel.dropna(subset=[PKEY])
        panel = panel.sort_values([PKEY, "year"]).reset_index(drop=True)
        return panel

    # -- population ---------------------------------------------------------
    @staticmethod
    def employee_mask(panel: pd.DataFrame) -> pd.Series:
        """True for wage/salary employees in December of the reference year.

        Employed (Q17 in 1-6) AND employed by a company/organisation
        (Q18 == 1), i.e. excluding executives, the self-employed, family
        workers and home workers.
        """
        emp = pd.to_numeric(panel["emp_status"], errors="coerce").isin(
            EMPLOYED_STATUS_CODES
        )
        employee = pd.to_numeric(panel["work_style"], errors="coerce") == EMPLOYEE_WORK_STYLE
        return emp & employee

    # -- targets ------------------------------------------------------------
    def add_targets(
        self, panel: pd.DataFrame, intention_scope: str = "active"
    ) -> pd.DataFrame:
        """Attach both attrition labels.

        ``attrition_separation``: 1 if the worker reports having quit/left a job
        (ev_quit) in the *next* wave, i.e. an actual separation observed between
        wave t and t+1. NaN when there is no next wave for that person.

        ``attrition_intention``: 1 if the worker states a turnover intention in
        the *current* wave (Q106/Q105). ``intention_scope`` is "active"
        (codes 1-2) or "any" (codes 1-3).
        """
        panel = panel.copy()

        # --- actual separation from the next wave -------------------------
        nxt = panel[[PKEY, "year", "ev_quit", "emp_status", "current_job_start_year"]].copy()
        nxt["year"] = nxt["year"] - 1  # align next wave onto current row
        nxt = nxt.rename(
            columns={
                "ev_quit": "next_ev_quit",
                "emp_status": "next_emp_status",
                "current_job_start_year": "next_job_start_year",
            }
        )
        panel = panel.merge(nxt, on=[PKEY, "year"], how="left")

        # Primary definition: the worker self-reports having quit/left a job
        # during the year between the two December snapshots (Q57_1 / Q58_1).
        # This is the clean, direct separation measure (~8%/yr for employees).
        quit_event = pd.to_numeric(panel["next_ev_quit"], errors="coerce") == 1

        # Diagnostic-only signal, NOT folded into the label: the reported
        # current-job start year advancing between waves. In practice this is
        # dominated by year-to-year re-reporting noise (~22%), so it is kept as
        # a separate column for inspection rather than used as a target.
        start_prev = pd.to_numeric(panel["current_job_start_year"], errors="coerce")
        start_next = pd.to_numeric(panel["next_job_start_year"], errors="coerce")
        panel["diag_changed_start_year"] = ((start_next - start_prev) > 0).astype("float")

        separated = quit_event.astype("float")
        has_next = panel["next_ev_quit"].notna() | panel["next_emp_status"].notna()
        separated[~has_next] = np.nan
        panel[TARGET_SEPARATION] = separated

        # --- stated turnover intention (current wave) ---------------------
        codes = INTENTION_ACTIVE if intention_scope == "active" else INTENTION_ANY
        intent = pd.to_numeric(panel["intention"], errors="coerce")
        label = intent.isin(codes).astype("float")
        label[intent.isna()] = np.nan
        panel[TARGET_INTENTION] = label

        return panel

    # -- convenience --------------------------------------------------------
    def build_modeling_frame(
        self, target: str, intention_scope: str = "active"
    ) -> pd.DataFrame:
        """Full pipeline: build panel, restrict to employees, attach labels,
        and drop rows where the requested target is undefined."""
        panel = self.build()
        panel = self.add_targets(panel, intention_scope=intention_scope)
        panel = panel[self.employee_mask(panel)].copy()
        panel = panel[panel[target].notna()].copy()
        panel[target] = panel[target].astype(int)
        return panel
