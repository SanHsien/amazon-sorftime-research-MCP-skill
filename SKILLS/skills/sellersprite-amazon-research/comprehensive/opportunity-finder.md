# 藍海機會挖掘

透過 ABA 趨勢發現飆升/增長/潛力關鍵詞。

## 使用方式

```
/opportunity-finder [關鍵詞或類目] [站點]
```

## 工具呼叫

透過 MCP client 呼叫：`mcp__sellersprite__<tool_name>`

**響應解析**：`result.content[0].text` 是 JSON 字串，需二次解析。

## 執行步驟

### 第1步-第3步: ABA 資料獲取

1. `mcp__sellersprite__aba_research_weekly` — `{"request": {"marketplace":"US", "keyword":"..."}}`
2. `mcp__sellersprite__aba_research_monthly` — `{"request": {"marketplace":"US", "keyword":"..."}}`
3. `mcp__sellersprite__aba_research_trend` — 扁平引數 `{"marketplace":"US", "keyword":"..."}`
   - ⚠️ 實際欄位：`label`(月份)、`date`、`searches`、`rank`（無 `clickShareRate`/`conversionShareRate`）

### 第4步: Google 趨勢（可選）

`mcp__sellersprite__google_trend` — `{"request": {"marketplace":"US", "keyword":"..."}}`

### 第5步: 儲存結果 + 生成報告

同時儲存原始資料和報告到 `{類別目錄}/`。

**報告結構：** 飆升關鍵詞 → 持續增長詞 → 季節性機會 → 藍海詞篩選 → Google趨勢驗證 → 行動建議
