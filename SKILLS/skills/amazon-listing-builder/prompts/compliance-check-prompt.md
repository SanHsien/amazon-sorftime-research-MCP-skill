# 合規檢查提示詞

> 用於最終校驗階段：檢查 Listing 是否違反亞馬遜政策和合規要求。

---

## 提示詞

```
你是一名亞馬遜合規稽核專家。請對以下 Listing 進行合規檢查。

## 輸入
- 標題：[貼上]
- 五點描述：[貼上 5 點]
- 產品描述：[貼上]
- A+ 內容文案：[貼上]
- Search Terms：[貼上]
- QA：[貼上 10 題]
- 產品類目：[填]
- 產品認證：[填，如 CPSIA / FDA / RoHS]

## 檢查維度

### 1. 絕對化表達檢查
掃描以下詞彙並標記：
- 100% / never / always / lifetime / forever
- best / #1 / top rated / cheapest / lowest price
- guaranteed / guarantee（無明確政策時）

替代建議：
- "100% no fade" → "help reduce fading"
- "lifetime use" → "designed for long-term use"
- "best seller" → "popular choice"

### 2. 醫療承諾檢查
掃描以下詞彙並標記：
- cures / treats / heals / prevents disease
- FDA approved（除非真有認證）
- medical grade / clinical proven（除非真有認證）
- relief from [disease name]

替代建議：
- "cures back pain" → "supports posture"
- "treats insomnia" → "may help with relaxation"

### 3. 環保承諾檢查
掃描以下詞彙並標記：
- 100% eco-friendly / 100% biodegradable
- organic（除非有 USDA Organic 認證）
- non-toxic（除非有認證）
- chemical-free

替代建議：
- "100% eco-friendly" → "made with recyclable materials"
- "organic" → "natural materials"（無認證時）

### 4. 安全承諾檢查
掃描以下詞彙並標記：
- FDA approved / CPSIA certified（除非真有）
- child-safe / baby-safe（如無測試）
- fireproof / waterproof（如無測試）

### 5. 競品品牌詞檢查
掃描已知競品品牌名（使用者提供）：
- 競品 A：[填]
- 競品 B：[填]
- 檢查所有文案 + ST 是否含這些詞

### 6. 重複堆詞檢查
- 標題中是否有同一關鍵詞重複出現（如 "artificial flowers" 出現 2 次）
- 五點中同一賣點是否重複
- 標題 vs ST 是否重複（ST 不應重複標題已有詞）

### 7. 欄位長度檢查
| 欄位 | 限制 |
|------|------|
| 標題（美國） | ≤ 200 字元（建議 ≤ 180） |
| 五點單點 | ≤ 500 字元（建議 ≤ 300） |
| 描述 | ≤ 2000 字元（建議 ≤ 1200） |
| ST（美國） | ≤ 250 位元組 |

### 8. 關鍵詞相關性檢查
- 每個埋入的關鍵詞是否與產品真實相關
- 是否有為了流量埋不相關熱詞

### 9. 誇大承諾檢查
- "premium quality" / "perfect for any occasion" / "great gift" / "easy to use"
- 沒有具體證據的形容詞

### 10. 虛假宣告檢查
- "limited edition"（除非真有限量）
- "best seller"（除非真有資料）
- "as seen on TV"（除非真有）
- "doctor recommended"（除非真有）

## 輸出格式

# 合規稽核報告

## 風險等級
- 高風險：X 處（必須修改）
- 中風險：X 處（建議修改）
- 低風險：X 處（可選修改）

## 詳細問題清單

### 高風險問題
| # | 位置 | 原文 | 問題 | 修改建議 |
|---|------|------|------|---------|
| 1 | 五點 1 | "100% no fade" | 絕對化表達 | 改為 "help reduce fading" |

### 中風險問題
...

### 低風險問題
...

## 透過的檢查項
- [x] 無競品品牌詞
- [x] 欄位長度全部合規
- [x] 無醫療承諾
- ...

## 整改建議
1. 優先修改高風險問題（X 處）
2. 修改後再做一次複審
3. 中風險問題上線後逐步最佳化
```

---

## 紅線詞清單（必須替換）

| 紅線詞 | 替代 |
|--------|------|
| 100% | help / support / designed to |
| never / always | tends to / designed to |
| lifetime / forever | long-term use |
| best / #1 / top rated | popular / favored |
| cheap / lowest price | affordable / value |
| cures / treats | supports / may help |
| 100% eco-friendly | made with recyclable materials |
| FDA approved（無認證） | meets [actual standard] |
| organic（無認證） | natural materials |
| guaranteed | designed for / backed by [policy] |
| fireproof（無測試） | fire-resistant（如有測試） |

---

## 使用時機

1. **生成 Listing 後必須先跑一次合規檢查**
2. **修改後再跑一次**確保問題都解決
3. **上線前最後一次稽核**
4. **定期複審**（亞馬遜政策更新時）
