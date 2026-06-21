"""
Generate synthetic data that mimics the structure and approximate distributions
of the JPSED panel data. No real respondent records are included.
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

N_RESPONDENTS = 500
WAVES = [1088, 1164, 1227, 1279, 1349, 1429, 1523, 1598, 1730, 1775]


def generate_synthetic_panel(n: int = N_RESPONDENTS, waves: list = WAVES) -> pd.DataFrame:
    pkeys = [f"SYN{i:06d}" for i in range(n)]
    records = []

    for wave_idx, wave in enumerate(waves):
        n_present = int(n * (0.95 ** wave_idx))  # simulate panel attrition
        present_keys = pkeys[:n_present]

        df = pd.DataFrame({"PKEY": present_keys, "wave": wave})

        df["Q1"] = RNG.choice([1, 2], size=n_present, p=[0.55, 0.45])
        df["Q2"] = RNG.integers(20, 65, size=n_present)
        df["Q3_1"] = 2016 - df["Q2"]
        df["Q12"] = RNG.choice([1, 2, 3, 4, 5, 6], size=n_present, p=[0.05, 0.05, 0.05, 0.10, 0.55, 0.20])
        df["Q5"] = RNG.choice([1, 2], size=n_present, p=[0.6, 0.4])
        df["Q6"] = RNG.choice([1, 2], size=n_present, p=[0.5, 0.5])

        df["Q17"] = RNG.choice([1, 2, 3], size=n_present, p=[0.70, 0.20, 0.10])
        df["Q18"] = RNG.choice([1, 2, 3], size=n_present, p=[0.60, 0.25, 0.15])
        df["Q28"] = RNG.integers(1, 20, size=n_present)
        df["Q29"] = RNG.choice([1, 2, 3, 4, 5], size=n_present)
        df["Q30"] = RNG.integers(1, 12, size=n_present)
        df["Q34_1"] = RNG.integers(1, 7, size=n_present)
        df["Q34_2"] = RNG.integers(20, 60, size=n_present).astype(float)
        df["Q35"] = RNG.choice([0, 1, 2, 3], size=n_present, p=[0.5, 0.2, 0.2, 0.1])
        df["Q36"] = RNG.choice([1, 2, 3, 4], size=n_present)
        df["Q40"] = RNG.choice([1, 2, 3, 4, 5], size=n_present)

        base_income = RNG.normal(loc=400, scale=200, size=n_present).clip(50, 2000)
        if wave_idx > 0:
            growth = RNG.normal(loc=0.02, scale=0.08, size=n_present)
            base_income = base_income * (1 + growth)
        df["Q85_1"] = base_income.round().astype(int)

        # Q46_1: attrition ~8% base rate, higher when income growth is negative
        logit = (
            -2.5
            - 0.02 * (df["Q2"] - 40)
            + 0.3 * (df["Q18"] == 2).astype(int)
            - 1.5 * (df["Q35"] >= 2).astype(int)
        )
        prob = 1 / (1 + np.exp(-logit))
        df["Q46_1"] = RNG.binomial(1, prob, size=n_present)

        df["Q43"] = RNG.integers(0, 5, size=n_present)

        records.append(df)

    panel = pd.concat(records, ignore_index=True)
    return panel


if __name__ == "__main__":
    panel = generate_synthetic_panel()
    out_path = "data/synthetic/sample_synthetic.csv"
    panel.to_csv(out_path, index=False)
    print(f"Saved {len(panel)} rows to {out_path}")
    print(panel.head())
