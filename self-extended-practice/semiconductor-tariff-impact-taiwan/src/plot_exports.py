#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot Taiwan IC (HS 8542) exports by market (2013–2025) with clean English labels.

Inputs (default repo layout):
- data/raw/taiwan_exports_by_country_2013_2025.csv
- data/mappings/country_name_map_full.json

Outputs:
- data/processed/top10_export_markets_avg_2013_2025.csv
- data/processed/top10_export_markets_trend_2013_2025.csv
- output/interactive/top10_export_markets_bar_race.html  (Plotly: play/pause)
- output/figures/taiwan_ic_top10_trend_en.png             (Matplotlib static)

Usage:
    python src/plot_exports.py \
      --raw data/raw/taiwan_exports_by_country_2013_2025.csv \
      --mapping data/mappings/country_name_map_full.json \
      --outdir output \
      --year-min 2013 --year-max 2025 \
      --exclude-others

Notes:
- Excludes the aggregate bucket "Others" by default (use --include-others to keep it).
- Assumes Export Value is in USD (numeric), Year is 4-digit.
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Dict, List

import pandas as pd

# Plotly for interactive chart, Matplotlib for static
import plotly.express as px
import plotly.io as pio
import matplotlib.pyplot as plt


# -------------------------
# Helpers
# -------------------------

def ensure_dirs(paths: List[Path]) -> None:
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


def load_country_map(path: Path) -> Dict[str, str]:
    with path.open("r", encoding="utf-8") as f:
        mapping = json.load(f)
    # Normalize: strip whitespace on keys/values
    clean = {}
    for k, v in mapping.items():
        clean[(k or "").strip()] = (v or "").strip() or "Others"
    return clean


def ascii_safe(s: str) -> str:
    """Ensure ASCII-only label to avoid font issues in some environments."""
    try:
        s.encode("ascii")
        return s
    except Exception:
        # drop non-ascii (most plot backends can still render unicode, but we keep safe)
        return s.encode("ascii", "ignore").decode("ascii") or "Unknown"


# -------------------------
# Core processing
# -------------------------

def prepare_top10_tables(
    raw_csv: Path,
    mapping_json: Path,
    year_min: int = 2013,
    year_max: int = 2025,
    include_others: bool = False,
    processed_dir: Path = Path("data/processed"),
) -> pd.DataFrame:
    """Return year-country aggregated DataFrame (top10 only) and write processed CSVs."""
    df = pd.read_csv(raw_csv)
    # Normalize columns
    df.columns = [c.strip() for c in df.columns]

    # Required columns check
    required = {"Year", "Country", "HS Code", "Description", "Export Value (USD)"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in {raw_csv}: {sorted(missing)}")

    # Year range filter and numeric cast
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Export Value (USD)"] = pd.to_numeric(df["Export Value (USD)"], errors="coerce")
    df = df.dropna(subset=["Year", "Export Value (USD)"])
    df = df[(df["Year"] >= year_min) & (df["Year"] <= year_max)]

    # Map country names to English
    cmap = load_country_map(mapping_json)
    df["Country_EN"] = df["Country"].map(cmap).fillna("Others")
    df["Country_EN"] = df["Country_EN"].map(ascii_safe)

    # Keep IC only (safety)
    df = df[df["HS Code"].astype(str).str.startswith("8542")].copy()

    # Aggregate to Year x Country
    year_country = (
        df.groupby(["Year", "Country_EN"], as_index=False)["Export Value (USD)"]
          .sum()
          .rename(columns={"Export Value (USD)": "Export_USD"})
    )

    # Compute Top10 by average over years
    avg = (year_country.groupby("Country_EN", as_index=False)["Export_USD"]
           .mean().rename(columns={"Export_USD": "Avg_Exports_2013_2025_USD"}))

    if not include_others:
        avg = avg[avg["Country_EN"].str.lower() != "others"]

    top10 = avg.sort_values("Avg_Exports_2013_2025_USD", ascending=False).head(10)

    # Save avg table
    ensure_dirs([processed_dir])
    avg_out = processed_dir / "top10_export_markets_avg_2013_2025.csv"
    top10.to_csv(avg_out, index=False, encoding="utf-8-sig")

    # Filter year_country for top10
    year_country_top10 = year_country[year_country["Country_EN"].isin(top10["Country_EN"])].copy()
    trend_out = processed_dir / "top10_export_markets_trend_2013_2025.csv"
    year_country_top10.to_csv(trend_out, index=False, encoding="utf-8-sig")

    return year_country_top10


def plot_static_lines(year_country_top10: pd.DataFrame, out_png: Path) -> None:
    pivot = year_country_top10.pivot(index="Year", columns="Country_EN", values="Export_USD").sort_index()
    plt.figure(figsize=(12, 7))
    for c in pivot.columns:
        plt.plot(pivot.index, pivot[c] / 1e9, linewidth=2.0, label=c)
    plt.title("Taiwan IC (HS 8542) Exports — Top 10 Markets Trend (2013–2025)", fontsize=18, pad=12)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Exports (USD, Billions)", fontsize=12)
    plt.grid(True, alpha=0.25)
    plt.legend(title="Market", ncol=2, fontsize=10, title_fontsize=11, frameon=True)
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=200)
    plt.close()


def plot_interactive_bar_race(year_country_top10: pd.DataFrame, out_html: Path) -> None:
    df_sorted = year_country_top10.copy()
    df_sorted["Export_Bn"] = df_sorted["Export_USD"] / 1e9
    df_sorted = df_sorted.sort_values(["Year", "Export_Bn"], ascending=[True, False])

    fig = px.bar(
        df_sorted,
        x="Export_Bn",
        y="Country_EN",
        orientation="h",
        color="Country_EN",
        animation_frame="Year",
        range_x=[0, max(1e-9, df_sorted["Export_Bn"].max()) * 1.1],
        labels={"Export_Bn": "Exports (USD, Billions)", "Country_EN": "Market", "Year": "Year"},
        title="Taiwan IC (HS 8542) Exports — Top 10 Markets (2013–2025)"
    )
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(
        legend_title_text="Market",
        hovermode="closest",
        updatemenus=[
            {
                "type": "buttons",
                "showactive": False,
                "buttons": [
                    {"label": "Play", "method": "animate", "args": [None, {"fromcurrent": True}]},
                    {"label": "Pause", "method": "animate", "args": [[None], {"mode": "immediate"}]}
                ]
            }
        ]
    )
    out_html.parent.mkdir(parents=True, exist_ok=True)
    pio.write_html(fig, file=str(out_html), auto_open=False, include_plotlyjs="cdn")


# -------------------------
# CLI
# -------------------------

def main():
    ap = argparse.ArgumentParser(description="Plot Top10 markets for Taiwan IC exports (2013–2025)")
    ap.add_argument("--raw", type=str, default="data/raw/taiwan_exports_by_country_2013_2025.csv",
                    help="Path to raw country-level exports CSV")
    ap.add_argument("--mapping", type=str, default="data/mappings/country_name_map_full.json",
                    help="Path to CN->EN country mapping JSON")
    ap.add_argument("--processed", type=str, default="data/processed",
                    help="Directory for processed CSV outputs")
    ap.add_argument("--outdir", type=str, default="output",
                    help="Directory for charts (figures/ + interactive/)")
    ap.add_argument("--year-min", type=int, default=2013)
    ap.add_argument("--year-max", type=int, default=2025)
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--include-others", action="store_true", help="Include the 'Others' bucket in Top10 selection")
    grp.add_argument("--exclude-others", action="store_true", help="Exclude the 'Others' bucket (default)")
    args = ap.parse_args()

    include_others = True if args.include_others else False
    if args.exclude_others:
        include_others = False

    raw_csv = Path(args.raw)
    mapping_json = Path(args.mapping)
    processed_dir = Path(args.processed)
    outdir = Path(args.outdir)

    # 1) Build processed top10 tables
    year_country_top10 = prepare_top10_tables(
        raw_csv=raw_csv,
        mapping_json=mapping_json,
        year_min=args.year_min,
        year_max=args.year_max,
        include_others=include_others,
        processed_dir=processed_dir,
    )

    # 2) Static lines
    png_path = outdir / "figures" / "taiwan_ic_top10_trend_en.png"
    plot_static_lines(year_country_top10, png_path)

    # 3) Interactive bar race
    html_path = outdir / "interactive" / "top10_export_markets_bar_race.html"
    plot_interactive_bar_race(year_country_top10, html_path)

    print("\nDone ✅")
    print(f"Processed avg table  : {(processed_dir / 'top10_export_markets_avg_2013_2025.csv').as_posix()}")
    print(f"Processed trend table: {(processed_dir / 'top10_export_markets_trend_2013_2025.csv').as_posix()}")
    print(f"Static PNG           : {png_path.as_posix()}")
    print(f"Interactive HTML     : {html_path.as_posix()}\n")


if __name__ == "__main__":
    main()
