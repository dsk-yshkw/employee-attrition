"""Dynamic microsimulation of multi-year attrition.

A base-year cohort of employees is propagated forward year by year using the
fitted :class:`~src.models.transitions.TransitionModels`. Each simulated year,
for every worker still employed:

1. draw separation ~ Bernoulli(P_separate(state));
2. stayers: real income <- wage_stay(state), tenure += 1;
3. separators: draw re-employment ~ Bernoulli(P_reemploy(state));
   - re-employed: real income <- wage_move(state), tenure = 0;
   - otherwise: the worker exits the employed population;
4. everyone ages by one year; nominal income, growth rates, CPI and inflation are
   updated from the (scenario) CPI path.

The CPI path can be overridden to run counterfactual inflation scenarios.

Timing: a state indexed by wave year ``Y`` carries the CPI of its reference year
``Y-1``. Advancing to ``Y+1`` sets CPI/inflation to those of year ``Y``.

Simplifications (documented for the paper): static attributes (education,
industry, occupation, firm size, contract type, family) are held fixed; wages
use the model's conditional mean plus optional Gaussian noise; the cohort is
closed (no new labour-market entrants).
"""

import numpy as np
import pandas as pd

from src.data.macro import MacroData
from src.features.assembler import FeatureAssembler


def initial_state(panel_builder, assembler: FeatureAssembler, year: int) -> pd.DataFrame:
    """Feature vectors for the employees observed in ``year`` (the base cohort)."""
    panel = panel_builder.build()
    panel = panel[(panel["year"] == year) & panel_builder.employee_mask(panel)].copy()
    X = assembler.build(panel).reset_index(drop=True)
    return X


class MicroSimulator:
    def __init__(self, transition_models, feature_cols, macro: MacroData = None):
        self.tm = transition_models
        self.feature_cols = list(feature_cols)
        self.cpi = (macro or MacroData()).lookup()  # indexed by calendar_year

    def _cpi_for(self, ref_year: int, override) -> tuple:
        table = override if (override is not None and ref_year in override.index) else self.cpi
        row = table.loc[ref_year]
        return float(row["cpi_all_items"]), float(row["inflation_all_items"])

    def simulate(self, init_state: pd.DataFrame, start_year: int, n_years: int,
                 seed: int = 0, cpi_override: pd.DataFrame = None,
                 wage_noise_sd: float = 0.0, cola_passthrough: float = 0.0,
                 min_wage_nominal: float = None, group_col: str = None) -> pd.DataFrame:
        """Propagate ``init_state`` (wave ``start_year`` employees) forward.

        Returns a per-year aggregate frame with the separation (attrition) rate,
        re-employment rate, exit rate, surviving population and mean real income.
        The ``year`` column is the *from* wave-year of each transition (matching
        the panel's ``attrition_separation`` definition).

        Wage-policy scenarios (applied to the predicted nominal wage each year):

        - ``cola_passthrough`` in [0, 1]: cost-of-living adjustment. Nominal wages
          are scaled by ``(1 + cola_passthrough * inflation/100)``. 0 = sticky
          nominal (real income erodes with inflation); 1 = wages fully track
          prices (real income protected). Contrasting the two isolates the
          real-wage-erosion channel of attrition.
        - ``min_wage_nominal``: a nominal annual wage floor (man-yen) applied to
          every survivor — a minimum-wage policy lever.
        - ``group_col``: a static feature (e.g. ``contract_type``); when set, the
          per-year attrition rate is also broken down by that group.
        """
        rng = np.random.default_rng(seed)
        state = init_state.copy().reset_index(drop=True)
        groups0 = (state[group_col].to_numpy() if group_col and group_col in state
                   else None)
        year = start_year
        records = []

        for _ in range(n_years):
            X = state[self.feature_cols]
            p_sep = self.tm.p_separate(X)
            sep = rng.random(len(state)) < p_sep
            p_re = self.tm.p_reemploy(X)
            reemp = rng.random(len(state)) < p_re
            w_stay = self.tm.wage_stay(X)
            w_move = self.tm.wage_move(X)

            stay = ~sep
            mv_re = sep & reemp
            exit_mask = sep & ~reemp

            # wage models predict NOMINAL next income; deflate by the (scenario)
            # CPI of the reference year to obtain real income.
            old_real = state["real_annual_income"].to_numpy(dtype=float)
            old_nom = state["annual_income"].to_numpy(dtype=float)
            new_nom = old_nom.copy()
            new_nom[stay] = w_stay[stay]
            new_nom[mv_re] = w_move[mv_re]
            if wage_noise_sd > 0:
                new_nom[stay | mv_re] += rng.normal(
                    0, wage_noise_sd, int((stay | mv_re).sum()))

            ref_year = year  # next wave (year+1) reports income for calendar `year`
            cpi_next, infl_next = self._cpi_for(ref_year, cpi_override)
            if cola_passthrough:                       # wage indexation to prices
                new_nom = new_nom * (1 + cola_passthrough * infl_next / 100.0)
            new_nom = np.clip(new_nom, 5.0, None)
            if min_wage_nominal is not None:           # nominal wage floor
                new_nom = np.maximum(new_nom, min_wage_nominal)

            new_tenure = state["tenure_years"].to_numpy(dtype=float).copy()
            new_tenure[stay] += 1
            new_tenure[mv_re] = 0

            rec = {
                "year": year,
                "pop": int(len(state)),
                "attrition_rate": float(sep.mean()),
                "reemploy_rate_given_sep": float(reemp[sep].mean()) if sep.any() else np.nan,
                "exit_rate": float(exit_mask.mean()),
                "mean_real_income": float(np.nanmean(old_real)),
                "mean_nominal_income": float(np.nanmean(old_nom)),
            }
            if groups0 is not None:
                for gval in np.unique(groups0[~np.isnan(groups0)] if groups0.dtype.kind == "f" else groups0):
                    gm = state[group_col].to_numpy() == gval
                    if gm.any():
                        rec[f"attrition_{group_col}={int(gval)}"] = float(sep[gm].mean())
            records.append(rec)

            # advance survivors to next year (deflate nominal by the scenario CPI)
            keep = ~exit_mask
            new_real = new_nom / (cpi_next / 100.0)

            nxt = state.copy()
            nxt["real_prev_annual_income"] = old_real
            nxt["real_annual_income"] = new_real
            nxt["real_salary_growth_rate"] = np.clip(
                (new_real - old_real) / np.where(old_real == 0, np.nan, old_real), -1, 3)
            nxt["prev_annual_income"] = old_nom
            nxt["annual_income"] = new_nom
            nxt["salary_growth_rate"] = np.clip(
                (new_nom - old_nom) / np.where(old_nom == 0, np.nan, old_nom), -1, 3)
            nxt["age"] = state["age"].to_numpy(dtype=float) + 1
            nxt["tenure_years"] = new_tenure
            nxt["cpi"] = cpi_next
            nxt["inflation_rate"] = infl_next

            state = nxt[keep].reset_index(drop=True)
            year += 1

        return pd.DataFrame(records)


def inflation_scenario(macro: MacroData, delta_pp: float, years) -> pd.DataFrame:
    """Return a CPI table with inflation shifted by ``delta_pp`` percentage points
    for the given calendar ``years`` (CPI level recompounded from the base)."""
    base = macro.lookup().copy()
    table = base.copy()
    for y in years:
        if y not in table.index:
            continue
        table.loc[y, "inflation_all_items"] = base.loc[y, "inflation_all_items"] + delta_pp
        prev = y - 1
        if prev in table.index:
            table.loc[y, "cpi_all_items"] = table.loc[prev, "cpi_all_items"] * (
                1 + table.loc[y, "inflation_all_items"] / 100.0)
    return table
