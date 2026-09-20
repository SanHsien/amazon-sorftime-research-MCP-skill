# Listing 最佳化診斷

診斷 Listing 質量，發現關鍵詞覆蓋缺口。

## 使用方式

```
/listing-optimizer [ASIN] [站點]
```

## 工具呼叫

透過 MCP client 呼叫：`mcp__sellersprite__<tool_name>`

**響應解析**：`result.content[0].text` 是 JSON 字串，需二次解析。

## 執行步驟

### 第1步: 獲取 Listing 基本資訊

`mcp__sellersprite__asin_detail` — 扁平引數 `{"marketplace":"US", "asin":"B0XXX"}`

### 第2步: 獲取 Listing 流量資料

`mcp__sellersprite__traffic_listing` — `{"request": {"marketplace":"US", "asin":"B0XXX"}}`

### 第3步: 獲取關鍵詞表現

`mcp__sellersprite__keyword_order` — `{"request": {"marketplace":"US", "asin":"B0XXX"}}`

`mcp__sellersprite__traffic_keyword` — `{"request": {"marketplace":"US", "asin":"B0XXX"}}`

### 第4步: 儲存結果 + 生成報告

同時儲存原始資料和報告到 `{類別目錄}/`。

**報告結構：** Listing概覽 → 關鍵詞覆蓋分析（自然/廣告排名）→ 標題最佳化 → 搜尋詞埋詞 → 圖片內容診斷 → 評分評論診斷 → 行動優先順序

### 欄位注意
- `traffic_keyword` 中 `rankPosition` 取 `.position`
- `naturalRatio/adRatio` 為 0~1，展示 ×100
- HTML 實體解碼：`html.unescape(title)`
