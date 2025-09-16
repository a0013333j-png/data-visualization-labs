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

**Outputs**
- `output/ai/` : coefficient tables, bar charts with CIs, event-study plots.
