# ABA 高增長趨勢詞

透過 ABA 資料發現近 3 月持續增長的關鍵詞。

## 工具
`mcp__sellersprite__keyword_research` — `{"request": {...}}`
`mcp__sellersprite__keyword_research_trends` — 扁平引數 `{"marketplace":"US", "keyword":"..."}`

## 篩選邏輯
- 近 3 月搜尋排名持續上升
- `monopolyClickRate` < 50%（0~1 比較 < 0.5）
- `supplyDemandRatio` 20-80

## 輸出
高增長關鍵詞表 + 搜尋量趨勢 + 競爭度 + PPC 競價

## 注意
`keyword_research_trends` 欄位：`time`/`search`/`chainGrowth`(環比)
