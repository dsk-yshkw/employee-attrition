# Employee Attrition Prediction using JPSED Panel Data

This repository contains code for modeling worker attrition behavior using the Japan Panel Survey of Employment Dynamics (JPSED), provided by the Social Science Japan Data Archive (SSJDA) at the University of Tokyo's Institute of Social Science.

## Overview

We build machine-learning models that predict a worker's probability of leaving
their job **in the following year**, using demographic, household, employment
and salary features from longitudinal panel data. The population is restricted
to **wage/salary employees** (people employed by a company/organisation in
December of the reference year).

Two attrition targets are constructed and compared:

- **Actual separation** (`attrition_separation`) — the worker reports in the
  *next* wave that they quit/left a job during the intervening year
  (JPSED Q57_1 / Q58_1, "仕事を辞めた・退職した"). This is realised behaviour;
  base rate ≈ 8%/yr among employees.
- **Turnover intention** (`attrition_intention`) — the worker states an active
  intention to change jobs in the *current* wave (Q106/Q105 codes 1–2). This is
  stated intent, not behaviour; base rate ≈ 19%.

Models are trained with a **time-based split** (earlier waves → train, latest
usable wave → test) and evaluated with ROC-AUC and PR-AUC. Backends:
logistic regression, scikit-learn `HistGradientBoostingClassifier` (default),
and XGBoost (optional).

### Key implementation note

JPSED renumbers survey questions across years (e.g. annual income is
`y22_q100_1` in 2022 but `y23_q99_1` in 2023). `src/variable_map.py` maps each
concept to the correct per-wave column so the rest of the pipeline uses stable
*canonical* names. The panel currently spans the **2020–2025 waves**
(SSJDA 1349 / 1429 / 1523 / 1598 / 1730 / 1775), which share `pkey`; earlier
waves (2016–2019, uppercase `Y17_`/`PKEY` naming) can be added to reach a
10-year panel.

### Macro / real income

Public Japanese CPI (`data/macro/japan_cpi.csv`, 2020=100, Statistics Bureau of
Japan) is merged onto the panel to deflate nominal income. Because JPSED wave `Y`
reports income for calendar year `Y-1`, income is deflated by CPI of `Y-1`. The
2022–2024 waves show the inflation story clearly: mean **nominal** income rose
(~361→370 man-yen) while mean **real** income *fell* (~361→350). Note that CPI /
inflation / real-income features do **not** improve single-year attrition AUC —
within one test year they are constant or monotonic transforms of nominal
values, so they carry no cross-sectional rank information. Their role is in the
multi-year simulation (inflation scenarios) and the real-wage labor-supply
elasticity, not static prediction. Toggle with `FeatureAssembler(include_macro=...)`.

## Data

The raw data used in this study is **not included** in this repository due to the data use agreement with SSJDA and the Act on the Protection of Personal Information (個人情報保護法).

To reproduce results with the original data, please refer to [DATA_ACCESS.md](DATA_ACCESS.md).

A synthetic dataset that mimics the structure and statistical properties of the original data is provided in `data/synthetic/` for code verification purposes.

## Repository Structure

```
employee-attrition/
├── src/
│   ├── variable_map.py         # Per-wave column map -> canonical variable names
│   ├── config.py               # Value-code semantics, targets, feature groups
│   ├── data/
│   │   ├── loader.py           # Load each wave's CSV, rename to canonical names
│   │   └── panel_builder.py    # Person-year panel + separation/intention labels
│   ├── features/
│   │   ├── demographics.py     # Gender, age, education, spouse, children
│   │   ├── employment.py       # Contract, industry, size, occupation, tenure, hours
│   │   ├── salary.py           # Annual income + year-over-year growth rate
│   │   └── assembler.py        # Combine feature builders into the model matrix
│   ├── models/
│   │   ├── attrition.py        # HistGBM (default) / logistic / xgboost backends
│   │   └── evaluator.py        # AUC, PR-AUC, ROC/PR plots, importance plots
│   └── pipeline.py             # End-to-end experiment (build -> split -> evaluate)
├── data/
│   └── synthetic/
│       ├── generate_synthetic.py   # Synthetic data generator (canonical schema)
│       ├── 2022.csv .. 2025.csv    # Per-wave synthetic files (safe to publish)
│       └── sample_synthetic.csv    # Combined synthetic panel
├── notebooks/
│   ├── attrition_analysis.ipynb    # EDA -> modelling -> evaluation -> comparison
│   └── simulation.ipynb            # Original Colab notebook
├── DATA_ACCESS.md              # Instructions for accessing the original JPSED data
├── requirements.txt
└── README.md
```

## Usage

### Quick start with synthetic data (no application required)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

python data/synthetic/generate_synthetic.py   # writes data/synthetic/<year>.csv
python -m src.pipeline --synthetic             # train + evaluate both targets
```

### With the original JPSED data

```bash
python -m src.pipeline --data-dir "/path/to/JPSED/data"
```

### As a library

```python
from src.data.loader import DataLoader
from src.data.panel_builder import PanelBuilder
from src.features.assembler import FeatureAssembler
from src.pipeline import run_experiment
from src.config import TARGET_SEPARATION

loader = DataLoader("/path/to/JPSED/data")        # or DataLoader("data/synthetic", synthetic=True)
pb, fa = PanelBuilder(loader), FeatureAssembler()

# Train on 2022-2023, test on 2024 (actual next-year separation).
result = run_experiment(pb, fa, TARGET_SEPARATION, test_year=2024, model_type="histgbm")
print(result.metrics["auc_roc"], result.importance.sort_values().tail(5))
```

## Results (original JPSED data, 2020–2025 panel)

Time-based split; employees only (train ≤ test_year-1). Separation test = 2024,
intention test = 2025. Indicative numbers from the current pipeline:

| Target | Model | Base rate | ROC-AUC | PR-AUC |
|---|---|---|---|---|
| Actual separation (next year) | Logistic | 0.08 | 0.65 | 0.14 |
| Actual separation (next year) | HistGBM | 0.08 | 0.70 | 0.18 |
| Actual separation (next year) | XGBoost | 0.08 | 0.73 | 0.19 |
| Turnover intention | Logistic | 0.19 | 0.65 | 0.28 |
| Turnover intention | HistGBM | 0.19 | 0.66 | 0.30 |
| Turnover intention | XGBoost | 0.19 | 0.67 | 0.31 |

Macro (CPI / real-income) features leave single-year AUC essentially unchanged
(±0.002) for the reason given under [Macro / real income](#macro--real-income).

Top predictors of actual separation: **tenure**, **age**, **annual income**,
**contract type** (regular vs non-regular). Raw salary growth rate contributes
little; see the note below.

### Note on "salary growth excluding scheduled raises"

JPSED does not record a base-pay vs. scheduled-increment (定期昇給) breakdown, so
`salary_growth_rate` is the raw year-over-year change and mixes scheduled raises
with promotions, job changes and hours changes. It is included as a
relative-change signal, with this limitation documented in `src/features/salary.py`.

> `HistGradientBoostingClassifier` is the default so the pipeline runs without
> native dependencies. XGBoost is optional; on macOS it needs OpenMP
> (`brew install libomp`).

### With original JPSED data

See [DATA_ACCESS.md](DATA_ACCESS.md) for data acquisition steps, then run `notebooks/simulation.ipynb` pointing `DATA_DIR` to your local or Google Drive data path.

## Citation

If you use the original JPSED data in your research, please include the following acknowledgment as required by SSJDA:

> 本研究では、東京大学社会科学研究所附属社会調査・データアーカイブ研究センターSSJデータアーカイブから「全国就業実態パネル調査」（調査番号：SSJDA1088, 1164, 1165, 1227, 1228, 1279, 1280, 1349, 1350, 1429, 1430, 1439, 1440, 1441, 1523, 1524, 1598, 1599, 1730, 1731, 1775, 1776）の個票データの提供を受けました。

## License

Code: MIT License

Data: Subject to SSJDA data use agreement. See [DATA_ACCESS.md](DATA_ACCESS.md).
