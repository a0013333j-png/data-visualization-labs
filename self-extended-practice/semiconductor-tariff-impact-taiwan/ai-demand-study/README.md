# AI Demand & Taiwan IC Exports (HS8542)

**Goal**  
Quantify how the post-2023 AI demand boom relates to Taiwan’s HS8542 exports, using public AI-proxy signals and two-way fixed effects / event study.

**Data Sources (external/)**
- GPU shipments / revenue (e.g., vendor earnings decks)
- Hyperscaler AI/CapEx (company 10-K/10-Q, investor decks)
- AI server shipments (market research summaries)
- Optional: AI-related keywords trends (Google Trends), data center power additions, etc.

**Method**
- Align AI signals to quarterly/yearly frequency; log/standardize.
- Merge with 2013–2025 HS8542 exports (TW/US/CN/KR).
- Baselines:  
  - TWFE with Year & Country FE + AI signal (global)  
  - TWFE with `Taiwan × AI_signal` interaction to test relative effect  
  - Placebo & pre-trend checks (event study around 2023H2)

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

