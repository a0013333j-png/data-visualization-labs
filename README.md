# 📍 Taiwan Earthquake Analysis (2000–2025)

互動式地圖專案，視覺化台灣 2000–2025 年地震事件（來源：**中央氣象署 GDMS**）。  
地圖可透過下拉式選單選擇年份，點擊地震標記可查看 **時間、規模、深度**。  
專案部署在 **GitHub Pages**，任何人都能直接體驗成果。

👉 **[立即體驗互動地圖](https://a0013333j-png.github.io/data-visualization-labs/)**

---

## 🔹 專案特色
- **資料來源**：中央氣象署 GDMS 平台（地震目錄 JSON，2000–2025 年，ML ≥ 4）。  
- **互動功能**：
  - 下拉式選單切換年份  
  - 圓點大小對應地震規模  
  - 圓點顏色對應地震深度（橘→淺層、紅→深層）  
  - 點擊地震位置顯示詳細資訊（時間 / 規模 / 深度）  
- **部署平台**：GitHub Pages（自動化 CI/CD 部署）

---

## 🛠 技術堆疊
- **程式語言**：Python 3.11  
- **套件**：
  - `pandas` → 資料清理、欄位轉換  
  - `folium` → 地圖繪製（Leaflet.js 封裝）  
- **版本控管**：Git & GitHub  
- **前端部署**：GitHub Pages  

---

## 📂 專案架構
```bash
taiwan_earthquake_analysis/
│── data/                # 原始地震資料 (JSON)
│── src/                 # Python 程式碼
│   └── make_map_by_year.py
│── index.html           # 最終輸出的互動地圖 (部署頁面)
│── README.md            # 專案說明文件
```

---

## 🚀 使用方式
1. **下載專案**
   ```bash
   git clone https://github.com/a0013333j-png/data-visualization-labs.git
   cd self-extended-practice/taiwan_earthquake_analysis
   ```
2. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```
3. **生成互動地圖**
   ```bash
   python main.py
   ```
   預設會輸出 **index.html**，可直接在瀏覽器開啟。

---

## 📊 成果展示
- [✅ GitHub Pages 網站](https://a0013333j-png.github.io/data-visualization-labs/)  
- 下圖為專案成果截圖：  
  ![demo](https://raw.githubusercontent.com/a0013333j-png/data-visualization-labs/main/self-extended-practice/taiwan_earthquake_analysis/demo.png)

---

## 📌 後續改進
- 增加 **規模篩選**（M ≥ 5, M ≥ 6）  
- 增加 **熱度圖 (HeatMap)**  
- 增加 **統計圖表**（年份 vs 次數）  
