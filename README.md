# 🌏 台灣地震互動地圖 Taiwan Earthquake Interactive Map (2000–2025)

## 📖 專案簡介 / Project Overview
這個專案使用 **台灣地震目錄（GDMS JSON 資料）**，將 2000–2025 年的地震資料視覺化成互動式地圖。  
使用者可透過下拉選單切換年份，並在地圖上查看各地震的震央、規模與深度。

This project uses **Taiwan Earthquake Catalog (GDMS JSON data)** to visualize earthquakes from 2000–2025 on an interactive map.  
Users can switch between years via a dropdown menu and view earthquake epicenters, magnitudes, and depths directly on the map.

---

## 🛠️ 技術堆疊 / Tech Stack
- **Python**：資料處理與清理 / Data processing and cleaning  
- **pandas**：資料轉換與欄位標準化 / Data transformation and column normalization  
- **folium**：生成互動式地圖與圖層控制 / Interactive map generation with layer controls  
- **GitHub Pages**：專案展示與成果發佈 / Project hosting and result presentation  

---

## 📂 專案結構 / Project Structure
```
data-visualization-labs/
│── self-extended-practice/
│   └── taiwan_earthquake_analysis/
│       ├── data/earthquakes/       # JSON 原始地震資料 / Raw earthquake data (JSON)
│       ├── src/make_map_by_year.py # 地圖生成程式 / Map generation script
│       ├── main.py                 # 主程式入口 / Main script entry
│       └── release/
│           └── index.html           # 輸出互動式地圖 / Interactive map output
```

---

## 🚀 使用方式 / Usage
1. 下載或更新地震 JSON 資料 (GDMS Catalog)。  
   Download or update earthquake JSON data (GDMS Catalog).  

2. 執行 `main.py` 產生互動地圖。  
   Run `main.py` to generate the interactive map.  

3. 生成結果將輸出到 `release/index.html`，可直接用瀏覽器開啟。  
   The output will be saved as `release/index.html`, which can be opened directly in a browser.  

---

## 🌐 線上展示 / Live Demo
👉 [GitHub Pages 展示 / View on GitHub Pages](https://a0013333j-png.github.io/data-visualization-labs/)  

---

## 📊 專案亮點 / Highlights
- ✅ **2000–2025 年全台地震分布** / Earthquake distribution across Taiwan from 2000–2025  
- ✅ **互動式下拉選單** / Interactive year dropdown selection  
- ✅ **地震詳細資訊（規模、深度、時間）** / Detailed earthquake information (magnitude, depth, time)  
- ✅ **可直接部署於 GitHub Pages** / Ready to deploy on GitHub Pages  

---

## 👤 作者 / Author
- **Pei-Ling Shih**  
  Data Visualization & Analytics Enthusiast  
