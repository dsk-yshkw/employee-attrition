# Macro data sources

## japan_cpi.csv — Japan Consumer Price Index (national)

- **Series**: Consumer Price Index, all-Japan, annual average, **2020 base (2020=100)**,
  fixed-base (原数値) index — the headline series.
  - `cpi_all_items` — 総合 (all items)
  - `cpi_core` — 生鮮食品を除く総合 (all items less fresh food)
  - `inflation_all_items`, `inflation_core` — year-over-year % change of the above.
- **Source**: 総務省統計局『2020年基準 消費者物価指数 全国』表7（年平均・原数値）.
  Statistics Bureau of Japan, Consumer Price Index (CPI), 2020-base, national,
  annual averages. https://www.stat.go.jp/data/cpi/
- **Retrieved**: 2026-07 from the official annual report PDF
  (`.../cpi/sokuhou/nen/pdf/zen-n.pdf`, 表7).
- **Note**: A separate *chain-linked Laspeyres reference index* (ラスパイレス連鎖基準,
  参考指数) exists and gives slightly different values (e.g. 2023 = 105.8 vs 105.6);
  we use the primary fixed-base headline index. Verify against e-Stat before final
  publication if exact decimals matter.

### Timing convention for the panel merge

JPSED wave `Y` (survey year) reports income for **calendar year `Y-1`**. So a
worker's nominal income in wave `Y` is deflated by the CPI of year `Y-1`, and the
real income growth between waves `Y-1` and `Y` subtracts the inflation of year
`Y-1` (relative to `Y-2`). See `src/data/macro.py`.
