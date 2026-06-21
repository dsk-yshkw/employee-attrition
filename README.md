# Employee Attrition Prediction using JPSED Panel Data

This repository contains code for modeling worker attrition behavior using the Japan Panel Survey of Employment Dynamics (JPSED), provided by the Social Science Japan Data Archive (SSJDA) at the University of Tokyo's Institute of Social Science.

## Overview

We build a machine learning model that predicts attrition probability using worker demographic attributes and salary growth rate as features, applied to longitudinal panel data.

## Data

The raw data used in this study is **not included** in this repository due to the data use agreement with SSJDA and the Act on the Protection of Personal Information (個人情報保護法).

To reproduce results with the original data, please refer to [DATA_ACCESS.md](DATA_ACCESS.md).

A synthetic dataset that mimics the structure and statistical properties of the original data is provided in `data/synthetic/` for code verification purposes.

## Repository Structure

```
employee-attrition/
├── src/
│   ├── data/
│   │   ├── loader.py           # CSV loading and encoding handling
│   │   └── panel_builder.py    # Merge multiple survey waves by PKEY
│   ├── features/
│   │   ├── demographics.py     # Demographic features (age, gender, education, etc.)
│   │   ├── employment.py       # Employment features (type, industry, firm size, etc.)
│   │   └── salary.py           # Salary and salary growth rate computation
│   ├── models/
│   │   ├── attrition.py        # Attrition probability model
│   │   └── evaluator.py        # Evaluation metrics (AUC, precision, recall, etc.)
│   └── config.py               # Variable name mappings and constants
├── data/
│   └── synthetic/
│       ├── generate_synthetic.py   # Synthetic data generation script
│       └── sample_synthetic.csv    # Sample synthetic data (included in repo)
├── notebooks/
│   └── simulation.ipynb        # Google Colab simulation notebook
├── DATA_ACCESS.md              # Instructions for accessing the original JPSED data
├── requirements.txt
└── README.md
```

## Usage

### With synthetic data (no application required)

```python
from src.data.loader import DataLoader
from src.data.panel_builder import PanelBuilder
from src.features.salary import SalaryFeatureBuilder
from src.models.attrition import AttritionModel

loader = DataLoader(data_dir="data/synthetic/")
panel = PanelBuilder(loader).build()
model = AttritionModel()
model.fit(panel)
```

### With original JPSED data

See [DATA_ACCESS.md](DATA_ACCESS.md) for data acquisition steps, then run `notebooks/simulation.ipynb` pointing `DATA_DIR` to your local or Google Drive data path.

## Citation

If you use the original JPSED data in your research, please include the following acknowledgment as required by SSJDA:

> 本研究では、東京大学社会科学研究所附属社会調査・データアーカイブ研究センターSSJデータアーカイブから「全国就業実態パネル調査」（調査番号：SSJDA1088, 1164, 1165, 1227, 1228, 1279, 1280, 1349, 1350, 1429, 1430, 1439, 1440, 1441, 1523, 1524, 1598, 1599, 1730, 1731, 1775, 1776）の個票データの提供を受けました。

## License

Code: MIT License

Data: Subject to SSJDA data use agreement. See [DATA_ACCESS.md](DATA_ACCESS.md).
