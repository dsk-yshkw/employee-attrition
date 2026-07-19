# 分類ブリッジ修正に伴う原稿差し替え一覧（2026-07, 7/28締切前）

背景：JPSED は2023年調査から業種・職種の分類体系を変更（業種67→76/77、職種
224→214/215）。旧パイプラインは新旧コードを混用していた。公式対応表による
新→旧ブリッジを実装し全数値を再凍結。**中核結果（shortfall 0.083、Table 4
シナリオ、雇用形態別インフレ反応）は不変**。以下は原稿の差し替え箇所。

## Methods に1文追加（変数調和の段落）

> JPSED also reclassified its industry and occupation codes beginning with the
> 2023 wave; we recode the 2023–2025 waves back to the 2017–2022 coding using
> the official correspondence tables supplied with the data.

## Table 2（本文の対応数値も）

| セル | 旧 | 新 |
|---|---|---|
| Sep logistic | 0.657 / 0.139 | **0.665 / 0.142** |
| Sep histgbm | 0.709 / 0.182 | **0.721 / 0.188** |
| Sep xgboost | 0.728 / 0.195 | **0.731 / 0.193** |
| Int logistic | 0.646 / 0.281 | **0.647 / 0.282** |
| Int histgbm | 0.663 / 0.300 | **0.669 / 0.304** |
| Int xgboost | 0.668 / 0.305 | **0.670 / 0.304** |
| Sep MLP | 0.707 / 0.174 | **0.706 / 0.175** |
| Sep GRU | 0.705 / 0.160 | **0.705 / 0.160** |
| Sep Transformer | 0.704 / 0.166 | **0.705 / 0.164** |

§5.1 の文（0.728/0.709/0.657/0.668）も同様に差し替え。なお修正後は
HistGBM(0.721) も全ニューラル(≤0.706) を明確に上回るため、「all trail the
best tree ensemble」→「all trail both tree ensembles」に戻してよい。

## Table 3

| 行 | 旧 | 新 |
|---|---|---|
| Separation ROC-AUC | 0.708 | **0.725** |
| Separation pred/obs | 0.086 / 0.083 | **0.082 / 0.083** |
| Re-employment | 0.703 | **0.704** |
| Wage stayers R²/MAE | 0.786 / 48.744 | **0.790 / 47.954** |
| Wage movers R²/MAE | 0.639 / 71.650 | **0.658 / 70.451** |

§5.5 の "(predicted 0.086 vs observed 0.083)" → **0.082 vs 0.083**。

## Table 4 — 変更なし（小数3桁まで一致）

## Table 5

- shortfall **0.083 (0.005) 不変**（主結果）
- market: 0.121 (0.067) → **0.092 (0.061)**。§5.4 の文をトーンダウン：
  > "The market rate itself enters positively though imprecisely (0.092,
  > SE 0.061), suggestive of procyclical separations."
- own / relative / N / R² 不変

## §5.2 SHAP（＋fig_importance キャプション）

順序変更：tenure ≫ occupation > age > … → **tenure ≫ age > occupation >
industry > contract type > real income**
（新 mean|SHAP|: tenure .498, age .227, occupation .202, industry .146,
contract .140, real income .122）

## §5.3 弾力性（＋§5.7）

- overall ≈0.013 → **≈0.014**
- dispatch ≈0.029 → **≈0.031**（regular ≈0.014 は不変）
- §5.7 の "(0.0132→0.0129)" → **(0.0140→0.0137)**

## §5.4 五分位・§5.6 — 数値変更なし

- lag-most ≈0.10 (新値0.104) vs middle ≈0.06 — 本文・キャプションそのまま可
- §5.6 の 350→296 / COLA 345 / dispatch 0.175→0.207 / contract 0.110→0.121 /
  regular 0.055→0.057 — すべて不変

## Supplementary（Table S2 全面差し替え、Table S1 不変）

| Model | ROC-AUC [95% CI] | Gap to XGBoost [95% CI] |
|---|---|---|
| XGBoost | 0.731 [0.720, 0.741] | — |
| HistGBM | 0.721 [0.711, 0.732] | +0.009 [0.005, 0.013] |
| MLP | 0.706 [0.695, 0.717] | +0.025 [0.018, 0.032] |
| GRU | 0.705 [0.695, 0.716] | +0.025 [0.019, 0.032] |
| Transformer | 0.705 [0.695, 0.715] | +0.026 [0.019, 0.033] |
| Logistic | 0.665 [0.653, 0.676] | +0.066 [0.057, 0.076] |

全ギャップの CI はゼロを除外（本文の主張は維持）。
