# Semiconductor Tariff Impact on Taiwan — Data Visualization & AI-Demand Regression

This project explores the impact of international tariffs and trade flows on Taiwan’s semiconductor industry (HS 8542 — electronic integrated circuits), and extends the analysis by relating **AI demand** to Taiwan/Global IC exports.

---

## Data Sources

- **Taiwan Customs** — export data of HS 8542 by destination country (2013–2025).
- **UN Comtrade** — monthly/annual exports of HS 8542 (Taiwan, China, South Korea, United States; World partner).
- **AI Demand Proxy (2015–2025)**  
  - **Google Trends**: interest over time for  
    `Artificial Intelligence`, `Machine Learning`, `Generative AI`.  
    We resample to **monthly**, Min–Max scale per keyword (0–100), then average into a single **AI demand index**, and aggregate to **quarterly** for regression.  
  - (Optional) **OECD AI Observatory**: can be added as an alternative proxy.

> **Coverage note:** UN Comtrade monthly data for **2025** may be partial (e.g., through Aug). We default to using **full quarters only** in the regression; now-casting with partial quarters is possible but should be clearly flagged if used.

---


## Directory Structure
```
self-extended-practice/
└── semiconductor-tariff-impact-taiwan/
├── data/
│ ├── raw/
│ │ ├── taiwan_exports_by_country_2013_2025.csv
│ │ └── ic_exports_world_HS8542_202501_202508_uncomtrade.csv # example monthly pull
│ ├── mappings/
│ │ └── country_name_map_full.json
│ └── processed/
│ ├── top10_export_markets_avg_2013_2025.csv
│ ├── top10_export_markets_trend_2013_2025.csv
│ ├── ic_exports_comparison.csv
│ └── ic_with_ai_index.csv # <- merged (quarterly) for regression
│
│ └── ai_demand_index_2015_2025.csv # <- Google Trends monthly index (cached)
│
├── notebooks/
│ ├── online_ic_regression.ipynb
│ └── online_ai_regression.ipynb # <- AI × IC regression (this README section)
│
├── output/
│ ├── figures/
│ │ ├── taiwan_ic_top10_trend_en.png
│ │ └── ic_exports_comparison.png
│ ├── interactive/
│ │ ├── taiwan_ic_top12_barchart.html
│ │ └── ic_exports_comparison.html
│ └── ai/
│ └── ic_vs_ai_quarterly.png # <- regression scatter + OLS fit
│
└── src/
├── plot_exports.py
└── fetch_and_plot_uncomtrade_comparison.py
```

---

## Notes

- The **Top 10/Top 12 markets** are **destinations of Taiwan’s IC exports**. Taiwan itself does not appear in these rankings because it is the reporter (exporting country).
- “Others” bucket is excluded by default. Use `--include-others` if needed.

### Policy Event Markers

To better understand the relationship between Taiwan’s IC exports and international trade policies, we overlay policy event years as vertical red dashed lines on trend charts.
These markers highlight years when U.S. tariff or semiconductor policy shifts occurred, helping link observed export fluctuations with external trade shocks.

- Example years included: 2018 (U.S.–China trade war tariffs), 2019 (expanded tariff list), 2021 (Biden administration review), 2022 (CHIPS Act), 2024–2025 (new semiconductor tariffs on China, announced 2024, effective 2025).
- Only verified policy years are marked — not every year.
- This ensures visual clarity, avoiding the misinterpretation that events happen annually.

---

## New: AI Demand × IC Exports (2015–2025)

### What we do
1. Build (or load cached) **AI demand index** from Google Trends (monthly), then aggregate to **quarterly**.
2. Transform IC exports to **quarterly** totals (World partner; value column prioritizes `fobvalue`, then `cifvalue`).
3. Inner-join by (`year`, `quarter`) → run regressions:
   - **OLS** in levels & `log1p`.
   - **Fixed effects** with `C(year) + C(quarter)` and **HAC** (Newey–West) robust errors.

### Key takeaways (current run)
- **Without fixed effects**: AI index and IC exports co-move (positive, significant) — largely explained by the **shared trend**.
- **With year + quarter fixed effects (HAC)**: the coefficient on the AI index becomes **statistically insignificant**, indicating limited marginal explanatory power for **within-year seasonal deviations** at the current aggregation and proxy.

> Interpretation: At **World aggregate** and with this **Google-Trends proxy**, AI demand captures the long-run uptrend, but adds little incremental signal after absorbing annual and seasonal effects.  
> To sharpen inference, try **lags**, **differences**, **destination/commodity splits**, or **stronger AI proxies** (e.g., GPU shipments/ASP, cloud CAPEX, vendor revenues).

**Outputs**
- Figure: `output/ai/ic_vs_ai_quarterly.png`  
- Merged table (quarterly): `data/processed/ic_with_ai_index.csv`  
- Notebook: `notebooks/online_ai_regression.ipynb`

---

## How to Reproduce

### Taiwan Customs — Top 10/12 Markets

```bash
python src/plot_exports.py \
  --raw data/raw/taiwan_exports_by_country_2013_2025.csv \
  --mapping data/mappings/country_name_map_full.json \
  --processed data/processed \
  --outdir output \
  --year-min 2013 --year-max 2025 \
  --exclude-others
```

Outputs:
 - `data/processed/top10_export_markets_avg_2013_2025.csv`
 - `data/processed/top10_export_markets_trend_2013_2025.csv`
 - `output/figures/taiwan_ic_top10_trend_en.png`
 - `output/interactive/taiwan_ic_top12_barchart.html`

### AI Demand × IC Exports (Notebook)

Open `notebooks/online_ai_regression.ipynb.`
Run Cell 1 → 2 → 3 → 4 (prepares paths, loads IC, builds/loads AI index, merges & regressions).
The notebook uses cached `data/ai_demand_index_2015_2025.csv` if present; otherwise it fetches Google Trends automatically and writes the CSV.
(Optional) Run Cell 5 for Year + Quarter FE with HAC robust errors.

Outputs:
 - `output/ai/ic_vs_ai_quarterly.png`
 - `data/processed/ic_with_ai_index.csv`

### Requirements
```
pandas
requests
matplotlib
plotly
```

