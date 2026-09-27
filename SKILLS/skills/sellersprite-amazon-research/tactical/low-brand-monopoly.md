# 低品牌壟斷類目

找品牌集中度低的類目（新品牌友好）。

## 工具
`mcp__sellersprite__market_research` — `{"request": {...}}`

## 篩選
- 客戶端過濾 `topBrandCrn <= 0.45`（品牌集中度≤45%）

## 輸出
低壟斷類目列表 + 市場規模/增長/競爭格局

## 注意
`topBrandCrn` 為 0~1，過濾比較 ≤ 0.45
