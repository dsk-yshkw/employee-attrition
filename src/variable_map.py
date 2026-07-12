"""Per-wave variable mapping for JPSED main-survey waves.

JPSED renumbers survey questions across years, so the same concept lives under
different column names in each wave (e.g. annual income is ``y22_q100_1`` in the
2022 survey but ``y23_q99_1`` in 2023). This module maps a stable *canonical*
name to the actual column in each wave so the rest of the pipeline never has to
know about year-specific question numbers.

Timing convention
------------------
The JPSED "year Y" survey (e.g. 2022) asks about the respondent's employment
status in *December of Y-1* and about job events *during Y-1*. We index each
wave by its survey year ``Y``. A worker's attrition between wave ``Y`` and wave
``Y+1`` is captured by the "quit/left a job" event reported in wave ``Y+1``
(Q57_1 / Q58_1), which refers to the year spanning the two December snapshots.
"""

# Survey year -> SSJDA survey number (directory name under data/).
# These four waves share the consistent ``yNN_`` column naming and a common
# ``pkey``, and form the usable longitudinal panel (2022-2025).
WAVES = {
    2022: 1523,
    2023: 1598,
    2024: 1730,
    2025: 1775,
}

# Two-digit year prefix used in column names, e.g. 2022 -> "y22".
def _prefix(year: int) -> str:
    return f"y{year % 100:02d}"


# For each canonical variable, the question-number *suffix* (without the yNN_
# prefix) in each survey year. A single string means the suffix is identical in
# every wave; a dict overrides specific years.
_SUFFIX = {
    # --- identifiers -----------------------------------------------------
    "pkey": {"_all": "pkey", "_raw": True},          # common panel ID (no prefix)
    # --- demographics ----------------------------------------------------
    "gender": "q1",                                  # 1=male, 2=female
    "age": "q2",
    "birth_year": "q3_1",
    "education": "q5",                               # ordinal education level
    "has_spouse_raw": "q9",                          # 1=has spouse
    "has_child_raw": "q10",                          # 1=has child
    "num_children": "q11",
    "youngest_child_age": "unq12",
    # --- employment (December of previous year) --------------------------
    "emp_status": "q17",                             # 1-6 employed, 7 unemployed, 8-11 NILF
    "work_style": "q18",                             # 1=employee, 2=exec, 3-4=self-emp, 5-6=family/home
    "contract_type": "q19",                          # 1=regular, 2=part, 3=dispatch, 4=contract, 5=shokutaku
    "industry": "q30",
    "firm_size": "q31",
    "occupation": "q32",
    "position": "q33",                               # managerial rank
    "weekly_hours": "q37_2",                         # hours worked per week
    # --- salary / income (previous calendar year) ------------------------
    "annual_income": {2022: "q100_1", 2023: "q99_1", 2024: "q99_1", 2025: "q99_1"},
    # --- tenure ----------------------------------------------------------
    "current_job_start_year": {
        2022: "qn99_11", 2023: "qn98_11", 2024: "qn98_11", 2025: "qn98_11",
    },
    # --- turnover intention (stated) -------------------------------------
    # 1=actively job-hunting, 2=wants to change (not acting),
    # 3=wants to change eventually, 4=no intention to change.
    "intention": {2022: "q106", 2023: "q105", 2024: "q105", 2025: "q105"},
    # --- retrospective job events (past year, MA: 1=selected) ------------
    "ev_quit": {2022: "q57_1", 2023: "q57_1", 2024: "q58_1", 2025: "q58_1"},
    "ev_started_job": {2022: "q57_2", 2023: "q57_2", 2024: "q58_2", 2025: "q58_2"},
}


def column_for(canonical: str, year: int) -> str:
    """Return the actual CSV column name for a canonical variable in a wave."""
    spec = _SUFFIX[canonical]
    if isinstance(spec, dict) and spec.get("_raw"):
        return spec["_all"]
    if isinstance(spec, dict):
        suffix = spec[year]
    else:
        suffix = spec
    return f"{_prefix(year)}_{suffix}"


def rename_map(year: int) -> dict:
    """Mapping {actual_column: canonical_name} for renaming a wave's dataframe."""
    out = {}
    for canonical in _SUFFIX:
        out[column_for(canonical, year)] = canonical
    return out


def canonical_columns() -> list:
    """All canonical variable names produced by the loader."""
    return list(_SUFFIX.keys())
