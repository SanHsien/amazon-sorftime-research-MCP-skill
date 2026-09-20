# 智慧選品助手

按多維條件篩選潛力商品，評估進入可行性。

## 使用方式

```
/product-research [關鍵詞] [站點] [篩選條件]
```

## 工具呼叫

透過 MCP client 呼叫：`mcp__sellersprite__product_research`

**引數模式**：`request` 巢狀物件 — 所有引數包裹在 `request` 鍵下。

**響應解析**：`result.content[0].text` 是 JSON 字串，需二次解析：
```python
raw = json.loads(result['content'][0]['text'])
data = raw.get('data', [])
```

## 執行步驟

### 第1步: 獲取類目節點（如需）

呼叫 `mcp__sellersprite__product_node`：
- 引數：`{"request": {"marketplace": "US", "keyword": "yoga mat"}}`
- ⚠️ `nodeLabelLocale`（中文翻譯）不可靠，以英文 `nodeLabelPath` 為準

### 第2步: 執行商品篩選

呼叫 `mcp__sellersprite__product_research`：
- 引數：`{"request": {"marketplace":"US", "keyword":"...", "minUnits":100, ...}}`

**常用篩選維度：** `keyword`, `marketplace`, `month`, `minUnits/maxUnits`, `minRevenue/maxRevenue`, `minPrice/maxPrice`, `minRating`, `minSubBsrRank`, `fulfillment`("FBA,FBM,AMZ"), `sellerNation`, `minLqs`, `minProfit`

### 第3步: 儲存結果

同時儲存兩份檔案：
1. **原始資料** → `{類別目錄}/research_data.json`
2. **分析報告** → `{類別目錄}/product_report.md`

### 第4步: 生成報告

**報告結構：** 篩選口徑 → KPI概覽 → 商品候選表（units/revenue/ratings/bsr）→ 進入建議

### 欄位注意
- `units`=月銷量、`revenue`=月銷售額、`ratings`=評分數、`bsr`=BSR
- 多值引數傳逗號字串，當前月資料可能為 None
- HTML 實體解碼：`html.unescape(title)`
