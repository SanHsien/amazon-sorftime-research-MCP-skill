# 關鍵詞分層提示詞

> 用於第一步：把零散關鍵詞資料整理成 5 層結構化詞庫。

## 🚨 資料來源鐵律

**必須先調 MCP**，禁止用瀏覽器抓 Amazon 搜詞建議。

```python
# 必須按順序呼叫以下 MCP 工具
mcp__sellersprite__keyword_miner({"request":{"marketplace":"US","keyword":"<種子詞>"}})
mcp__sellersprite__keyword_research_trends({"marketplace":"US","keyword":"<種子詞>"})  # 扁平引數
for asin in competitor_asins:
    mcp__sellersprite__traffic_keyword({"request":{"marketplace":"US","asin":asin}})
    mcp__sellersprite__keyword_order({"request":{"marketplace":"US","asin":asin}})
```

❌ **嚴禁**：`webReader(amazon.com/s?k=...)` 抓 Amazon 搜尋頁湊詞
✅ **允許**：使用者自己提供的廣告搜尋詞報告（後臺匯出）

---

## 提示詞

```
你是一名亞馬遜關鍵詞分層專家。請把以下零散關鍵詞資料整理成 5 層結構化詞庫。

## 輸入資料
- 種子詞：[使用者填入，如 "artificial flowers outdoor"]
- 產品核心賣點：[使用者填入]
- 賣家精靈 keyword_miner 返回資料：[貼上 JSON]
- 賣家精靈 keyword_research_trends 返回資料：[貼上 JSON]
- 競品 ASIN 出單詞（來自 traffic_keyword）：[貼上]
- 廣告搜尋詞報告：[貼上]
- 評論高頻詞：[貼上]

## 任務

### 1. 合併去重
所有來源的關鍵詞合併，按文字去重。

### 2. 按 5 層分類
- L1 核心品類詞：品牌+產品核心名詞（artificial flowers / faux plants）
- L2 功能屬性詞：含 resistant / proof / free / material 等功能修飾
- L3 場景詞：含 patio / garden / porch 等場景名詞
- L4 問題詞：含 won't / how to / can I / for ... 等問題句式
- L5 規格詞：含數量、尺寸、顏色、形狀等規格
- L6 後臺補充：同義詞、變體詞、錯拼詞（前臺不出現）

### 3. 欄位標註（每個詞必須填全）
| 欄位 | 說明 |
|------|------|
| keyword | 關鍵詞原文 |
| layer | L1-L6 |
| intent | 搜尋意圖（如"功能+場景"） |
| search_volume | 月搜尋量（來自 keyword_miner） |
| chain_growth | 環比增長（來自 keyword_research_trends） |
| yearly_growth | 同比增長 |
| ppc_bid | 廣告建議價 |
| click_concentration | 點選集中度（0-1） |
| conversion_concentration | 轉化集中度（0-1） |
| suggested_position | 標題/五點/描述/ST/QA |
| must_frontend | true/false（核心詞、功能詞、主場景詞預設 true） |
| priority | P0/P1/P2 |

### 4. 缺失資料標註
如果某些欄位缺失（如某詞 PPC 拿不到），標註 "DATA_MISSING"，不要編造。

### 5. 排除規則
- 排除競品品牌詞（其他賣家品牌）
- 排除不相關的泛詞（如 "decor" 單獨出現）
- 排除誇大詞（best / #1）

### 6. 輸出格式

按層級分組輸出 Markdown 表格，並在最後輸出 JSON 結構化資料供後續步驟使用。

## 輸出模板

# 關鍵詞分層詞庫 — {產品名}

## L1 核心品類詞（必須前臺）
| 關鍵詞 | 月搜 | 趨勢 | PPC | 集中度 | 優先順序 | 建議位置 |
|--------|------|------|-----|--------|--------|---------|
| ...    | ...  | ...  | ... | ...    | ...    | 標題    |

## L2-L6：...

## 總結
- L1 詞數：X
- L2 詞數：X
- L3 詞數：X
- L4 詞數：X
- L5 詞數：X
- L6 詞數：X
- P0 優先順序：X 個
- DATA_MISSING：X 個（列表）
- 已排除：X 個（列表）
```

---

## 使用示例

### 輸入（種子詞：artificial flowers outdoor）
```
種子詞：artificial flowers outdoor
keyword_miner 返回：[JSON]
競品出單詞：uv resistant artificial outdoor plants, front porch planter flowers, ...
```

### 輸出（節選）
```
## L1 核心品類詞
| artificial flowers | 95,000 | +12% | $0.85 | 0.42 | P0 | 標題 |
| faux plants | 22,000 | +8% | $0.65 | 0.35 | P1 | 五點 |

## L2 功能屬性詞
| UV resistant | 18,000 | +25% | $1.20 | 0.55 | P0 | 標題 |
| fade resistant | 9,500 | +18% | $0.95 | 0.48 | P0 | 五點 1 |

...
```

---

## 檢查清單

- [ ] 5 層結構完整
- [ ] 每詞欄位齊全（缺失欄位標 DATA_MISSING）
- [ ] 無編造資料
- [ ] 排除了競品品牌詞
- [ ] P0 關鍵詞清晰
- [ ] 同時輸出 Markdown 表格和 JSON
