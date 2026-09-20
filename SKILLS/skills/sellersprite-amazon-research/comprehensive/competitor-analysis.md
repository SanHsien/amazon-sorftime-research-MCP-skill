# 競品深度拆解

對競品 ASIN 進行全面拆解，覆蓋產品資訊、關鍵詞流量、趨勢和變體。

## 使用方式

```
/competitor-analysis [ASIN或關鍵詞] [站點]
```

## 工具呼叫

所有工具透過 MCP client 呼叫：`mcp__sellersprite__<tool_name>`

**引數模式**：大部分工具使用 `request` 巢狀物件；少量工具（`asin_detail`, `traffic_keyword_stat`, `keepa_info` 等）使用扁平引數。

**響應解析**：`result.content[0].text` 是 JSON 字串，需二次解析：
```python
raw = json.loads(result['content'][0]['text'])
data = raw.get('data', [])
```

## 執行步驟

### 第1步: 獲取競品列表（如輸入為關鍵詞）

呼叫 `mcp__sellersprite__competitor_lookup`：
- 引數：`{"request": {"marketplace":"US", "keyword":"..."}}`

若使用者直接提供 ASIN，跳過此步。

### 第2步: 並行獲取 ASIN 深度資料

1. **`mcp__sellersprite__asin_detail`** — 扁平引數 `{"marketplace":"US", "asin":"B0XXX"}`
2. **`mcp__sellersprite__traffic_keyword`** — `{"request": {"marketplace":"US", "asin":"B0XXX"}}`
3. **`mcp__sellersprite__keepa_info`** — 扁平引數 `{"marketplace":"US", "asin":"B0XXX"}`
   - 返回 `buyBox` 是 `[{timePoint, value}]` 陣列，取最後一項為當前價
   - `bsr` 同理取 `[{timePoint, value}]` 格式
4. **`mcp__sellersprite__traffic_source`** — `{"request": {"marketplace":"US", "asin":"B0XXX"}}`

### 第3步: 輔助資料

- `mcp__sellersprite__asin_prediction` — 扁平引數
- `mcp__sellersprite__asin_coupon_trend` — 扁平引數

### 第4步: 儲存結果

同時儲存兩份檔案：
1. **原始資料** → `{類別目錄}/research_data.json`
2. **分析報告** → `{類別目錄}/competitor_report.md`

### 第5步: 生成報告

**報告結構：** 競品概覽 → 銷量與趨勢 → 流量結構（自然/廣告佔比 0~1，展示×100）→ 關鍵詞覆蓋（rankPosition 取 .position）→ 定價促銷 → 變體分析 → SWOT → 應對策略
