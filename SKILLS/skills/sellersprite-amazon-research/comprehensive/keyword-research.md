# 關鍵詞選品研究

基於關鍵詞進行市場需求分析，挖掘高潛力關鍵詞。

## 使用方式

```
/keyword-research [種子詞] [站點]
```

## 工具呼叫

透過 MCP client 呼叫：`mcp__sellersprite__<tool_name>`

**引數模式**：`keyword_miner`/`keyword_research` 使用 `request` 巢狀物件；`keyword_research_trends` 使用扁平引數。

**響應解析**：`result.content[0].text` 是 JSON 字串，需二次解析。

## 執行步驟

### 第1步: 關鍵詞挖掘

呼叫 `mcp__sellersprite__keyword_miner`：
- 引數：`{"request": {"marketplace":"US", "keyword":"種子詞"}}`

### 第2步: 關鍵詞研究

呼叫 `mcp__sellersprite__keyword_research`：
- 引數：`{"request": {"marketplace":"US", "keyword":"種子詞"}}`

### 第3步: 關鍵詞趨勢

呼叫 `mcp__sellersprite__keyword_research_trends`：
- 扁平引數：`{"marketplace":"US", "keyword":"種子詞"}`
- ⚠️ 實際欄位：`time`（非 `month`）、`search`（非 `searches`）、`chainGrowth`（環比）、`yearlyGrowth`（同比）

### 第4步: 儲存結果

同時儲存兩份檔案：
1. **原始資料** → `{類別目錄}/research_data.json`
2. **分析報告** → `{類別目錄}/keyword_report.md`

### 第5步: 生成報告

**報告結構：** 關鍵詞總覽 → 高潛力詞表 → 趨勢分析 → 競爭分析 → 長尾詞機會 → 廣告建議

### 欄位注意
- `purchaseRate/cvsShareRate/monopolyClickRate` 為 0~1，展示 ×100
- `supplyDemandRatio` 真實比值不換算
- `keyword_research_trends` 用 `time`/`search`/`chainGrowth` 欄位，非文件名
