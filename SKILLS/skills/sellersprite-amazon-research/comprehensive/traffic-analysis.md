# 流量結構分析

拆解 ASIN 的流量來源，分析自然/廣告/推薦流量結構。

## 使用方式

```
/traffic-analysis [ASIN] [站點]
```

## 工具呼叫

透過 MCP client 呼叫：`mcp__sellersprite__<tool_name>`

**響應解析**：`result.content[0].text` 是 JSON 字串，需二次解析。

## 執行步驟

### 第1步: 獲取流量來源

`mcp__sellersprite__traffic_source` — **扁平引數** + `"q": "asin"`

```json
{"marketplace": "US", "asin": "B0XXX", "q": "asin"}
```

> ⚠️ 實測：文件標為 `request` 巢狀物件，但實際 API 要求扁平引數 + `q` 欄位。`q` 值固定傳 `"asin"`。

### 第2步: 獲取關鍵詞流量統計

`mcp__sellersprite__traffic_keyword_stat` — 扁平引數 `{"marketplace":"US", "asin":"B0XXX"}`
- ⚠️ 實際欄位：`keywords`(總數)、`ranks`(有排名)、`ads`(有廣告)

### 第3步: 獲取完整流量詞

`mcp__sellersprite__traffic_keyword` — `{"request": {"marketplace":"US", "asin":"B0XXX"}}`

### 第4步: 儲存結果 + 生成報告

同時儲存原始資料和報告到 `{類別目錄}/`。

**報告結構：** 流量總覽 → 自然/廣告/推薦佔比（餅圖，0~1×100）→ Top流量詞 → 自然排名表現 → 廣告投放分析 → 流量缺口 → 最佳化建議

### 欄位注意
- `trafficPercentage/naturalRatio/adRatio` 為 0~1，展示 ×100
- `rankPosition`/`adPosition` 是物件，取 `.position`
