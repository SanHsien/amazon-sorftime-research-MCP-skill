# 新品快速爆發

找上架不久但銷量已快速攀升的新品。

## 工具
`mcp__sellersprite__product_research` — `{"request": {...}}`

## 篩選引數
- `minUnits`: 300, `maxRatings`: 100, `minUnitsCr`: 正增長
- 按 `units` 降序

## 邏輯
上架≤2月 + 月銷量≥300 + Review≤100 → 已驗證市場需求，評論門檻低。

## 輸出
新品 ASIN 列表 + 銷量/價格/評分/BSR 對比 + 進入可行性分析

## 注意
響應欄位用 `units`(銷量)、`revenue`(銷售額)、`ratings`(評分)
