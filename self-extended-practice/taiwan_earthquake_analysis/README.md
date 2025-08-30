# Taiwan Earthquake Analysis

互動式地圖呈現中央氣象署（CWA）地震目錄資料（JSON），顯示震央位置、規模與深度（<70km 藍、≥70km 紅），並限制在台灣及近海範圍。

## 專案結構
```
self-extended-practice/taiwan_earthquake_analysis/
├── README.md
├── requirements.txt
├── src/
│ └── make_map.py
├── data/
│ └── earthquakes/
│ └── E-A0073-001.json
├── output/
│ └── taiwan_earthquake_map.html
└── .gitignore
```

## 資料來源
- 政府資料開放平臺 → 中央氣象署地震目錄（E-A0073-001）

## 如何執行
```bash
pip install -r requirements.txt
python src/make_map.py
