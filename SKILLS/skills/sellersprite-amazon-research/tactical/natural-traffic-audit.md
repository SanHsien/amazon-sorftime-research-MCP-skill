# 自然流量反查

找自然流量佔比高的 ASIN（驗證是否為真實需求驅動）。

## 工具
`mcp__sellersprite__traffic_source` — `{"request": {"marketplace":"US", "asin":"B0XXX"}}`

## 過濾標準
- 自然流量佔比 > 60%（0~1 比較 > 0.6）

## 輸出
流量結構餅圖 + 自然/廣告/推薦佔比 + 驗證結論
