# 案例：down filled pillows QA（Alexa 風格）

> 來自需求文件的示例：基於 Alexa 演算法做 QA 問答，在 QA 中自然埋入指定關鍵詞。

---

## 輸入資訊

- **品類**：Down filled pillows（羽絨枕）
- **產品特性**：24 x 24 / bulk / fluffy
- **核心賣點**：24 x 24（尺寸規格）
- **必須埋入的關鍵詞**：
  - down filled pillows
  - feather down pillow
  - down feather pillow
  - goose down pillows
- **目標**：模擬 Alexa 演算法下客戶可能問的問題及答案

---

## 設計思路

按需求文件要求，從 4 個維度構建 QA：
1. **產品應用場景**（用在哪些場景）
2. **產品功能**（規格、效能、特性）
3. **產品適用人群**（適合誰）
4. **產品使用方式**（怎麼用）

每題答案具體不空泛，自然埋入關鍵詞，不堆砌。

---

## 完整 QA（10 題）

### 場景類（產品應用場景）

**Q1: Can I use these pillows for both sleeping and as decorative throw pillows?**
A: Yes, the 24 x 24 down filled pillows work well for both. The fluffy feather down filling provides soft support for back sleeping, while the bulk fill holds shape inside decorative shams for couches, beds, and reading nooks.

> 埋入：24 x 24, down filled pillows, fluffy, feather down, bulk

**Q2: Are these suitable for a guest room or Airbnb setup?**
A: Yes, these 24 x 24 feather down pillows are popular for guest rooms, Airbnb, and hospitality use. The bulk filling provides a premium feel without the premium price tag of luxury goose down pillows, and the 24 x 24 size fits standard euro shams.

> 埋入：24 x 24, feather down pillow, goose down pillows, bulk

**Q3: Will these pillows work on a sectional sofa?**
A: Yes, the 24 x 24 down filled pillows are an ideal size for sectional sofas and oversized armchairs. The fluffy feather down fill keeps the corners full, and the bulk filling prevents the pillow from going flat after regular use.

> 埋入：24 x 24, down filled pillows, fluffy, feather down, bulk

### 功能類（產品功能）

**Q4: How fluffy are these pillows right out of the package?**
A: Each 24 x 24 feather down pillow ships compressed. Allow 24-48 hours for the goose down fill to fully expand — the bulk down fill will reach maximum fluffy loft after a few hours of air exposure and gentle fluffing.

> 埋入：24 x 24, feather down pillow, goose down, bulk, fluffy, down fill

**Q5: Are these pillows firm or soft?**
A: These down feather pillows have a medium-plush feel. The 24 x 24 size combined with the bulk feather down fill creates a balance between cushioning softness and structural support — ideal for back sleepers and decorative use.

> 埋入：down feather pillow, 24 x 24, bulk, feather down

**Q6: Are these genuine goose down or a blend?**
A: These down feather pillows use a feather down blend designed for balanced support and fluffy bulk. The 24 x 24 size provides medium-firm support suitable for side and back sleepers.

> 埋入：down feather pillow, goose down pillows, 24 x 24, fluffy, bulk

**Q7: Are these pillows machine washable, or do they need dry cleaning?**
A: These 24 x 24 down filled pillows are best maintained with spot cleaning or professional dry cleaning to preserve the fluffy feather down filling. Frequent machine washing may reduce the loft of the goose down fill over time.

> 埋入：24 x 24, down filled pillows, fluffy, feather down, goose down

### 適用人群類

**Q8: Are these pillows suitable for side sleepers?**
A: The 24 x 24 size and bulk feather down fill provide enough loft for most side sleepers, though stomach sleepers may prefer a flatter profile. The down filled pillows work best for back sleepers and as decorative throw pillows.

> 埋入：24 x 24, bulk, feather down, down filled pillows

### 使用方式類

**Q9: What size pillow cover fits these?**
A: Standard 24 x 24 inch pillow covers fit perfectly. The bulk filling holds shape well inside shams and decorative covers, making them ideal for couches, beds, and reading nooks.

> 埋入：24 x 24, bulk, down filled pillows

**Q10: How do I keep them fluffy over time?**
A: Fluff the 24 x 24 feather down pillows daily when making the bed. Air them out monthly in fresh air for 1-2 hours, and use a 24 x 24 protective cover to keep the bulk goose down fill clean. Avoid heavy compression in storage.

> 埋入：24 x 24, feather down pillow, bulk, goose down

---

## Alexa 自然語言變體

模擬 Alexa/Rufus 可能問的完整問題：

| 短詞搜尋 | Alexa 自然語言變體 | QA 對應 |
|---------|------------------|--------|
| down pillows for sleeping | "Which down pillows work for both sleeping and decoration?" | Q1 |
| fluffy 24x24 pillow | "How fluffy are these 24 by 24 pillows out of the package?" | Q4 |
| pillow for sectional sofa | "Are these 24 inch pillows good for a sectional sofa?" | Q3 |
| goose down pillow bulk | "Are these genuine goose down or a blend?" | Q6 |
| washable down pillow | "Can I machine wash these down pillows?" | Q7 |

---

## 關鍵詞覆蓋檢查

| 關鍵詞 | 出現次數 | QA 編號 |
|--------|---------|---------|
| down filled pillows | 6 | Q1, Q3, Q7, Q8, Q9 + Alexa |
| feather down pillow | 7 | Q1, Q2, Q3, Q5, Q6, Q7, Q10 |
| down feather pillow | 2 | Q5, Q6 |
| goose down pillows | 4 | Q2, Q6, Q7, Q10 |
| 24 x 24 | 10 | 每題都有 |
| fluffy | 6 | Q1, Q3, Q4, Q6, Q7, Q10 |
| bulk | 7 | Q1, Q2, Q3, Q5, Q6, Q8, Q9, Q10 |

✅ 所有關鍵詞均自然埋入，無堆砌感。

---

## 設計要點總結

1. **每題答案 60-120 字**，不只 yes/no
2. **關鍵詞自然出現 2-4 次/題**（不堆砌）
3. **覆蓋 4 個維度**：場景 / 功能 / 人群 / 使用
4. **場景邊界明確**（如"stomach sleepers may prefer flatter"）
5. **預期管理**（如"machine washing may reduce loft"）
6. **埋入規格證據**（24 x 24、bulk、fluffy 反覆出現）

---

## 給 Codex 的提示詞模板（基於此案例）

```
我是亞馬遜美國站賣家，銷售的產品為：[產品名]，現在要根據亞馬遜最新 Alexa 演算法做 QA 問答。請根據產品特性及核心賣點，模擬 Alexa 演算法下客戶可能提問的問題及答案（從產品應用場景 / 產品功能 / 產品適用人群 / 產品使用方式著手），並在 QA 中自然埋入下列產品關鍵詞。用英文輸出。

產品特性：[填，如 24 x 24 / bulk / fluffy]
產品核心賣點：[填]
關鍵詞：
- [關鍵詞 1]
- [關鍵詞 2]
- [關鍵詞 3]
- [關鍵詞 4]

要求：
1. 生成 10 個 QA
2. 每 Q 答案 60-120 字，不只 yes/no
3. 關鍵詞自然出現 2-4 次/題，不堆砌
4. 覆蓋 4 個維度（場景/功能/人群/使用）
5. 每題明確場景邊界，做預期管理
6. 模擬 5 個 Alexa 自然語言變體
7. 輸出關鍵詞覆蓋檢查表
```
