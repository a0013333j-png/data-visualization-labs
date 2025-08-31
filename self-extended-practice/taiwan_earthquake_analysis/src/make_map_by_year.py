from __future__ import annotations
from pathlib import Path
import json, re
import pandas as pd
import folium
from branca.element import Element

# ---------- helpers ----------
def _pick(df: pd.DataFrame, candidates: list[str]) -> str | None:
    m = {str(c).lower(): c for c in df.columns}
    for k in candidates:
        if str(k).lower() in m:
            return m[str(k).lower()]
    return None

def _infer_time_from_row(row: pd.Series) -> str | None:
    for v in row.values:
        s = (v if isinstance(v, str) else str(v)).strip()
        if re.match(r"^\d{4}[-/]\d{2}[-/]\d{2}[ T]\d{2}:\d{2}:\d{2}$", s):
            return s
    date_s, time_s = None, None
    for v in row.values:
        s = (v if isinstance(v, str) else str(v)).strip()
        if re.match(r"^\d{8}$", s):  # YYYYMMDD
            date_s = s
        if re.match(r"^\d{6}$", s) or re.match(r"^\d{2}:\d{2}:\d{2}$", s):
            time_s = s
    if date_s and time_s:
        y, m, d = date_s[:4], date_s[4:6], date_s[6:8]
        hhmmss = time_s if ":" in time_s else f"{time_s[:2]}:{time_s[2:4]}:{time_s[4:6]}"
        return f"{y}-{m}-{d} {hhmmss}"
    for k, v in row.items():
        if str(k).lower() in {"datetime", "origintime", "eventtime", "time"}:
            s = (v if isinstance(v, str) else str(v)).strip().replace("T", " ").replace("/", "-")
            if re.match(r".*\d{6}$", s):
                s = re.sub(r"(\d{2})(\d{2})(\d{2})$", r"\1:\2:\3", s)
            return s
    return None

# ---------- load JSON ----------
def _load_quakes(json_path: str | Path) -> pd.DataFrame:
    p = Path(json_path)
    with p.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    # CWA E-A0073-001
    if isinstance(raw, dict) and "cwaopendata" in raw:
        catalog = raw.get("cwaopendata", {}).get("Dataset", {}).get("Catalog", {})
        eq_list = catalog.get("EarthquakeInfo")
        if not isinstance(eq_list, list):
            return pd.DataFrame(columns=["time","lat","lon","depth","mag","year"])
        df = pd.DataFrame(eq_list).rename(columns={
            "OriginTime": "time",
            "EpicenterLongitude": "lon",
            "EpicenterLatitude": "lat",
            "FocalDepth": "depth",
            "LocalMagnitude": "mag",
        })
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        for c in ["lon","lat","depth","mag"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

    # GDMS（header + body）
    elif isinstance(raw, dict) and {"header","body"} <= set(raw.keys()):
        header, body = raw["header"], raw["body"]
        if not isinstance(header, list) or not isinstance(body, list) or not body:
            return pd.DataFrame(columns=["time","lat","lon","depth","mag","year"])
        first = body[0]
        if isinstance(first, (list, tuple)):
            max_len = max(len(r) for r in body)
            cols = [str(h) for h in header][:max_len]
            if len(cols) < max_len:
                cols += [f"col_{i}" for i in range(len(cols), max_len)]
            body_fixed = [list(r) + [None]*(max_len-len(r)) for r in body]
            df = pd.DataFrame(body_fixed, columns=cols)
        else:
            df = pd.DataFrame(body)

        date_col = _pick(df, ["date","日期"])
        time_col = _pick(df, ["time","時間"])
        dt_col   = _pick(df, ["datetime","origintime","eventtime","發震時刻","time"])
        if date_col and time_col:
            ts = pd.to_datetime(
                df[date_col].astype(str).str.strip()+" "+df[time_col].astype(str).str.strip(),
                errors="coerce"
            )
        elif dt_col:
            ts = pd.to_datetime(df[dt_col].astype(str).str.strip().str.replace("T"," ", regex=False), errors="coerce")
        else:
            ts = pd.to_datetime(df.apply(_infer_time_from_row, axis=1), errors="coerce")
        df["time"] = ts

        lat_col = _pick(df, ["lat","latitude","緯度","y","震央緯度"])
        lon_col = _pick(df, ["lon","longitude","經度","x","震央經度"])
        dep_col = _pick(df, ["depth","focaldepth","深度"])
        mag_col = _pick(df, ["mag","magnitude","規模","ML","Mw"])
        rename = {}
        if lat_col: rename[lat_col] = "lat"
        if lon_col: rename[lon_col] = "lon"
        if dep_col: rename[dep_col] = "depth"
        if mag_col: rename[mag_col] = "mag"
        df = df.rename(columns=rename)
        for c in ["lat","lon","depth","mag"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        keep = ["time","lat","lon"] + [c for c in ["depth","mag"] if c in df.columns]
        df = df[keep]
    else:
        return pd.DataFrame(columns=["time","lat","lon","depth","mag","year"])

    df = df.dropna(subset=["time","lat","lon"]).copy()
    df["year"] = pd.to_datetime(df["time"]).dt.year
    return df.sort_values("time").reset_index(drop=True)

# ---------- interactive map ----------
def make_interactive_map(json_path: str, outfile: str = "release/index.html"):
    df = _load_quakes(json_path)

    years = sorted(df["year"].dropna().unique())
    print(f"[INFO] records={len(df)}, years={years}")

    # 建立 folium 地圖
    m = folium.Map(location=[23.7, 121], zoom_start=7, tiles="CartoDB positron")

    # 建立下拉選單
    year_selector = folium.map.CustomPane("year_selector")
    m.add_child(year_selector)

    feature_groups = {}
    for year in years:
        fg = folium.FeatureGroup(name=str(year), show=(year == years[0]))
        yearly = df[df["year"] == year]

        for _, r in yearly.iterrows():
            folium.CircleMarker(
                location=[r["lat"], r["lon"]],
                radius=3 + float(r["mag"]) if pd.notna(r["mag"]) else 3,
                color="red" if r["depth"] > 70 else "blue",
                fill=True,
                fill_opacity=0.6,
                popup=(
                    f"時間：{pd.to_datetime(r['time']).strftime('%Y-%m-%d %H:%M:%S')}<br>"
                    f"規模：{r['mag'] if pd.notna(r['mag']) else '—'}<br>"
                    f"深度：{r['depth']} km"
                ),
            ).add_to(fg)

        fg.add_to(m)
        feature_groups[year] = fg

    folium.LayerControl(collapsed=False).add_to(m)

    # 🚩固定輸出檔案名稱為 index.html
    m.save(outfile)
    print(f"[OK] 互動地圖輸出：{outfile}")

