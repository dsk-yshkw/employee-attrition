**Table 2: Next-year attrition prediction, time-based split (test = latest usable wave).**

| Target     | Model    |   Base rate |   ROC-AUC |   PR-AUC |
|:-----------|:---------|------------:|----------:|---------:|
| Separation | logistic |       0.078 |     0.657 |    0.139 |
| Separation | histgbm  |       0.078 |     0.709 |    0.182 |
| Separation | xgboost  |       0.078 |     0.728 |    0.195 |
| Intention  | logistic |       0.188 |     0.646 |    0.281 |
| Intention  | histgbm  |       0.188 |     0.663 |    0.3   |
| Intention  | xgboost  |       0.188 |     0.668 |    0.305 |
