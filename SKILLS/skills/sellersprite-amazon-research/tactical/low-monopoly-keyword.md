# 流量分散關鍵詞

找搜尋量大但點選集中度低的關鍵詞（藍海詞）。

## 工具
`mcp__sellersprite__keyword_miner` — `{"request": {...}}`

## 篩選引數
- `minSearch`: 5000
- 客戶端過濾 `monopolyClickRate < 0.5`（集中度<50%）

## 輸出
藍海關鍵詞表 + 搜尋量/購買率/競價/供需比

## 注意
`monopolyClickRate` 為 0~1，過濾比較 < 0.5
