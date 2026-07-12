# Macro data — sources & citation (for the paper)

## Consumer Price Index (`japan_cpi.csv`)

**Publisher**: Statistics Bureau of Japan, Ministry of Internal Affairs and
Communications (総務省統計局).
**Dataset**: Consumer Price Index (消費者物価指数, CPI), 2020-base (2020=100),
all-Japan, **annual average, fixed-base headline index (原数値)**.
Series used: 総合 (all items) and 生鮮食品を除く総合 (all items less fresh food),
with year-over-year percentage change. Coverage 2013–2025.

### Links

- CPI top page (portal for all CPI results):
  https://www.stat.go.jp/data/cpi/
- CPI results index (時系列・結果):
  https://www.stat.go.jp/data/cpi/1.html
- Annual-average summary (最新の年平均結果の概要):
  https://www.stat.go.jp/data/cpi/sokuhou/nen/index-z.html
- Annual report PDF actually used (表7 年平均・原数値, 全国):
  https://www.stat.go.jp/data/cpi/sokuhou/nen/pdf/zen-n.pdf
- e-Stat machine-readable tables (政府統計の総合窓口):
  https://www.e-stat.go.jp/stat-search/files?toukei=00200573
- e-Stat CPI 2020-base table view:
  https://www.e-stat.go.jp/dbview?sid=0003427113

**Retrieved**: 2026-07. Values transcribed from 表7 of the official annual PDF.

### Note on index variants

The Statistics Bureau also publishes a **chain-linked Laspeyres reference index**
(ラスパイレス連鎖基準方式・参考指数), which gives slightly different figures
(e.g. 2023 = 105.8 vs. the headline 105.6). This file uses the **primary
fixed-base headline index**. For final publication, re-download the exact table
from e-Stat and confirm the decimals.

### Suggested citation

- 日本語: 総務省統計局「2020年基準 消費者物価指数（全国）」（年平均・総合），
  https://www.stat.go.jp/data/cpi/ （2026年7月取得）.
- English: Statistics Bureau of Japan, *Consumer Price Index (2020-base),
  Japan, annual average, all items*, https://www.stat.go.jp/data/cpi/
  (retrieved July 2026).

> When reusing this data, the Statistics Bureau requests a source attribution
> (e.g. 「出典：総務省『消費者物価指数』」).

## Nominal wage growth (`japan_wage_growth.csv`)

- **Series**: total cash earnings (現金給与総額), year-over-year % change,
  all surveyed industries (調査産業計), establishments with 5+ employees, all
  employment types (就業形態計). This is the *society-wide* market wage growth used
  as the external reference for the relative-wage analysis.
- **Publisher**: Ministry of Health, Labour and Welfare (厚生労働省),
  Monthly Labour Survey (毎月勤労統計調査).
- **Source**: 毎月勤労統計調査 令和6年分結果速報, 付表（前年比の推移, 調査産業計）.
  https://www.mhlw.go.jp/toukei/itiran/roudou/monthly/r06/24cp/dl/pdf24cp.pdf
  (annual all-industry series 2017–2024; 2016 = +0.5 from prior releases).
- Survey top page: https://www.mhlw.go.jp/toukei/list/30-1a.html
- e-Stat industry-level wage index (for the industry×year refinement):
  https://www.e-stat.go.jp/stat-search/database?statdisp_id=0003030699
- **Retrieved**: 2026-07.
- **Note (relevant to the paper)**: MHLW cautions that this wage growth mainly
  reflects *base-up* (ベースアップ) and is less sensitive to individual *scheduled
  increments* (定期昇給). Establishment-based; not directly comparable to JPSED's
  individual annual income, so treat as a market/reference trend, not a level.
  Industry×year growth (JSIC major divisions) is available from the same survey
  and is the planned refinement of the year-level society-wide reference here.

### Suggested citation (wage)

- 日本語: 厚生労働省「毎月勤労統計調査」（現金給与総額 前年比・調査産業計），
  https://www.mhlw.go.jp/toukei/list/30-1a.html （2026年7月取得）.
- English: Ministry of Health, Labour and Welfare, *Monthly Labour Survey
  (total cash earnings, year-on-year change, all industries)*,
  https://www.mhlw.go.jp/toukei/list/30-1a.html (retrieved July 2026).
