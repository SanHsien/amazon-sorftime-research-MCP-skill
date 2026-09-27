# 定價策略分析

分析市場價格帶分佈，制定最優定價策略。

## 使用方式

```
/pricing-strategy [類目關鍵詞或節點ID] [站點]
```

## 工具呼叫

透過 MCP client 呼叫：`mcp__sellersprite__<tool_name>`，均使用 `request` 巢狀引數。

**響應解析**：`result.content[0].text` 是 JSON 字串，需二次解析。

## 執行步驟

### 第1步: 獲取類目節點

`mcp__sellersprite__product_node` — `{"request": {"marketplace":"US", "keyword":"..."}}`

### 第2步: 獲取價格分佈

`mcp__sellersprite__market_price_distribution` — `{"request": {"marketplace":"US", "nodeIdPath":"..."}}`
- 返回 `data` 是直接陣列（非 `{items: [...]}`），欄位：`label`(價格帶)、`products`、`units`、`unitsRatio`(0~1)

### 第3步: 獲取競品價格

`mcp__sellersprite__competitor_lookup` — `{"request": {"marketplace":"US", "nodeIdPath":"..."}}`

### 第4步: 儲存結果 + 生成報告

同時儲存原始資料和報告到 `{類別目錄}/`。

**報告結構：** 市場價格帶總覽 → 最佳定價帶 → Top競品定價 → 利潤空間 → 推薦定價策略 → 促銷策略建議
