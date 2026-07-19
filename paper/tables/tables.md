**Table 1: Sample size and attrition base rates by wave (employees).**

|   Year |   Employees | Separation rate   |   Intention rate |
|-------:|------------:|:------------------|-----------------:|
|   2017 |       31531 | 0.088             |            0.224 |
|   2018 |       32969 | 0.089             |            0.201 |
|   2019 |       42646 | 0.085             |            0.203 |
|   2020 |       38294 | 0.085             |            0.197 |
|   2021 |       36904 | 0.079             |            0.183 |
|   2022 |       37050 | 0.082             |            0.184 |
|   2023 |       36924 | 0.083             |            0.195 |
|   2024 |       36922 | 0.078             |            0.191 |
|   2025 |       36898 | —                 |            0.188 |


**Table 2: Next-year attrition prediction, time-based split (test = latest usable wave).**

| Target     | Model    |   Base rate |   ROC-AUC |   PR-AUC |
|:-----------|:---------|------------:|----------:|---------:|
| Separation | logistic |       0.078 |     0.665 |    0.142 |
| Separation | histgbm  |       0.078 |     0.721 |    0.188 |
| Separation | xgboost  |       0.078 |     0.731 |    0.193 |
| Intention  | logistic |       0.188 |     0.647 |    0.282 |
| Intention  | histgbm  |       0.188 |     0.669 |    0.304 |
| Intention  | xgboost  |       0.188 |     0.67  |    0.304 |


**Table 3: Transition sub-model validation (test = 2023).**

| Sub-model      | Metric        | Value         |
|:---------------|:--------------|:--------------|
| Separation     | ROC-AUC       | 0.725         |
| Separation     | pred/obs rate | 0.082 / 0.083 |
| Re-employment  | ROC-AUC       | 0.704         |
| Wage (stayers) | R^2           | 0.79          |
| Wage (stayers) | MAE (man-yen) | 47.954        |
| Wage (movers)  | R^2           | 0.658         |
| Wage (movers)  | MAE (man-yen) | 70.451        |


**Table 4: Microsimulation scenarios (cohort 2021, 4 years).**

| Scenario         |   End attrition |   Cumulative attrition |   End real income |
|:-----------------|----------------:|-----------------------:|------------------:|
| Baseline         |           0.076 |                  0.317 |             349.7 |
| +2pp inflation   |           0.078 |                  0.321 |             321.9 |
| +4pp inflation   |           0.077 |                  0.32  |             296.4 |
| +4pp + full COLA |           0.076 |                  0.317 |             344.6 |
| Min wage (200)   |           0.077 |                  0.319 |             370.7 |


**Table 5: Linear probability models of separation on wage growth relative to the industry market (cluster-robust SE by person in parentheses).**

| Term                    | (1) own       | (2) own+market   | (3) relative   | (4) shortfall   |
|:------------------------|:--------------|:-----------------|:---------------|:----------------|
| Own wage growth         | 0.002 (0.001) | 0.002 (0.001)    |                |                 |
| Market wage growth      |               | 0.092 (0.061)    |                |                 |
| Relative (own-market)   |               |                  | 0.002 (0.001)  |                 |
| Shortfall (market-own)+ |               |                  |                | 0.083 (0.005)   |
| Year FE                 | Yes           | Yes              | Yes            | Yes             |
| N                       | 147,949       | 147,949          | 147,949        | 147,949         |
| R^2                     | 0.000         | 0.000            | 0.000          | 0.002           |


