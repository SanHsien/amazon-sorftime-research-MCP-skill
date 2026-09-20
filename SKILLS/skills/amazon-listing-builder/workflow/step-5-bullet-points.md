# 第五步：五點描述

> **五點不是參數列，而是購買決策鏈**。每一點回答一個使用者疑慮，推動買家做決策。

## 🚨 本步不調 MCP

本步基於**第一步詞庫 + 第二步問題庫 Top 5 + 第三步痛點-證據對映表**生成五點，不再呼叫 MCP 工具。

### 資料來源
- 每點對應的賣點：第三步證據庫
- 每點埋入的關鍵詞：第一步詞庫
- 每點回答的使用者疑慮：第二步問題庫
- 字元限制：基於目標站點規範

### ❌ 禁止行為

不要用瀏覽器抓競品五點湊內容，所有競品五點參考已在第二步透過 `asin_detail` MCP 拿到。

---

## 一、五點 = 五個決策環節

| 點位 | 決策環節 | 回答的問題 | 示例（抗 UV 戶外模擬植物） |
|------|---------|----------|---------------------------|
| 1 | 核心價值 | 為什麼這個產品適合 XX 場景？ | Designed for Outdoor Sunlight（抗 UV） |
| 2 | 痛點解決 | 會不會有 XX 問題？ | Realistic Color and Layered Petals（真實感） |
| 3 | 使用場景 | 適合哪些具體場景？ | Perfect for Porch, Patio and Garden Planters |
| 4 | 規格使用 | 數量多少？怎麼用？ | 12 Bundles, Flexible Stems for Direct Insertion |
| 5 | 信任風險 | 包裝/維護/售後？ | Protective Packaging and Maintenance-Free |

---

## 二、寫法原則

### 原則 1：每一點一句話承諾 + 一句證據

✅ **第 1 點示例**：
> **Designed for Outdoor Sunlight** — Made with UV-resistant materials to help reduce fading in patio, porch and garden use.

✗ **錯誤示例（堆詞無證據）**：
> **Premium Quality**：High quality material, perfect for any occasion, great for home and garden.

### 原則 2：關鍵詞自然融入，不堆砌

把 L2 功能詞、L3 場景詞、L4 問題詞自然融入，不是塞進去。

✅ `Made with UV-resistant materials to help reduce fading in patio, porch and garden use.`
- 含 UV-resistant（L2）、fading（L4）、patio/porch/garden（L3）

### 原則 3：禁用空泛詞

| 禁用 | 用具體賣點替代 |
|------|--------------|
| Premium quality | 寫具體材料 / 工藝 |
| Perfect for any occasion | 寫具體場景 |
| Easy to use | 寫具體怎麼用 |
| Great gift | 寫適合什麼人送禮 |
| High performance | 寫具體資料 |

---

## 三、抗 UV 戶外模擬植物完整示例

### Point 1: Designed for Outdoor Sunlight
Made with UV-resistant materials to help reduce fading in patio, porch and garden use.

**埋入**：UV-resistant（L2）、outdoor、sunlight、fading（L4）、patio、porch、garden（L3）

### Point 2: Realistic Color and Layered Petals
Natural color variation and fuller flower heads create a more lifelike look from a distance.

**埋入**：realistic、lifelike（L2）、natural color（L4 變體）

### Point 3: Perfect for Porch, Patio and Garden Planters
Flexible stems can be directly inserted into planters, baskets and porch boxes for instant outdoor decor.

**埋入**：porch、patio、garden、planters（L3）、flexible stems、direct insertion（L4）

### Point 4: 12 Bundles for Full Arrangements
Each set includes 12 bundles of faux plants, enough to fill 2-3 medium planters or one long window box.

**埋入**：12 bundles（L5）、planters、window box（L3）

### Point 5: Protective Packaging and Maintenance-Free
Shipped with reinforced packaging to reduce transit damage. No watering, no trimming — keeps outdoor spaces colorful all season.

**埋入**：protective packaging（L4）、maintenance-free、no watering（L2/L4）

---

## 四、字元規範

| 站點 | 單點字元上限 | 建議範圍 |
|------|------------|---------|
| 美國站 | 500 | 200-300 |
| 歐洲站 | 500 | 200-300 |
| 日本站 | 250（位元組） | 150-200 |

每點結構：**加粗賣點標題（5-8 詞）+ 短句承諾 + 長句證據**。

---

## 五、給 Codex 的提示詞（本步專用）

> 輸入：痛點-證據對映表（第三步）、關鍵詞分層詞庫（第一步）、使用者問題庫 Top 5（第二步）、產品規格、合規限制。
>
> 任務：
> 1. 嚴格按 5 個決策環節生成五點
> 2. 每點結構：加粗賣點標題 + 1 句承諾 + 1-2 句證據
> 3. 每點埋入至少 3 個關鍵詞（來自不同層級）
> 4. 禁用空泛詞清單（premium / perfect / easy / great gift / high performance）
> 5. 字元控制在 200-300 之間
> 6. 每點對應一個使用者問題（來自問題庫 Top 5）
> 7. 不誇大，不絕對化

---

## 六、給 Codex 的禁忌詞清單

直接傳給 AI：

```
禁用詞清單（絕對不能出現在五點中）：
- Premium quality / High quality
- Perfect for any occasion / Perfect for everyone
- Great gift / Best gift
- 100% / Lifetime / Never / Always
- Eco-friendly（無認證）
- FDA approved（無認證）
- Cures / Treats / Heals（醫療）
- Best / Number 1 / Top rated
- Cheap / Lowest price

替換規則：
- premium quality → 寫具體材料（如 PE plastic / stainless steel）
- perfect for any occasion → 寫具體 2-3 個場景
- great gift → 寫具體適合什麼人（如 for housewarmings, for Mother's Day）
- 100% no fade → help reduce fading
```

---

## 七、輸出模板

```markdown
# 五點描述草稿 — {產品名}

## Point 1: Designed for Outdoor Sunlight
**加粗賣點標題**：Designed for Outdoor Sunlight
**正文**：Made with UV-resistant materials to help reduce fading in patio, porch and garden use.
**字元數**：118
**埋入關鍵詞**：UV-resistant（L2）、outdoor、sunlight、fading（L4）、patio、porch、garden（L3）
**對應問題**：Q1 - Will these flowers fade in direct sunlight?
**合規檢查**：✅ 用 "help reduce" 而非 "no fade"

## Point 2-5: ...

## 檢查結果
- [x] 5 個決策環節全覆蓋
- [x] 每點埋入 3+ 關鍵詞
- [x] 無禁用詞
- [x] 無絕對化表達
- [x] 字元數 200-300 之間
```

---

## 八、檢查清單

- [ ] 5 個決策環節全覆蓋（核心價值 / 痛點 / 場景 / 規格 / 信任）
- [ ] 每點都有具體證據，無空話
- [ ] 禁用詞全部規避
- [ ] 每點埋入 3+ 關鍵詞
- [ ] 每點對應一個使用者問題
- [ ] 合規檢查透過
- [ ] 字元數符合規範
