**Table 2: Next-year attrition prediction, time-based split (test = latest usable wave).**

| Target     | Model    |   Base rate |   ROC-AUC |   PR-AUC |
|:-----------|:---------|------------:|----------:|---------:|
| Separation | logistic |       0.078 |     0.665 |    0.142 |
| Separation | histgbm  |       0.078 |     0.721 |    0.188 |
| Separation | xgboost  |       0.078 |     0.731 |    0.193 |
| Intention  | logistic |       0.188 |     0.647 |    0.282 |
| Intention  | histgbm  |       0.188 |     0.669 |    0.304 |
| Intention  | xgboost  |       0.188 |     0.67  |    0.304 |
