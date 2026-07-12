"""Generate synthetic JPSED-like panel data with canonical column names.

Produces one CSV per survey year (``2022.csv`` .. ``2025.csv``) plus a combined
``sample_synthetic.csv``. Columns use the canonical variable names emitted by
the real loader, and encode a realistic relationship between worker attributes
and next-year separation so the modelling code exercises end to end. No real
respondent records are used.

Run:  python data/synthetic/generate_synthetic.py
"""

import os
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
YEARS = [2022, 2023, 2024, 2025]
N = 4000


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def generate() -> dict:
    # Person-level fixed attributes.
    pkey = np.arange(1, N + 1)
    gender = RNG.choice([1, 2], size=N, p=[0.55, 0.45])
    age0 = RNG.integers(20, 60, size=N)
    education = RNG.choice([2, 3, 4, 5, 6, 7], size=N, p=[0.05, 0.10, 0.15, 0.50, 0.15, 0.05])
    contract = RNG.choice([1, 2, 3, 4, 5], size=N, p=[0.60, 0.20, 0.08, 0.09, 0.03])
    industry = RNG.integers(1, 18, size=N)
    occupation = RNG.integers(1, 13, size=N)
    firm_size = RNG.choice([1, 2, 3, 4, 5, 6, 7], size=N)
    tenure0 = np.minimum(RNG.integers(0, 30, size=N), age0 - 18).clip(0, None)
    income0 = RNG.normal(420, 180, size=N).clip(80, 1800)

    tenure = tenure0.astype(float)
    income = income0.copy()
    has_spouse = RNG.random(N) < _sigmoid((age0 - 30) / 8)
    has_child = has_spouse & (RNG.random(N) < 0.7)

    # ev_quit at wave Y refers to a separation that happened during Y-1, i.e. it
    # is the *label* for the previous wave. We simulate the quit decision from a
    # wave's own features and record it in the following wave's ev_quit.
    quit_prev = np.zeros(N, dtype=int)  # quit reported at the current wave

    waves = {}
    for i, year in enumerate(YEARS):
        age = age0 + i
        growth = RNG.normal(0.015, 0.06, size=N)
        income = (income * (1 + growth)).clip(80, 3000)

        # Latent separation propensity from this wave's situation.
        logit = (
            -2.3
            - 0.55 * np.log1p(tenure)          # long tenure -> stay
            - 0.015 * (age - 40)               # older -> stay
            + 0.9 * (contract != 1)            # non-regular -> leave
            - 0.0008 * (income - 420)          # higher pay -> stay
            - 2.0 * np.clip(growth, -0.3, 0.3)  # raises -> stay
        )
        p_quit = _sigmoid(logit)
        quit_this_year = RNG.binomial(1, p_quit)  # separation during `year`

        # Stated turnover intention correlates with the same drivers (younger,
        # non-regular, short-tenure, low raises are more likely to want to move).
        p_intent = _sigmoid(logit + 1.4)
        wants_move = RNG.binomial(1, p_intent)
        # Map to codes 1-4: movers -> active (1/2), stayers -> passive (3/4).
        intention_code = np.where(
            wants_move == 1,
            RNG.choice([1, 2], size=N, p=[0.4, 0.6]),
            RNG.choice([3, 4], size=N, p=[0.35, 0.65]),
        )

        df = pd.DataFrame({
            "pkey": pkey,
            "gender": gender,
            "age": age,
            "birth_year": year - 1 - age,
            "education": education,
            "has_spouse_raw": np.where(has_spouse, 1, 2),
            "has_child_raw": np.where(has_child, 1, 2),
            "num_children": np.where(has_child, RNG.integers(1, 4, size=N), 0),
            "youngest_child_age": np.where(has_child, RNG.integers(0, 20, size=N), np.nan),
            "emp_status": 1,                        # employed in December
            "work_style": 1,                        # employee (kept in-scope)
            "contract_type": contract,
            "industry": industry,
            "firm_size": firm_size,
            "occupation": occupation,
            "position": RNG.choice([1, 2, 3, 8], size=N, p=[0.1, 0.15, 0.2, 0.55]),
            "weekly_hours": RNG.normal(40, 8, size=N).clip(10, 70).round(),
            "annual_income": income.round().astype(int),
            "current_job_start_year": (year - 1 - tenure).round().astype(int),
            "intention": intention_code,
            "ev_quit": quit_prev,                   # separation during year-1
            "ev_started_job": quit_prev,            # simplistic: rejoined
        })
        waves[year] = df

        # Advance state into next wave: quitters reset tenure, others accrue.
        moved = quit_this_year == 1
        tenure = np.where(moved, 0.0, tenure + 1)
        income = np.where(moved, income * RNG.normal(1.0, 0.15, size=N), income)
        quit_prev = quit_this_year

    return waves


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    waves = generate()
    for year, df in waves.items():
        df.to_csv(os.path.join(out_dir, f"{year}.csv"), index=False)
    combined = pd.concat([d.assign(year=y) for y, d in waves.items()], ignore_index=True)
    combined.to_csv(os.path.join(out_dir, "sample_synthetic.csv"), index=False)
    print(f"Wrote {len(waves)} wave files + sample_synthetic.csv ({len(combined)} rows) to {out_dir}")


if __name__ == "__main__":
    main()
