import json
import pandas as pd
import folium

# 路徑：以 repo 根目錄為基準
JSON_PATH = "./self-extended-practice/taiwan_earthquake_analysis/data/earthquakes/E-A0073-001.json"
HTML_OUT = "./self-extended-practice/taiwan_earthquake_analysis/output/taiwan_earthquake_map.html"

# 讀 JSON
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# 取地震清單
eq_list = data["cwaopendata"]["Dataset"]["Catalog"]["EarthquakeInfo"]
df = pd.json_normalize(eq_list)

# 欄位轉型
df["lat"] = pd.to_numeric(df["EpicenterLatitude"], errors="coerce")
df["lon"] = pd.to_numeric(df["EpicenterLongitude"], errors="coerce")
df["depth"] = pd.to_numeric(df["FocalDepth"], errors="coerce")
df["mag"] = pd.to_numeric(df["LocalMagnitude"], errors="coerce")
df["year"] = pd.to_datetime(df["OriginTime"], errors="coerce").dt.year

# 只留台灣近海範圍，避免跑去太平洋 & 中國內陸
df = df[(df["lat"] >= 20) & (df["lat"] <= 26.5) & (df["lon"] >= 118) & (df["lon"] <= 123.8)]

# folium 繪圖
m = folium.Map(location=[23.7, 121], zoom_start=7, tiles="OpenStreetMap")

for _, row in df.iterrows():
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

m.save(HTML_OUT)
print(f"✅ 地圖已輸出：{HTML_OUT}")
