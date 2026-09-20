# 報告管理

## 目錄結構

```
專案目錄/
├── reports/
│   ├── analysis_B07PQFT83F_US_20260302.md
│   ├── analysis_B08N5WRWNW_US_20260302.md
│   └── archive/
│       ├── 2025/
│       │   ├── analysis_xxx_US_20251215.md
│       │   └── ...
│       └── 2024/
│           └── ...
└── .claude/
    └── skills/
        └── amazon-analyse/
```

## 報告生命週期

| 階段 | 時間範圍 | 處理方式 |
|------|----------|----------|
| **活躍期** | 最近30天 | 保持在 `reports/` 根目錄 |
| **參考期** | 1-6個月 | 移至 `reports/archive/YYYY/` |
| **歸檔期** | 6個月以上 | 可壓縮歸檔或刪除 |

## 報告對比分析

**縱向對比**：同一ASIN不同時期的報告
```bash
# 對比同一產品在不同時間的資料變化
diff reports/analysis_xxx_US_20260101.md \
     reports/analysis_xxx_US_20260301.md
```

**橫向對比**：不同ASIN在同一時期的報告
```bash
# 對比競品之間的資料差異
ls -la reports/analysis_*_US_20260302.md
```

## 報告應用場景

1. **競品追蹤**：定期分析同一競品，監控其策略變化
2. **市場研究**：積累多個產品報告，發現行業趨勢
3. **團隊分享**：將報告傳送給運營、產品團隊
4. **決策支援**：基於歷史資料制定定價、選品策略

## 報告匯出格式

報告預設儲存為 Markdown 格式，可轉換為：
- PDF（用於列印/分享）
- HTML（用於網頁展示）
- Excel（用於資料提取）

## 報告儲存最佳實踐

1. 每次分析都儲存獨立檔案，便於歷史對比
2. 檔名包含日期，支援多次分析同一產品
3. 報告開頭包含分析時間戳，確保資料時效性
4. 建議定期整理舊報告，歸檔到 `reports/archive/` 目錄

## 報告檔案命名規則

```
analysis_{ASIN}_{站點}_{日期}.md
例如: analysis_B07PQFT83F_US_20260302.md
```

## 儲存位置

```
專案目錄/reports/
```

## 儲存命令

```bash
# 1. 先檢查/建立 reports 目錄
mkdir -p reports/

# 2. 生成報告檔案路徑（使用當前日期）
FILENAME="reports/analysis_${ASIN}_${站點}_$(date +%Y%m%d).md"

# 3. 使用 Write 工具儲存完整報告內容
Write $FILENAME
```
