# 第八步：QA 設計

> QA 在 Alexa/Rufus 對話式購物時代會越來越重要，**因為它天然就是問題和答案結構**。它是 Listing 的"答案型內容補丁"。

## 🚨 本步基於第二步資料，可選瀏覽器補充

本步主要基於**第二步問題庫 Top 10 + 第三步賣點證據庫**生成，不再呼叫 MCP 工具。

### ✅ 瀏覽器補充（MCP 無 QA 工具，允許）

```javascript
// 1. 競品 QA 板塊（補充 MCP 拿不到的問題）
mcp__web_reader__webReader({
  url:"https://www.amazon.com/ask-questions/B07XXX...",
  return_format:"text",
  retain_images:false
})

// 2. Reddit 真實買家提問（可選）
mcp__web_reader__webReader({url:"https://www.reddit.com/r/..."})
```

### ❌ 禁止行為

不要用瀏覽器抓競品評論湊問題，所有競品評論已在第二步透過 `review` MCP 拿到。

---

## 一、QA 的雙重作用

1. **承接自然語言搜尋** — 當使用者用完整問題提問時，QA 直接匹配
2. **補 Listing 沒講透的地方** — 標題五點不能太長，QA 可以補規格、適配、使用、維護、場景邊界

---

## 二、QA 來源

| 來源 | 優先順序 |
|------|--------|
| 第二步使用者問題庫 Top 10 | ⭐⭐⭐ |
| 競品 QA 板塊高頻問題 | ⭐⭐⭐ |
| 客服記錄 | ⭐⭐⭐ |
| 差評反饋的疑慮 | ⭐⭐⭐ |
| 5W1H 推演 | ⭐⭐ |

---

## 三、QA 寫法兩大原則

### 原則 1：回答要具體，不要只說 yes

✅ **好回答**：
> **Q: Will these artificial flowers fade in direct sunlight?**
> A: They are made with UV-resistant materials to help reduce fading during outdoor use, but like all outdoor decor, long-term extreme sun exposure may gradually affect color. For best longevity, shelter during severe weather.

✗ **差回答**：
> **Q: Will these fade?**
> A: Yes, they are fade-resistant.

### 原則 2：QA 補 Listing 沒講透的地方

| 型別 | 示例 QA |
|------|---------|
| 規格 | How many bundles do I need for a medium planter? |
| 適配 | Will these fit a 12-inch window box? |
| 使用 | Do I need to assemble anything? |
| 維護 | How do I clean them? |
| 場景邊界 | Can I use them in a bathroom with high humidity? |
| 風險 | Are they waterproof? Can they stay out in rain? |

---

## 四、抗 UV 戶外模擬植物 QA 完整示例

### Q1: Will these artificial flowers fade in direct sunlight?
**A**: They are made with UV-resistant materials to help reduce fading during outdoor use, but like all outdoor decor, long-term extreme sun exposure may gradually affect color. For best longevity, shelter during severe weather.
**埋入**：UV-resistant, fade, outdoor, sunlight

### Q2: Can I use them in outdoor planters?
**A**: Yes, the flexible stems can be inserted directly into planters, pots, baskets and porch boxes. Each bundle is shaped to mimic real blooms.
**埋入**：outdoor planters, flexible stems, planters, baskets

### Q3: Are the stems flexible enough to bend?
**A**: Yes, the stems are made of durable plastic with internal wire, allowing you to shape them naturally and fit different planter sizes.
**埋入**：flexible stems, plastic, planter

### Q4: How many bundles do I need for a medium planter?
**A**: For a 12-inch medium planter, 4-6 bundles create full coverage. The 12-bundle set fills 2-3 medium planters or one long window box.
**埋入**：12 bundles, medium planter, window box

### Q5: Do they look realistic up close?
**A**: Natural color variation and layered petals create a lifelike look from a distance. For very close inspection, the petals may feel slightly plastic to the touch.
**埋入**：realistic, natural color, layered petals, lifelike

### Q6: Are they waterproof? Can I leave them out in rain?
**A**: Yes, the materials are water-resistant and suitable for outdoor use in normal weather. For longest life, we recommend sheltering during heavy storms or extreme winds.
**埋入**：waterproof, water-resistant, outdoor, weather

### Q7: How tall are they?
**A**: Each bundle measures approximately 14-16 inches tall, suitable for medium and large planters.
**埋入**：size, inches, planters

### Q8: Will the color look fake or too bright?
**A**: The petals use natural color variation to avoid the over-saturated look common in cheap faux florals. Colors are designed to mimic real garden blooms.
**埋入**：color, natural, realistic, faux florals

### Q9: Is the packaging protective? Will they arrive deformed?
**A**: Each set is shipped with reinforced packaging to reduce transit damage. If any bundle arrives misshapen, gentle fluffing restores the shape.
**埋入**：packaging, reinforced, transit

### Q10: Can I use them for indoor decoration too?
**A**: Yes, while designed for outdoor use, they work well in indoor planters, vases, and centerpieces. The UV-resistant materials do not affect indoor use.
**埋入**：indoor, planters, vases, centerpieces

---

## 五、down filled pillows QA 示例（來自需求文件）

> 使用者輸入示例：產品特性 24x24 / bulk / fluffy；核心賣點 24x24；關鍵詞 down filled pillows / feather down pillow / down feather pillow / goose down pillows

### Q1: Are these pillows machine washable, or do they need dry cleaning?
**A**: These 24 x 24 down filled pillows are best maintained with spot cleaning or professional dry cleaning to preserve the fluffy feather down filling. Frequent machine washing may reduce the loft of the goose down fill over time.
**埋入**：24 x 24, down filled pillows, fluffy, feather down, goose down

### Q2: How fluffy are these pillows right out of the package?
**A**: Each 24 x 24 feather down pillow ships compressed. Allow 24-48 hours for the goose down fill to fully expand — the bulk down fill will reach maximum fluffy loft after a few hours of air exposure and gentle fluffing.
**埋入**：24 x 24, feather down pillow, goose down, bulk, fluffy

### Q3: Are these genuine goose down or a blend?
**A**: These down feather pillows use a feather down blend designed for balanced support and fluffy bulk. The 24 x 24 size provides medium-firm support suitable for side and back sleepers.
**埋入**：down feather pillow, goose down pillows, 24 x 24, fluffy, bulk

### Q4: What size pillow cover fits these?
**A**: Standard 24 x 24 inch pillow covers fit perfectly. The bulk filling holds shape well inside shams and decorative covers, making them ideal for couches, beds, and reading nooks.
**埋入**：24 x 24, bulk, down filled pillows

---

## 六、給 Codex 的提示詞（本步專用）

詳見 `prompts/master-prompt.md` 第 9 步。精簡版：

> 輸入：使用者問題庫 Top 10、產品規格、賣點證據庫、產品關鍵詞列表（必須埋入）。
>
> 任務：
> 1. 生成 10 個 QA，覆蓋 5 個決策環節（場景適配 / 痛點擔憂 / 規格確認 / 使用成本 / 信任）
> 2. 每個回答具體（不只用 yes/no），含場景邊界和注意事項
> 3. 每個回答自然埋入 2-3 個指定關鍵詞
> 4. 答案穩健，不誇大（如醫療/環保承諾）
> 5. 涵蓋至少 2 個"邊界問題"（如某場景是否適合、極端使用情況）
> 6. 模擬 Alexa/Rufus 可能問的自然語言變體

---

## 七、Alexa/Rufus 風格問題模板

對話式購物的問題特徵：
- 用完整句子問，不是短詞
- 含具體場景和約束（"for my front porch that gets full sun"）
- 含比較（"better than X for Y"）

### 模板
- "Which [product type] won't [problem] in [scenario]?"
- "Can I use [product] for [specific scenario]?"
- "Is [product] suitable for [user type] with [specific concern]?"
- "How does [product] compare to [alternative] for [use case]?"

---

## 八、輸出模板

```markdown
# QA 草稿 — {產品名}

## Q1: Will these artificial flowers fade in direct sunlight?
**A**: They are made with UV-resistant materials to help reduce fading during outdoor use, but like all outdoor decor, long-term extreme sun exposure may gradually affect color. For best longevity, shelter during severe weather.
**埋入關鍵詞**：UV-resistant, fade, outdoor, sunlight
**對應問題庫**：Q1
**對應賣點**：抗 UV
**Alexa 變體**："Which artificial flowers won't fade in full sun?"

## Q2-Q10: ...

## 檢查清單
- [x] 10 個 QA
- [x] 5 個決策環節覆蓋
- [x] 每個回答具體
- [x] 關鍵詞自然埋入
- [x] 無誇大承諾
- [x] 含至少 2 個邊界問題
```

---

## 九、檢查清單

- [ ] 至少 10 個 QA
- [ ] 5 個決策環節全覆蓋
- [ ] 每個回答具體（不只 yes/no）
- [ ] 每個回答埋入 2-3 個關鍵詞
- [ ] 無誇大承諾
- [ ] 至少 2 個邊界問題（極端場景）
- [ ] Alexa 自然語言變體已生成
- [ ] 與五點描述互補（不重複，補缺口）
