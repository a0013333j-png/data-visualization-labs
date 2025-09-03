# Semiconductor Tariff Impact on Taiwan — Data Visualization

This project explores the impact of international tariffs and trade flows on Taiwan’s semiconductor industry (HS 8542 — electronic integrated circuits).

## Data Sources

- **Taiwan Customs** — export data of HS 8542 by destination country (2013–2025).
- **UN Comtrade API** — global exports of HS 8542 (Taiwan, China, South Korea, United States).

## Directory Structure
```
self-extended-practice/
└── semiconductor-tariff-impact-taiwan/
├── data/
│ ├── raw/
│ │ └── taiwan_exports_by_country_2013_2025.csv
│ ├── mappings/
│ │ └── country_name_map_full.json
│ └── processed/
│ ├── top10_export_markets_avg_2013_2025.csv
│ ├── top10_export_markets_trend_2013_2025.csv
│ └── ic_exports_comparison.csv
├── output/
│ ├── figures/
│ │ ├── taiwan_ic_top10_trend_en.png
│ │ └── ic_exports_comparison.png
│ └── interactive/
│ ├── taiwan_ic_top12_barchart.html
│ └── ic_exports_comparison.html
└── src/
├── plot_exports.py
└── fetch_and_plot_uncomtrade_comparison.py
```

## Notes

- The **Top 10/Top 12 markets** are **destinations of Taiwan’s IC exports**. Taiwan itself does not appear in these rankings because it is the reporter (exporting country).
- “Others” bucket is excluded by default. Use `--include-others` flag if needed.

## Policy Event Markers

To better understand the relationship between Taiwan’s IC exports and international trade policies, we overlay policy event years as vertical red dashed lines on trend charts.
These markers highlight years when U.S. tariff or semiconductor policy shifts occurred, helping link observed export fluctuations with external trade shocks.

Example years included: 2018 (U.S.–China trade war tariffs), 2019 (expanded tariff list), 2021 (Biden administration review), 2022 (CHIPS Act), 2024–2025 (new semiconductor tariffs on China, announced 2024, effective 2025).

Only verified policy years are marked — not every year.

This ensures visual clarity, avoiding the misinterpretation that events happen annually.

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


### Requirements
```
pandas
requests
matplotlib
plotly
```

