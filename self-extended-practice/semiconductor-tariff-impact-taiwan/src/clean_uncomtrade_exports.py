import pandas as pd
from pathlib import Path

def clean_uncomtrade_exports(raw_path, processed_path):
    # 讀取原始資料
    df = pd.read_csv(raw_path)
    
    # 保留必要欄位
    keep_cols = ["Period", "Reporter", "Trade Value (US$)"]
    df = df[keep_cols].rename(columns={
        "Period": "Year",
        "Trade Value (US$)": "ExportValueUSD"
    })
    
    # 移除缺失值
    df = df.dropna(subset=["ExportValueUSD"])
    
    # 確保數值型態正確
    df["ExportValueUSD"] = pd.to_numeric(df["ExportValueUSD"], errors="coerce")
    
    # 移除 ExportValueUSD = 0 的列
    df = df[df["ExportValueUSD"] > 0]
    
    # 排序
    df = df.sort_values(by=["Year", "Reporter"]).reset_index(drop=True)
    
    # 輸出到 processed/
    Path(processed_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)
    print(f"✅ Cleaned file saved to: {processed_path}")

if __name__ == "__main__":
    raw_file = "self-extended-practice/semiconductor-tariff-impact-taiwan/data/raw/ic_exports_comparison_uncomtrade_2013_2024.csv"
    processed_file = "self-extended-practice/semiconductor-tariff-impact-taiwan/data/processed/ic_exports_comparison_clean_2013_2024.csv"
    clean_uncomtrade_exports(raw_file, processed_file)
