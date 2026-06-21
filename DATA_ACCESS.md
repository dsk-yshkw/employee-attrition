# Data Access Instructions

## Overview

This study uses the **Japan Panel Survey of Employment Dynamics (JPSED / 全国就業実態パネル調査)**, provided by the Social Science Japan Data Archive (SSJDA) at the Institute of Social Science, University of Tokyo.

The raw data is not redistributable under the SSJDA data use agreement and the Act on the Protection of Personal Information. Researchers wishing to replicate this study must independently apply for data access.

## How to Apply

1. Visit the SSJDA data catalog: https://doi.org/10.34500/SSJDA.1088
2. Create an account on the SSJDA portal
3. Submit a data use application for the survey numbers listed below
4. Upon approval, download the CSV files and place them according to the directory structure below

## Survey Numbers Used

| SSJDA No. | Directory |
|-----------|-----------|
| 1088 | `data/raw/1088/` |
| 1164 | `data/raw/1164/` |
| 1165 | `data/raw/1165/` |
| 1227 | `data/raw/1227/` |
| 1228 | `data/raw/1228/` |
| 1279 | `data/raw/1279/` |
| 1280 | `data/raw/1280/` |
| 1349 | `data/raw/1349/` |
| 1350 | `data/raw/1350/` |
| 1429 | `data/raw/1429/` |
| 1430 | `data/raw/1430/` |
| 1439 | `data/raw/1439/` |
| 1440 | `data/raw/1440/` |
| 1441 | `data/raw/1441/` |
| 1523 | `data/raw/1523/` |
| 1524 | `data/raw/1524/` |
| 1598 | `data/raw/1598/` |
| 1599 | `data/raw/1599/` |
| 1730 | `data/raw/1730/` |
| 1731 | `data/raw/1731/` |
| 1775 | `data/raw/1775/` |
| 1776 | `data/raw/1776/` |

## Expected Directory Structure

After downloading, place files as follows:

```
data/
└── raw/
    ├── 1088/
    │   └── japanese/
    │       ├── 1088_ver2019.csv
    │       └── 1088_ver2019 label.txt
    ├── 1164/
    │   └── japanese/
    │       ├── 1164_ver2019.csv
    │       └── 1164_ver2019label.txt
    └── ...
```

## Key Variables

| Variable | Description | Role |
|----------|-------------|------|
| `PKEY` | Respondent ID (common across all waves) | Panel join key |
| `Q1` | Gender | Demographic feature |
| `Q2` | Age | Demographic feature |
| `Q12` | Final education | Demographic feature |
| `Q17` | Employment type (December of previous year) | Employment feature |
| `Q18` | Contract type | Employment feature |
| `Q28` | Industry | Employment feature |
| `Q29` | Firm size | Employment feature |
| `Q30` | Occupation | Employment feature |
| `Q85_1` | Annual income from main job (10,000 JPY) | Salary feature / growth rate |
| `Q46_1` | Quit or resigned from job in past year | **Target variable** |
| `Q43` | Cumulative number of resignations | Supplementary target |
