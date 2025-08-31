# src/make_map_by_year.py
from __future__ import annotations
from pathlib import Path
import json
import re
import pandas as pd
import folium
from branca.element import Element


# -------------------------------
# 小工具：欄名/時間欄位推斷
# -------------------------------
def _pick(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """在 df 欄名中，找出第一個存在的候選名稱（不分大小寫）。"""
    lower_map = {str(c).lower(): c for c in df.columns}
    for k in candidates:
        if k.lower() in lower_map:
            return lower_map[k.lower()]
    return None


def _infer_time_from_row(row: pd.Series) -> str | None:
    """
    嘗試從一列中推斷出可 parse 的時間字串。
    支援：
    - 完整 datetime (YYYY-MM-DD HH:MM:SS 或含 T / /)
    - date(YYYYMMDD) + time(HHMMSS 或 HH:MM:SS)
    - 欄名含 datetime / time / originTime / eventTime
    """
    # 1) 直接有完整 datetime 的情況
    for v in row.values:
        s = (v if isinstance(v, str) else str(v)).strip()
        if re.match(r"^\d{4}[-/]\d{2}[-/]\d{2}[ T]\d{2}:\d{2}:\d{2}$", s):
            return s.replace("T", " ").replace("/", "-")

    # 2) 分離的 date/time
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

    # 3) 可能藏在特定欄
    for k, v in row.items():
        if str(k).lower() in {"datetime", "origintime", "eventtime", "time"}:
            s = (v if isinstance(v, str) else str(v)).strip()
            s = s.replace("T", " ").replace("/", "-")
            # 若尾巴是 HHMMSS，補上冒號
            if re.search(r"\d{6}$", s) and not re.search(r"\d{2}:\d{2}:\d{2}$", s):
                s = re.sub(r"(\d{2})(\d{2})(\d{2})$", r"\1:\2:\3", s)
            return s
    return None


# -------------------------------
# 只支援 GDMS Catalog：讀檔 → DataFrame
# -------------------------------
def _load_quakes_from_gdms(json_path: str | Path) -> pd.DataFrame:
    """
    讀取 GDMS Catalog JSON（header+body），回傳標準欄位：
    ['time','lat','lon','depth','mag','year']
    """
    p = Path(json_path)
    with p.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    if not (isinstance(raw, dict) and {"header", "body"} <= set(raw.keys())):
        raise ValueError("此版本僅支援 GDMS Catalog（需包含 'header' 與 'body'）。")

    header, body = raw["header"], raw["body"]
    if not isinstance(header, list) or not isinstance(body, list) or not body:
        raise ValueError("GDMS JSON 結構不完整（header/body）。")

    # body 可能是「list of list」或「list of dict」
    if isinstance(body[0], (list, tuple)):
        max_len = max(len(r) for r in body)
        cols = [str(h) for h in header][:max_len]
        if len(cols) < max_len:
            cols += [f"col_{i}" for i in range(len(cols), max_len)]
        body_fixed = [list(r) + [None] * (max_len - len(r)) for r in body]
        df = pd.DataFrame(body_fixed, columns=cols)
    else:
        df = pd.DataFrame(body)

    # 找時間欄（優先 date+time，其次 datetime / originTime / eventTime / time）
    date_col = _pick(df, ["date", "日期"])
    time_col = _pick(df, ["time", "時間"])
    dt_col = _pick(df, ["datetime", "origintime", "eventtime", "發震時刻", "time"])

    if date_col and time_col:
        ts_series = (
            df[date_col].astype(str).str.strip()
            + " "
            + df[time_col].astype(str).str.strip()
        )
        # 標準化：YYYY-MM-DD HH:MM:SS
        ts_series = ts_series.str.replace("T", " ", regex=False).str.replace("/", "-", regex=False)
        # 若 time 是 HHMMSS 沒有冒號，加上
        ts_series = ts_series.apply(
            lambda s: re.sub(r"(\d{2})(\d{2})(\d{2})$", r"\1:\2:\3", s) if re.search(r"\d{6}$", s) and ":" not in s[-8:] else s
        )
        df["time"] = pd.to_datetime(ts_series, errors="coerce")
    elif dt_col:
        tmp = df[dt_col].astype(str).str.strip().str.replace("T", " ", regex=False).str.replace("/", "-", regex=False)
        tmp = tmp.apply(
            lambda s: re.sub(r"(\d{2})(\d{2})(\d{2})$", r"\1:\2:\3", s) if re.search(r"\d{6}$", s) and ":" not in s[-8:] else s
        )
        df["time"] = pd.to_datetime(tmp, errors="coerce")
    else:
        # 逐列嘗試推斷
        df["time"] = pd.to_datetime(df.apply(_infer_time_from_row, axis=1), errors="coerce")

    # 經緯度/深度/規模欄位
    lat_col = _pick(df, ["lat", "latitude", "緯度", "y", "震央緯度"])
    lon_col = _pick(df, ["lon", "longitude", "經度", "x", "震央經度"])
    dep_col = _pick(df, ["depth", "focaldepth", "深度"])
    mag_col = _pick(df, ["mag", "magnitude", "規模", "ml", "mw"])

    rename = {}
    if lat_col: rename[lat_col] = "lat"
    if lon_col: rename[lon_col] = "lon"
    if dep_col: rename[dep_col] = "depth"
    if mag_col: rename[mag_col] = "mag"
    df = df.rename(columns=rename)

    # 型別轉換
    for c in ["lat", "lon", "depth", "mag"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # 只保留需要欄位
    keep = ["time", "lat", "lon"] + [c for c in ["depth", "mag"] if c in df.columns]
    df = df[keep]

    # 去除無效
    df = df.dropna(subset=["time", "lat", "lon"]).copy()

    # 台灣大致範圍（避免海外點誤入）
    df = df[(df["lat"].between(20, 27)) & (df["lon"].between(118, 124))].copy()

    df["year"] = pd.to_datetime(df["time"]).dt.year
    df = df.sort_values("time").reset_index(drop=True)
    return df


# -------------------------------
# 互動地圖（下拉選年）— 橘/紅配色
# -------------------------------
def make_interactive_map(json_path: str, outfile: str = "index.html") -> None:
    df = _load_quakes_from_gdms(json_path)

    years = sorted(df["year"].dropna().unique().tolist())
    print(f"[INFO] records={len(df)}, years={years}")

    m = folium.Map(location=[23.7, 121.0], zoom_start=7, tiles="CartoDB positron")

    # 每個年份一個 FeatureGroup；記下對應的 JS 變數名稱
    year_to_jsvar: dict[int, str] = {}

    for i, year in enumerate(years):
        fg = folium.FeatureGroup(name=str(year), show=(i == 0))
        yearly = df[df["year"] == year]

        for _, r in yearly.iterrows():
            depth = float(r["depth"]) if "depth" in r and pd.notna(r["depth"]) else None
            mag = float(r["mag"]) if "mag" in r and pd.notna(r["mag"]) else None

            # 顏色：<=70km 橘色，>70km 紅色
            color = "#ff7f0e" if (depth is None or depth <= 70) else "#d62728"

            folium.CircleMarker(
                location=[float(r["lat"]), float(r["lon"])],
                radius=(3 + (mag if mag is not None else 0)),  # 規模越大點越大
                color=color,
                weight=1,
                fill=True,
                fill_color=color,
                fill_opacity=0.65,
                popup=(
                    f"時間：{pd.to_datetime(r['time']).strftime('%Y-%m-%d %H:%M:%S')}<br>"
                    f"規模：{(f'{mag:.1f}' if mag is not None else '—')}<br>"
                    f"深度：{(f'{depth:.1f} km' if depth is not None else '—')}"
                ),
            ).add_to(fg)

        fg.add_to(m)
        # 取得此 FeatureGroup 的 JS 變數名稱（folium 內部用 get_name()）
        year_to_jsvar[year] = fg.get_name()

    # 保留 LayerControl（可多選/核取）
    folium.LayerControl(collapsed=False).add_to(m)

    # 自訂下拉式選單 + JS：單選年份（或全部）
    map_var = m.get_name()
    years_options = "\n".join([f"<option value='{y}'>{y}</option>" for y in years])
    js_groups = "\n".join([f"groups['{y}'] = {year_to_jsvar[y]};" for y in years])

    html = f"""
<div id="year-picker" style="
  position: fixed; top: 10px; left: 50px; z-index: 9999;
  background: white; padding: 6px 8px; border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.3); font: 14px/1.2 Arial;">
  <label style="margin-right:6px;">年份</label>
  <select id="yearSelect">
    <option value="all">全部</option>
    {years_options}
  </select>
</div>
<script>
(function() {{
  var map = {map_var};
  var groups = {{}};
  {js_groups}

  function showYear(y) {{
    Object.keys(groups).forEach(function(k) {{
      if (y === 'all') {{
        if (!map.hasLayer(groups[k])) map.addLayer(groups[k]);
      }} else {{
        if (k === y) {{
          if (!map.hasLayer(groups[k])) map.addLayer(groups[k]);
        }} else {{
          if (map.hasLayer(groups[k])) map.removeLayer(groups[k]);
        }}
      }}
    }});
  }}

  // 初始：顯示第一個年份（或全部）
  var sel = document.getElementById('yearSelect');
  sel.addEventListener('change', function() {{ showYear(this.value); }});
  // 預設顯示第一個年份
  sel.value = '{years[0] if years else "all"}';
  showYear(sel.value);
}})();
</script>
"""
    m.get_root().html.add_child(Element(html))

    # 固定輸出檔名為 index.html（方便 GitHub Pages）
    Path(outfile).parent.mkdir(parents=True, exist_ok=True)
    m.save(outfile)
    print(f"[OK] 互動地圖輸出：{outfile}")


# -------------------------------
# （可選）本地測試
# -------------------------------
if __name__ == "__main__":
    # 例：
    # make_interactive_map("attached_assets/data/earthquakes/GDMScatalog.json",
    #                      outfile="release/index.html")
    pass
