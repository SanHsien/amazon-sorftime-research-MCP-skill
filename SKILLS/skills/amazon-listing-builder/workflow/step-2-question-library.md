# 第二步：使用者問題庫

> 新演算法語境下，**問題庫比關鍵詞庫更重要**。因為 Alexa/Rufus/對話式購物的本質是：買家不搜短詞，而是問問題。

## 🚨 必須先調 MCP（核心資料禁止瀏覽器抓 Amazon）

本步的**競品評論和競品 Listing 結構**必須用 MCP，**嚴禁**用 web reader 抓 `amazon.com/product-reviews/` 或 `amazon.com/dp/` 頁面。

### 必須呼叫的 MCP 工具

```python
# 1. 競品差評（使用者問題庫最核心來源）
for asin in competitor_asins:  # 3-5 個競品
  mcp__sellersprite__review({
    "marketplace":"US", "asin":asin  # 注意：扁平引數
  })
  # ⚠️ 每次最多返回 20 條，是樣本資料，需多次呼叫或多 ASIN 取並集

# 2. 競品 Listing（拿標題/五點/描述/A+ 結構參考）
for asin in competitor_asins:
  mcp__sellersprite__asin_detail({
    "marketplace":"US", "asin":asin
  })

# 3. 競品流量結構（看主力出單詞反映的需求）
for asin in competitor_asins:
  mcp__sellersprite__traffic_keyword({
    "request": {"marketplace":"US", "asin":asin}
  })
```

### ❌ 嚴禁的錯誤做法

```javascript
// 錯誤：用瀏覽器抓 Amazon 評論頁
mcp__web_reader__webReader({
  url:"https://www.amazon.com/product-reviews/B07PQFT83F?filterByStar=critical&pageNumber=1"
})
// 錯誤：用瀏覽器抓商品詳情頁
mcp__web_reader__webReader({url:"https://www.amazon.com/dp/B07XXX..."})
```

### ✅ 瀏覽器補充（MCP 無對應工具，允許）

```javascript
// 1. 競品 QA 板塊（MCP 無 QA 工具）
mcp__web_reader__webReader({
  url:"https://www.amazon.com/ask-questions/B07XXX...",
  return_format:"text",
  retain_images:false
})

// 2. 站外買家真實反饋
mcp__web_reader__webReader({url:"https://www.reddit.com/r/..."})
mcp__web_reader__webReader({url:"https://www.tiktok.com/..."})
```

詳見 `reference/mcp-mandatory-protocol.md`。

---

## 一、為什麼要建問題庫

如果使用者問 "Will these flowers fade in direct sunlight?"，你的 Listing 沒有回答這個問題 → 系統不會推薦你。

問題庫的作用：
1. **QA 內容來源** — 直接把高頻問題做成 QA
2. **五點描述的"答案"邏輯** — 每一點回答一個使用者疑慮
3. **A+ 模組結構** — 用一屏回答一個大問題
4. **語義覆蓋校驗** — 檢查 Listing 是否覆蓋了所有高頻問題

---

## 二、問題來源

| 來源 | 工具/方法 | 優先順序 |
|------|----------|--------|
| 競品 1-3 星差評 | `review` + ASIN 反查 | ⭐⭐⭐ |
| 競品 QA 板塊 | 亞馬遜前臺手動抓取 | ⭐⭐⭐ |
| 自己客服記錄 | 後臺 Customer Q&A | ⭐⭐⭐ |
| Reddit / TikTok 評論 | 站外搜產品類目 | ⭐⭐ |
| 廣告搜尋詞報告 | 後臺下載，找問句式 | ⭐⭐ |
| 買家退貨原因 | 後臺 Return Report | ⭐⭐ |
| 5W1H 推演 | 見下方"問題框架" | ⭐ |

---

## 三、問題框架（5W1H + 決策鏈）

按購買決策階段拆分問題：

### 階段 1：是否適合我？（場景適配）
- Can I use these in [場景]?
- Will it work for [用途]?
- Is this suitable for [人群]?

### 階段 2：會不會有 XX 問題？（痛點擔憂）
- Will it [褪色/變形/損壞]?
- Does it really [效果承諾]?
- Is it [真實/耐用/安全]?

### 階段 3：規格對嗎？（引數確認）
- What size is it?
- How many [bundles/pieces]?
- Will it fit my [容器/位置]?

### 階段 4：怎麼用？（使用成本）
- How do I install/setup?
- Do I need [額外配件]?
- Is it easy to [維護/清潔]?

### 階段 5：出了問題怎麼辦？（信任）
- What if I don't like it?
- Is there a warranty?
- How is the packaging?

---

## 四、抗 UV 戶外模擬植物案例

| # | 問題 | 高頻來源 | 對應賣點 | Listing 位置 |
|---|------|---------|---------|------------|
| 1 | Will these flowers fade in direct sunlight? | 差評 + QA | 抗 UV 材料 | 五點 1 + QA |
| 2 | Can I use them in outdoor planters? | QA | 靈活枝幹 | 五點 3 + QA |
| 3 | Are the stems flexible enough to bend? | QA | 可塑枝幹 | 五點 5 |
| 4 | How many bundles do I need for a medium planter? | QA | 數量建議 | 五點 4 + QA |
| 5 | Do they look realistic up close? | 差評 | 花瓣層次 | 五點 2 + A+ |
| 6 | Will they fall apart or shed? | 差評 | 加固工藝 | 五點 5 |
| 7 | Can I leave them outside in rain? | QA | 防水 | QA |
| 8 | How tall are they? | QA | 規格 | 五點 4 |
| 9 | Will the color look fake? | 差評 | 自然色差 | 五點 2 + A+ |
| 10 | Is the packaging protective? | 差評 | 加固包裝 | 五點 5 + A+ |

---

## 五、欄位定義

| 欄位 | 說明 |
|------|------|
| `question` | 問題原文（英文） |
| `frequency_source` | 來源（差評/QA/Reddit/客服） |
| `frequency_score` | 出現頻次（1-5） |
| `corresponding_feature` | 對應賣點 |
| `corresponding_keyword` | 對應可埋關鍵詞 |
| `listing_position` | 五點 N / QA / A+ 第 N 屏 |
| `natural_language_form` | 自然語言搜尋變體（Alexa 可能問的） |

---

## 六、給 Codex 的提示詞（本步專用）

> 輸入：競品 ASIN 列表、產品核心賣點、產品規格、客戶評論資料、客服記錄（如有）。
>
> 任務：
> 1. 從評論差評提取 30+ 個使用者問題
> 2. 從競品 QA 板塊提取 20+ 個使用者問題
> 3. 用 5W1H 框架補全所有決策環節
> 4. 按頻次打分（1-5），保留 Top 20
> 5. 標註每個問題對應的賣點、關鍵詞、Listing 位置
> 6. 生成 Alexa/Rufus 可能問的自然語言變體（問題型搜尋）

---

## 七、輸出模板

```markdown
# 使用者問題庫 — {產品名}

## Top 10 高頻問題（必須覆蓋）

### Q1: Will these flowers fade in direct sunlight?
- 頻次：⭐⭐⭐⭐⭐
- 來源：差評（出現 18 次）+ QA（出現 12 次）
- 對應賣點：抗 UV 材料
- 對應關鍵詞：UV resistant / fade resistant / won't fade in sun
- 建議位置：五點 1 + QA + A+ 第 2 屏
- Alexa 變體："Which artificial flowers won't fade in full sun?"

## Q2-Q10: ...

## 次高頻問題（11-20）
...
```

---

## 八、檢查清單

- [ ] 至少覆蓋 20 個問題
- [ ] 5 個決策階段都有問題
- [ ] 每個問題都標註了對應賣點
- [ ] Alexa 自然語言變體已生成
- [ ] 差評高頻問題已 100% 覆蓋（差評 = 痛點真相）
