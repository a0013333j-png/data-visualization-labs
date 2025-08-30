import json
import pandas as pd
import folium
import sys

# 路徑
JSON_PATH = "./self-extended-practice/taiwan_earthquake_analysis/data/earthquakes/E-A0073-001.json"
OUTPUT_TEMPLATE = "./self-extended-practice/taiwan_earthquake_analysis/output/taiwan_earthquake_map_{year}.html"

# 載入資料
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

eq_list = data["cwaopendata"]["Dataset"]["Catalog"]["EarthquakeInfo"]
df = pd.json_normalize(eq_list)

# 數據轉換
df["lat"] = pd.to_numeric(df["EpicenterLatitude"], errors="coerce")
df["lon"] = pd.to_numeric(df["EpicenterLongitude"], errors="coerce")
df["depth"] = pd.to_numeric(df["FocalDepth"], errors="coerce")
df["mag"] = pd.to_numeric(df["LocalMagnitude"], errors="coerce")
df["year"] = pd.to_datetime(df["OriginTime"], errors="coerce").dt.year

# 範圍過濾（台灣近海）
df = df[(df["lat"] >= 20) & (df["lat"] <= 26.5) & (df["lon"] >= 118) & (df["lon"] <= 123.8)]

# 使用方式：python make_map_by_year.py 2025
if len(sys.argv) < 2:
    print("請輸入年份，例如：python make_map_by_year.py 2025")
    sys.exit(1)

year = int(sys.argv[1])
df_year = df[df["year"] == year]

if df_year.empty:
    print(f"⚠️ 沒有 {year} 年的地震資料")
    sys.exit(0)

# 繪製地圖
m = folium.Map(location=[23.7, 121], zoom_start=7, tiles="OpenStreetMap")

for _, row in df_year.iterrows():
    if pd.isna(row["lat"]) or pd.isna(row["lon"]):
        continue
    color = "blue" if (row["depth"] or 0) < 70 else "red"
    radius = max(2, min(12, (row["mag"] or 0) * 2))

    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
        popup=(
            f"時間：{row['OriginTime']}<br>"
            f"規模：{row['mag']}<br>"
            f"深度：{row['depth']} km<br>"
            f"座標：({row['lat']}, {row['lon']})"
        )
    ).add_to(m)

out_path = OUTPUT_TEMPLATE.format(year=year)
m.save(out_path)
print(f"✅ {year} 年地圖已輸出：{out_path}")
