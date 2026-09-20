# 廣告投放最佳化

基於關鍵詞資料最佳化 PPC 廣告策略。

## 使用方式

```
/ad-optimizer [ASIN或關鍵詞] [站點]
```

## 工具呼叫

透過 MCP client 呼叫：`mcp__sellersprite__<tool_name>`。

**響應解析**：`result.content[0].text` 是 JSON 字串，需二次解析。

## 執行步驟

### 第1步: 關鍵詞排名與轉化

`mcp__sellersprite__keyword_order` — `{"request": {"marketplace":"US", "asin":"B0XXX"}}`

### 第2步: 流量關鍵詞

`mcp__sellersprite__traffic_keyword` — `{"request": {"marketplace":"US", "asin":"B0XXX"}}`
- 提取：`searches`、`bid/bidMin/bidMax`、`adPosition`、`rankPosition`

### 第3步: 關鍵詞分類

將關鍵詞分為：高價值詞（高轉化+合理競價）、機會詞（高搜尋+低競價）、低效詞（高競價+低轉化）

### 第4步: 儲存結果 + 生成報告

同時儲存原始資料和報告到 `{類別目錄}/`。

**報告結構：** 投放概覽 → 高價值詞（建議出價）→ 機會關鍵詞 → 否定詞建議 → 競價最佳化 → 廣告結構建議

### 欄位注意
- `bid/bidMin/bidMax` 為 PPC 競價
- `naturalRatio/adRatio` 為 0~1，展示 ×100
- 區分自然排名(`rankPosition.position`)和廣告排名(`adPosition.position`)
