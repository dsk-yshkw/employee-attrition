"""Project-wide constants for the JPSED attrition pipeline.

Variable-to-column mapping lives in :mod:`src.variable_map`; this module holds
value-code semantics, target definitions, and feature groupings that build on
the canonical variable names.
"""

from src.variable_map import WAVES  # noqa: F401  (re-exported for convenience)

PKEY = "pkey"

# ---------------------------------------------------------------------------
# Value-code semantics (canonical variables)
# ---------------------------------------------------------------------------

# Q17 employment status in December: codes 1-6 mean "had a job" (working or on
# temporary leave), 7 = job-seeking (unemployed), 8-11 = not in labour force.
EMPLOYED_STATUS_CODES = {1, 2, 3, 4, 5, 6}

# Q18 work style: 1 = employed by a company/organisation (what we call an
# "employee"); 2 = executive, 3-4 = self-employed, 5 = family worker, 6 = home work.
EMPLOYEE_WORK_STYLE = 1

# Q19 contract type: 1 = regular (seiki) employee.
REGULAR_CONTRACT = 1

# Q106/Q105 turnover intention codes.
#   1 = wants to change jobs and is actively job-hunting
#   2 = wants to change jobs but is not job-hunting
#   3 = would like to change jobs eventually
#   4 = has no intention of changing jobs
INTENTION_ACTIVE = {1, 2}      # "active" turnover intention (default label)
INTENTION_ANY = {1, 2, 3}      # any stated intention to eventually move

# Sentinel / non-response codes to convert to NaN, per canonical variable.
# JPSED uses large sentinels for numeric "unknown"/"NA" answers.
MISSING_VALUES = {
    "annual_income": [9999, 99999, 999999],
    "weekly_hours": [999],
    "youngest_child_age": [999],
    "num_children": [99],
    "current_job_start_year": [9999, 99999],
    "age": [999],
}

# ---------------------------------------------------------------------------
# Target definitions
# ---------------------------------------------------------------------------
TARGET_SEPARATION = "attrition_separation"   # actual separation observed at t+1
TARGET_INTENTION = "attrition_intention"     # stated turnover intention at t

# ---------------------------------------------------------------------------
# Feature groupings (canonical names)
# ---------------------------------------------------------------------------
DEMOGRAPHIC_FEATURES = [
    "gender", "age", "education", "has_spouse", "has_child",
    "num_children", "youngest_child_age",
]
EMPLOYMENT_FEATURES = [
    "contract_type", "industry", "firm_size", "occupation",
    "position", "weekly_hours", "tenure_years",
]
SALARY_FEATURES = [
    "annual_income", "prev_annual_income", "salary_growth_rate",
]

# Columns that are categorical (nominal) and should be treated as such by models.
CATEGORICAL_FEATURES = [
    "gender", "contract_type", "industry", "occupation", "position",
]
