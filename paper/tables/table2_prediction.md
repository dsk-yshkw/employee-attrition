**Table 2: Next-year attrition prediction under the time-based split (separation test = 2024, intention test = 2025). Neural sequence models (MLP on the current state; GRU and Transformer on up-to-8-wave histories) are evaluated on the separation target: access to history does not improve on the current-state MLP, and all trail the tree ensembles.**

| Target     | Model                 |   Base rate |   ROC-AUC |   PR-AUC |
|:-----------|:----------------------|------------:|----------:|---------:|
| Separation | logistic              |       0.078 |     0.665 |    0.142 |
| Separation | histgbm               |       0.078 |     0.721 |    0.188 |
| Separation | xgboost               |       0.078 |     0.731 |    0.193 |
| Separation | MLP (current state)   |       0.078 |     0.706 |    0.175 |
| Separation | GRU (history)         |       0.078 |     0.705 |    0.16  |
| Separation | Transformer (history) |       0.078 |     0.705 |    0.164 |
| Intention  | logistic              |       0.188 |     0.647 |    0.282 |
| Intention  | histgbm               |       0.188 |     0.669 |    0.304 |
| Intention  | xgboost               |       0.188 |     0.67  |    0.304 |
