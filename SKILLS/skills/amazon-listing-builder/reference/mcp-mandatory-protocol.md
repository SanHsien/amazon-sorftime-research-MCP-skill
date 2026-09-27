# MCP 強制使用協議（核心鐵律）

> **資料來源優先順序：MCP（賣家精靈）> 瀏覽器**
>
> 核心資料必須走 MCP；瀏覽器僅作為 MCP 沒有覆蓋的資料的補充來源。

---

## 一、鐵律（必須遵守）

### 🚨 紅線 1：核心資料必須走 MCP

以下資料**禁止用瀏覽器抓取 Amazon**，必須使用賣家精靈 MCP 工具：

| 資料型別 | 必須使用的 MCP 工具 | 禁止行為 |
|---------|------------------|---------|
| 關鍵詞搜尋量 / PPC / 趨勢 | `keyword_miner` / `keyword_research_trends` | ❌ 瀏覽器搜 Amazon Suggest |
| 競品 ASIN 詳情（標題/五點/價格/評分） | `asin_detail` | ❌ 瀏覽器抓 Amazon 商品頁 |
| 競品關鍵詞反查 | `traffic_keyword` / `keyword_order` | ❌ 瀏覽器看 Amazon 搜尋建議 |
| 競品評論（含差評主題） | `review` | ❌ ❌ ❌ **瀏覽器抓 `amazon.com/product-reviews/...`** |
| 競品流量結構 | `traffic_listing` / `traffic_keyword_stat` | ❌ 瀏覽器看 BSR |
| 價格歷史 / BSR 歷史 | `keepa_info` | ❌ 瀏覽器查 Keepa 網站 |
| 市場價格分佈 | `market_price_distribution` | ❌ 瀏覽器翻列表 |
| 類目節點 | `product_node` | ❌ 瀏覽器搜 Amazon 類目樹 |
| 品牌 / 賣家分析 | `market_brand_concentration` | ❌ 瀏覽器手動統計 |

### ✅ 紅線 2：瀏覽器僅作必要補充

以下資料**MCP 拿不到**，允許使用瀏覽器（如 `mcp__web_reader__webReader`）：

| 資料型別 | 瀏覽器來源 | 說明 |
|---------|----------|------|
| 站外買家真實反饋 | Reddit / TikTok / Pinterest 評論 | MCP 不覆蓋站外 |
| 亞馬遜前臺 QA 板塊 | `amazon.com/ask-questions/...` | MCP 無 QA 工具 |
| 自己的客服記錄 | 賣家後臺 / 客服系統 | 私有資料，MCP 拿不到 |
| 自己的廣告搜尋詞報告 | 賣家後臺廣告報表 | 私有資料 |
| 自己的退貨報告 | 賣家後臺 | 私有資料 |
| 品牌官網 / 認證資訊 | 品牌官網 / CPSIA / FDA / RoHS 官網 | 驗證合規性 |
| Google Trends | `trends.google.com` | MCP 無（但有 `google_trend` 工具，優先用 MCP） |
| 競品品牌詞識別 | 競品 ASIN 的品牌名 | 先用 `asin_detail` 拿品牌，再人工排除 |

### 🔧 紅線 3：資料缺失時正確處理

如果 MCP 呼叫失敗或資料不完整：
1. **先重試 1 次**（可能是網路瞬時問題）
2. **檢查引數是否正確**（參考 `reference/sellersprite-mcp-integration.md` 第八節常見陷阱）
3. **如果仍然失敗，標註 `DATA_MISSING`**，列出需要人工補充的欄位
4. **絕對禁止**用瀏覽器抓 Amazon 頁面來"湊資料"

---

## 二、八步工作流的 MCP 呼叫順序

每一步開始前，必須先調 MCP 工具拿真實資料，再讓 AI 分析。**順序不能顛倒**。

### 第一步：關鍵詞分層詞庫

```python
# 必須按順序呼叫以下 MCP 工具
# 1. 關鍵詞挖掘（主力擴詞）
mcp__sellersprite__keyword_miner({
  "request": {"marketplace":"US", "keyword":"<種子詞>"}
})

# 2. 關鍵詞趨勢驗證（欄位：time/search/chainGrowth/yearlyGrowth）
mcp__sellersprite__keyword_research_trends({
  "marketplace":"US", "keyword":"<種子詞>"   # 注意：扁平引數
})

# 3. 競品關鍵詞反查（找出競品真實出單詞）
for asin in competitor_asins:
  mcp__sellersprite__traffic_keyword({
    "request": {"marketplace":"US", "asin":asin}
  })

# 4. 競品出單詞（用於詞庫優先順序排序）
for asin in competitor_asins:
  mcp__sellersprite__keyword_order({
    "request": {"marketplace":"US", "asin":asin}
  })
```

**瀏覽器補充**：無（關鍵詞資料 MCP 全覆蓋）

---

### 第二步：使用者問題庫

```python
# 1. 競品差評（必走 MCP，禁止瀏覽器抓評論頁）
for asin in competitor_asins:
  mcp__sellersprite__review({
    "marketplace":"US", "asin":asin
  })
  # ⚠️ 注意：每次最多返回 20 條，是樣本資料

# 2. 競品 Listing 結構（拿五點和描述參考）
for asin in competitor_asins:
  mcp__sellersprite__asin_detail({
    "marketplace":"US", "asin":asin
  })
```

**瀏覽器補充**（僅這些場景允許）：
```javascript
// 1. 競品 QA 板塊（MCP 無 QA 工具）
mcp__web_reader__webReader({
  url: "https://www.amazon.com/ask-questions/B0XXXXXXX",
  return_format: "text",
  retain_images: false
})

// 2. Reddit / TikTok 站外買家反饋
mcp__web_reader__webReader({
  url: "https://www.reddit.com/r/.../...",
  return_format: "text"
})

// ❌ 錯誤示例：抓 Amazon 評論頁
// mcp__web_reader__webReader({
//   url: "https://www.amazon.com/product-reviews/B07PQFT83F?filterByStar=critical"
// })
```

---

### 第三步：賣點證據庫

**主要靠人工**（供應鏈資訊、測試資料、認證），MCP 不提供產品內部資料。

```python
# 可呼叫：競品評論中的好評（提取"客戶認可的證據"）
mcp__sellersprite__review({
  "marketplace":"US", "asin":"<自己的ASIN>"
})
```

**瀏覽器補充**：
- 品牌官網（驗證材料承諾）
- 認證機構官網（驗證 CPSIA / FDA / RoHS 等證書真實性）

---

### 第四步：標題結構設計

**不再調 MCP**。基於第一、二、三步的資料生成 3 版標題對比。

---

### 第五步：五點描述

**不再調 MCP**。基於痛點-證據對映表生成。

---

### 第六步：描述 + A+ 內容

**不再調 MCP**。基於敘事流生成。

**瀏覽器補充**：
- 品牌官網（拿品牌定位語言）
- 競品 A+ 模組（如想參考結構）

---

### 第七步：Search Terms

**不再調 MCP**。基於第一步詞庫 + 第四步標題，做差集運算（找出未在前臺出現的詞）。

---

### 第八步：QA 設計

基於第二步問題庫生成。

**瀏覽器補充**（可選）：
- 競品 QA 板塊（補充 MCP 拿不到的問題）
- Reddit 真實買家提問

---

## 三、上線後迭代的 MCP 呼叫

```python
# 1. 自己 ASIN 的流量診斷
mcp__sellersprite__traffic_listing({
  "request":{"marketplace":"US","asin":"<自己的ASIN>"}
})

# 2. 自己 ASIN 的出單詞
mcp__sellersprite__keyword_order({
  "request":{"marketplace":"US","asin":"<自己的ASIN>"}
})

# 3. 價格分佈
mcp__sellersprite__market_price_distribution({
  "request":{"marketplace":"US","nodeIdPath":"<類目>"}
})

# 4. 自己 Listing 的評論反饋（監控差評主題）
mcp__sellersprite__review({
  "marketplace":"US","asin":"<自己的ASIN>"
})
```

**自己後臺資料（瀏覽器 / 後臺匯出）**：
- 廣告搜尋詞報告（後臺 Reports → Advertising）
- 客戶 QA（後臺 Buyer-Seller Messaging）
- 退貨報告（後臺 Returns）
- BSR 排名歷史（用 MCP `keepa_info`）

---

## 四、呼叫前的檢查清單

每次開始八步工作流前，必須確認：

- [ ] `.mcp.json` 配置正確（URL + headers.secret-key）
- [ ] MCP 客戶端能成功呼叫 `mcp__sellersprite__product_node` 測試工具
- [ ] 目標 ASIN 已確認（自己的 + 3-5 個競品）
- [ ] 類目節點 nodeIdPath 已查到（用 `product_node` 工具）
- [ ] 站點確認（US / UK / DE / JP）

如果 MCP 呼叫失敗，**先排查**，不要用瀏覽器抓 Amazon 湊資料。

---

## 五、常見錯誤對比

| 場景 | ❌ 錯誤做法 | ✅ 正確做法 |
|------|-----------|-----------|
| 抓競品評論 | `webReader(amazon.com/product-reviews/B07X...)` | `mcp__sellersprite__review({asin:"B07X..."})` |
| 抓競品標題 | `webReader(amazon.com/dp/B07X...)` | `mcp__sellersprite__asin_detail({asin:"B07X..."})` |
| 拿關鍵詞搜尋量 | `webReader(Amazon 搜尋建議)` | `mcp__sellersprite__keyword_miner({keyword:"..."})` |
| 看 BSR 歷史 | `webReader(keepa.com)` | `mcp__sellersprite__keepa_info({asin:"..."})` |
| 看價格分佈 | `webReader(翻 Amazon 列表)` | `mcp__sellersprite__market_price_distribution` |
| 看 Reddit 評論 | ✅ `webReader(reddit.com/r/...)` | MCP 無此資料 |
| 看競品 QA 板塊 | ✅ `webReader(amazon.com/ask-questions/...)` | MCP 無 QA 工具 |
| 驗證 FDA 認證 | ✅ `webReader(fda.gov)` | MCP 無認證查詢 |

---

## 六、為什麼不能用瀏覽器抓 Amazon

| 問題 | 說明 |
|------|------|
| 反爬蟲封鎖 | Amazon 會快速封鎖抓取 IP，資料不完整 |
| 資料結構易變 | HTML 結構變動導致指令碼失效 |
| 評論資料不全 | Amazon 前臺評論有分頁、篩選、隱藏 |
| 缺少核心欄位 | 瀏覽器抓不到搜尋量、PPC、轉化集中度等核心資料 |
| 合規風險 | 抓取 Amazon 資料違反其 ToS |
| 效率低 | MCP 一次呼叫拿全欄位，瀏覽器要多次請求 |
| 資料已結構化 | MCP 返回 JSON，瀏覽器返回 HTML 需要解析 |

**結論**：MCP 是第一手結構化資料來源，瀏覽器只是"必要補充"，不是"主要通道"。

---

## 七、違規自檢

每次跑完 skill，自檢以下問題：

- [ ] 第一步是否呼叫了 `keyword_miner`？（不是瀏覽器搜 Amazon）
- [ ] 第二步是否呼叫了 `review`？（不是瀏覽器抓評論頁）
- [ ] 第二步是否呼叫了 `asin_detail`？（不是瀏覽器抓商品頁）
- [ ] 瀏覽器呼叫是否僅限於：Reddit / TikTok / 競品 QA 板塊 / 官網驗證？
- [ ] 所有 MCP 失敗的欄位是否標註 `DATA_MISSING`？

如果以上任何一項不透過，**重新跑**該步驟，不要湊資料。
