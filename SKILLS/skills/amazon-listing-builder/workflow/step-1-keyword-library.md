# 第一步：關鍵詞分層詞庫

> 不要把所有詞丟在一起，**按意圖分層**才能決定每個詞放哪裡。

## 🚨 必須先調 MCP（禁止瀏覽器抓 Amazon）

本步核心資料**必須**全部來自賣家精靈 MCP，**禁止**用 web reader 抓 Amazon 搜尋建議或關鍵詞頁。

### 必須呼叫的 MCP 工具（按順序）

```python
# 1. 主力擴詞（按種子詞擴充套件）
mcp__sellersprite__keyword_miner({
  "request": {"marketplace":"US", "keyword":"<種子詞>"}
})

# 2. 趨勢驗證（注意：扁平引數；欄位是 time/search/chainGrowth/yearlyGrowth）
mcp__sellersprite__keyword_research_trends({
  "marketplace":"US", "keyword":"<種子詞>"
})

# 3. 競品關鍵詞反查（必須傳競品 ASIN）
for asin in competitor_asins:  # 3-5 個競品
  mcp__sellersprite__traffic_keyword({
    "request": {"marketplace":"US", "asin":asin}
  })

# 4. 競品真實出單詞（用於排序詞庫優先順序）
for asin in competitor_asins:
  mcp__sellersprite__keyword_order({
    "request": {"marketplace":"US", "asin":asin}
  })
```

### ❌ 禁止行為

```javascript
// 錯誤：用瀏覽器抓 Amazon 搜詞建議
mcp__web_reader__webReader({url:"https://www.amazon.com/s?k=artificial+flowers"})
// 錯誤：用瀏覽器抓關鍵詞頁
mcp__web_reader__webReader({url:"https://www.amazon.com/s?k=..."})
```

### ✅ 瀏覽器補充（僅限）

- 自己的廣告搜尋詞報告：從賣家後臺手動下載（MCP 無）
- 自己的客服記錄：從賣家後臺匯出（MCP 無）

詳見 `reference/mcp-mandatory-protocol.md`。

---

## 一、為什麼要分層

舊方法：把 uv resistant artificial outdoor plants、outdoor artificial flowers、fake flowers outdoor 全塞標題，結果標題像詞庫垃圾桶。

新方法：按使用者搜尋意圖把詞分成 5 層，每層放在不同位置（標題 / 五點 / 描述 / ST / QA），讓系統理解關係，讓買家讀得下去。

---

## 二、五層詞庫結構

| 層級 | 名稱 | 示例（抗 UV 戶外模擬植物） | 建議位置 |
|------|------|--------------------------|---------|
| 1 | 核心品類詞 | artificial flowers / artificial plants / fake flowers / faux plants | 標題開頭 + 五點 + 描述 |
| 2 | 功能屬性詞 | UV resistant / fade resistant / weather resistant / waterproof / maintenance free | 標題 + 五點 1 |
| 3 | 場景詞 | outdoor / patio / garden / porch / planter / front door / cemetery / balcony | 標題 + 五點 3 + A+ |
| 4 | 問題詞 | won't fade in sun / for outdoor planters / looks real / no watering / full sun | 五點 + QA + A+ |
| 5 | 規格詞 | 12 bundles / plastic stems / 16 inch / flowers for pots | 標題 + 五點 4 |

---

## 三、欄位定義（每個關鍵詞都要標註）

| 欄位 | 說明 |
|------|------|
| `keyword` | 關鍵詞原文 |
| `layer` | 1-5（按上表） |
| `intent` | 搜尋意圖（如"功能+場景"） |
| `search_volume` | 月搜尋量（來自賣家精靈 keyword_miner） |
| `trend` | 趨勢（chainGrowth / yearlyGrowth，來自 keyword_research_trends） |
| `ppc` | 廣告建議價 |
| `click_concentration` | 點選集中度（0~1） |
| `conversion_concentration` | 轉化集中度（0~1） |
| `suggested_position` | 標題 / 五點 / 描述 / ST / QA |
| `must_frontend` | 是否必須前臺（true/false） |
| `priority` | P0（必放）/ P1（推薦）/ P2（補充） |

---

## 四、資料來源

| 來源 | 賣家精靈工具 | 備註 |
|------|------------|------|
| 種子詞擴充套件 | `keyword_miner` | 主力擴詞工具 |
| 全球熱詞參照 | `keyword_research` | 注意會忽略 keyword 引數，僅作趨勢參照 |
| 趨勢驗證 | `keyword_research_trends` | 欄位：`time` / `search` / `chainGrowth` / `yearlyGrowth` |
| 競品反查 | `traffic_keyword` + `keyword_order` | 找出競品真實出單詞 |
| 廣告搜尋詞報告 | 後臺下載 | 真實轉化資料 |
| 評論高頻詞 | `review` + 自定義 NLP | 注意 review 工具僅返回 20 條 |
| 站外內容詞 | TikTok / Reddit / Pinterest | 手動補充 |

---

## 五、合併去重與意圖分類規則

1. 全部詞合併到一張表，按 `keyword` 文字去重
2. 用關鍵詞本身判斷層級：
   - 含 brand/product 類名詞 → 第 1 層
   - 含 `resistant`/`proof`/`free`/`material` → 第 2 層
   - 含場景名詞（patio/garden/porch/...） → 第 3 層
   - 含問題句式（won't / how to / can I / for ...） → 第 4 層
   - 含數量/尺寸/規格 → 第 5 層
3. 一個詞可能跨多層（如 `uv resistant outdoor flowers` 同時屬 2+3），按主意圖歸類

---

## 六、輸出模板

```markdown
# 關鍵詞分層詞庫 — {產品名}

## L1 核心品類詞（必須前臺）
| 關鍵詞 | 月搜尋量 | 趨勢 | PPC | 建議位置 |
|--------|---------|------|-----|---------|
| artificial flowers | 95,000 | ↑12% | $0.85 | 標題 |
| ...  | ... | ... | ... | ... |

## L2 功能屬性詞
...

## L3 場景詞
...

## L4 問題詞
...

## L5 規格詞
...

## 後臺補充候選（同義詞/變體/錯拼）
...
```

---

## 七、給 Codex 的提示詞（本步專用）

詳見 `prompts/layered-keyword-prompt.md`。精簡版：

> 輸入：種子詞、產品核心賣點、賣家精靈關鍵詞資料、競品 ASIN、廣告搜尋詞報告、評論高頻詞。
>
> 任務：
> 1. 合併所有關鍵詞並去重
> 2. 按上述 5 層結構分類，標註每個欄位
> 3. 標記 must_frontend（核心詞、功能詞、主場景詞預設必前臺）
> 4. 輸出 Markdown 表格 + JSON 結構化資料
> 5. 標註缺失資料欄位（如某詞 PPC 缺失），不要編造

---

## 八、檢查清單

- [ ] 五層詞庫都至少有 5 個詞
- [ ] 每個核心詞都標註了 must_frontend=true
- [ ] 沒有把同一個詞重複放在不同層級
- [ ] 沒有把競品品牌詞（如其他賣家品牌）混進來
- [ ] 資料缺失欄位已標註，未編造
