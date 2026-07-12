"""Per-wave variable mapping for JPSED main-survey waves.

JPSED renumbers survey questions across years, and the column-naming convention
itself changed over time, so the same concept lives under different column names
in each wave:

- 2017-2019 waves use an UPPERCASE ``Y17_``/``Y18_``/``Y19_`` prefix and an
  uppercase ``PKEY`` id (SSJDA "ver2019"/"ver2022" integrated files).
- 2020-2025 waves use a lowercase ``y20_``..``y25_`` prefix and lowercase ``pkey``.
- The 2016 (y16) wave has a different question structure entirely (two-question
  employment block, education under Q12, no youngest-child variable) and is not
  wired in yet.

This module maps a stable *canonical* name to the actual column in each wave so
the rest of the pipeline never has to know about year-specific question numbers
or casing.

Timing convention
------------------
The JPSED "year Y" survey asks about the respondent's employment status in
*December of Y-1* and about job events *during Y-1*. We index each wave by its
survey year ``Y``. Attrition between wave ``Y`` and wave ``Y+1`` is captured by
the "quit/left a job" event reported in wave ``Y+1`` (``ev_quit``).
"""

# Survey year -> SSJDA survey number (directory name under data/).
WAVES = {
    2017: 1164,
    2018: 1227,
    2019: 1279,
    2020: 1349,
    2021: 1429,
    2022: 1523,
    2023: 1598,
    2024: 1730,
    2025: 1775,
}

# Per-wave naming style: (column prefix, case transform for the q-suffix, id column).
_STYLE = {
    2017: ("Y17_", str.upper, "PKEY"),
    2018: ("Y18_", str.upper, "PKEY"),
    2019: ("Y19_", str.upper, "PKEY"),
    2020: ("y20_", str.lower, "pkey"),
    2021: ("y21_", str.lower, "pkey"),
    2022: ("y22_", str.lower, "pkey"),
    2023: ("y23_", str.lower, "pkey"),
    2024: ("y24_", str.lower, "pkey"),
    2025: ("y25_", str.lower, "pkey"),
}


def _same(value, years):
    """Helper: the same suffix for every listed year."""
    return {y: value for y in years}


_ALL = list(WAVES)

# Canonical variable -> question-number suffix (lowercase, no prefix) per year.
# A plain string means "identical suffix in every wave"; a dict gives per-year
# suffixes (a year absent from the dict means the variable is unavailable in that
# wave and is simply dropped by the loader).
_SUFFIX = {
    # --- identifiers -----------------------------------------------------
    "pkey": {"_raw": True},                          # resolved via _STYLE id column
    # --- demographics (stable across 2017-2025) --------------------------
    "gender": "q1",
    "age": "q2",
    "birth_year": "q3_1",
    "education": "q5",
    "has_spouse_raw": "q9",
    "has_child_raw": "q10",
    "num_children": "q11",
    "youngest_child_age": _same("unq12", [2020, 2021, 2022, 2023, 2024, 2025]),
    # --- employment (December of previous year) --------------------------
    "emp_status": "q17",                             # 1-6 employed, 7 unemployed, 8+ NILF
    "work_style": "q18",                             # 1=employee, 2=exec, 3-4=self-emp, 5-6=family/home
    "contract_type": "q19",                          # 1=regular, 2=part, 3=dispatch, 4=contract, 5=shokutaku
    "industry": {2017: "q29", 2018: "q33", 2019: "q30",
                 2020: "q30", 2021: "q30", 2022: "q30",
                 2023: "q30", 2024: "q30", 2025: "q30"},
    "firm_size": {2017: "q30", 2018: "q34", 2019: "q31",
                  2020: "q31", 2021: "q31", 2022: "q31",
                  2023: "q31", 2024: "q31", 2025: "q31"},
    "occupation": {2017: "q31", 2018: "q35", 2019: "q32",
                   2020: "q32", 2021: "q32", 2022: "q32",
                   2023: "q32", 2024: "q32", 2025: "q32"},
    "position": {2017: "q32", 2018: "q36", 2019: "q33",
                 2020: "q33", 2021: "q33", 2022: "q33",
                 2023: "q33", 2024: "q33", 2025: "q33"},
    "weekly_hours": {2017: "q36_2", 2018: "q40_2", 2019: "q37_2",
                     2020: "q37_2", 2021: "q37_2", 2022: "q37_2",
                     2023: "q37_2", 2024: "q37_2", 2025: "q37_2"},
    # --- salary / income (previous calendar year, man-yen) ---------------
    "annual_income": {2017: "q91_1", 2018: "q98_1", 2019: "q100_1",
                      2020: "q94_1", 2021: "q100_1", 2022: "q100_1",
                      2023: "q99_1", 2024: "q99_1", 2025: "q99_1"},
    # --- tenure ----------------------------------------------------------
    "current_job_start_year": {2017: "qn90_11", 2018: "qn97_11", 2019: "qn99_11",
                               2020: "qn93_11", 2021: "qn99_11", 2022: "qn99_11",
                               2023: "qn98_11", 2024: "qn98_11", 2025: "qn98_11"},
    # --- turnover intention (1=active hunt .. 4=no intention) ------------
    "intention": {2017: "q95", 2018: "q106", 2019: "q106",
                  2020: "q100", 2021: "q106", 2022: "q106",
                  2023: "q105", 2024: "q105", 2025: "q105"},
    # --- retrospective job events (past year, MA: 1=selected) ------------
    "ev_quit": {2017: "q50_1", 2018: "q55_1", 2019: "q59_1",
                2020: "q53_1", 2021: "q59_1", 2022: "q57_1",
                2023: "q57_1", 2024: "q58_1", 2025: "q58_1"},
    "ev_started_job": {2017: "q50_2", 2018: "q55_2", 2019: "q59_2",
                       2020: "q53_2", 2021: "q59_2", 2022: "q57_2",
                       2023: "q57_2", 2024: "q58_2", 2025: "q58_2"},
}


def column_for(canonical: str, year: int):
    """Actual CSV column for a canonical variable in a wave, or None if absent."""
    prefix, case, id_col = _STYLE[year]
    spec = _SUFFIX[canonical]
    if isinstance(spec, dict) and spec.get("_raw"):
        return id_col
    if isinstance(spec, dict):
        suffix = spec.get(year)
        if suffix is None:
            return None
    else:
        suffix = spec
    return f"{prefix}{case(suffix)}"


def rename_map(year: int) -> dict:
    """Mapping {actual_column: canonical_name} for renaming a wave's dataframe."""
    out = {}
    for canonical in _SUFFIX:
        col = column_for(canonical, year)
        if col is not None:
            out[col] = canonical
    return out


def canonical_columns() -> list:
    """All canonical variable names produced by the loader."""
    return list(_SUFFIX.keys())
