# Data sources (for the paper)

Consolidated list of every dataset used, with links and suggested citations.
Primary microdata is licensed and **not** redistributed here; the external
official statistics below (CPI, wages) are public and bundled under `data/macro/`.

Retrieved: July 2026. For the camera-ready, re-download and re-verify decimals
from the machine-readable e-Stat tables where noted.

---

## 1. Primary microdata — JPSED (licensed, not in repo)

- **Dataset**: 全国就業実態パネル調査 (Japan Panel Survey of Employment Dynamics,
  JPSED), Recruit Works Institute.
- **Provider / access**: 東京大学社会科学研究所附属社会調査・データアーカイブ研究
  センター SSJ データアーカイブ (SSJDA), University of Tokyo, Institute of Social
  Science. https://csrda.iss.u-tokyo.ac.jp/
- **SSJDA survey numbers used**: 1164, 1227, 1279, 1349, 1429, 1523, 1598, 1730,
  1775 (main survey waves 2017–2025) and the paired attrition-weight datasets
  1430, 1524, 1731, 1776.
- **Required acknowledgment** (Japanese): 「本研究では、東京大学社会科学研究所附属
  社会調査・データアーカイブ研究センターSSJデータアーカイブから『全国就業実態パネル
  調査』（寄託者：リクルートワークス研究所）の個票データの提供を受けました。」

## 2. Consumer Price Index — `data/macro/japan_cpi.csv`

- **Series**: 消費者物価指数 (CPI), all-Japan, annual average, 2020-base, fixed-base
  headline index (総合 and 生鮮食品を除く総合), with YoY %. 2013–2025.
- **Publisher**: 総務省統計局 (Statistics Bureau of Japan).
- **Links**:
  - CPI portal: https://www.stat.go.jp/data/cpi/
  - Annual results: https://www.stat.go.jp/data/cpi/sokuhou/nen/index-z.html
  - Annual report PDF used (表7): https://www.stat.go.jp/data/cpi/sokuhou/nen/pdf/zen-n.pdf
  - e-Stat table: https://www.e-stat.go.jp/dbview?sid=0003427113
- **Citation**: 総務省統計局「2020年基準 消費者物価指数（全国）」, https://www.stat.go.jp/data/cpi/ (2026年7月取得).

## 3. Society-wide nominal wage growth — `data/macro/japan_wage_growth.csv`

- **Series**: 現金給与総額 (total cash earnings), YoY %, all surveyed industries
  (調査産業計), establishments with 5+ employees, all employment types. 2016–2024.
- **Publisher**: 厚生労働省 (MHLW), 毎月勤労統計調査 (Monthly Labour Survey).
- **Links**:
  - Survey portal: https://www.mhlw.go.jp/toukei/list/30-1a.html
  - Annual report PDF used (付表, 令和6年速報): https://www.mhlw.go.jp/toukei/itiran/roudou/monthly/r06/24cp/dl/pdf24cp.pdf
  - e-Stat wage-index DB: https://www.e-stat.go.jp/stat-search/database?statdisp_id=0003030699
- **Citation**: 厚生労働省「毎月勤労統計調査」（現金給与総額 前年比・調査産業計）, https://www.mhlw.go.jp/toukei/list/30-1a.html (2026年7月取得).

## 4. Industry×year nominal wage growth — `data/macro/japan_wage_growth_industry.csv`

- **Series**: 現金給与総額 YoY % by **JSIC major division** (16 industries),
  就業形態計, 5+ employees. 2021–2024 (used as the market reference for the
  relative-wage analysis; matched to JPSED industries via `src/features/industry_map.py`).
- **Publisher / links**: same as §3 (MHLW Monthly Labour Survey). Per-year annual
  reports (industry earnings table): e.g. 令和5年 https://www.mhlw.go.jp/toukei/itiran/roudou/monthly/r05/23cp/dl/pdf23cp.pdf ,
  令和4年 …/r04/22cp/dl/pdf22cp.pdf , 令和3年 …/r03/21cp/dl/pdf21cp.pdf .
- **Full time series** (all industries, all years) via e-Stat DB
  statdisp_id=0003030699 (産業別賃金指数（現金給与総額）年平均).

### Notes relevant to interpretation

- MHLW wage growth mainly reflects **base-up (ベースアップ)** and is *less* sensitive
  to individual **scheduled increments (定期昇給)** — relevant to the "salary growth
  excluding scheduled raises" framing.
- MHLW figures are establishment-based and not directly comparable in *level* to
  JPSED individual annual income; used here only as a market/reference **trend**.
- JPSED annual income is coarse (median YoY change ≈ 0), so individual wage-growth
  measures are noisy.
