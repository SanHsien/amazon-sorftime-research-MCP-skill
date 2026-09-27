# 第四步：標題結構設計

> **標題不是越長越好，也不是關鍵詞越多越好**。標題是 Listing 的"定位宣告"，要讓系統快速理解、讓買家快速決策。

## 🚨 本步不調 MCP

本步基於**第一步詞庫 + 第三步賣點證據庫**生成 3 版標題對比，不再呼叫 MCP 工具。

### 資料來源
- 關鍵詞優先順序：來自第一步 MCP `keyword_miner` / `keyword_research_trends` / `traffic_keyword` 的輸出
- 差異化屬性：來自第三步痛點-證據對映表
- 品牌名、規格：使用者提供

### ✅ 瀏覽器補充（可選）

```javascript
// 品牌官網（拿品牌定位詞）
mcp__web_reader__webReader({url:"https://yourbrand.com/about"})
```

---

## 一、黃金結構

```
[品牌] + [核心品類詞] + [關鍵差異化屬性] + [主使用場景] + [規格/數量] + [差異化價值（可選）]
```

### 案例：抗 UV 戶外模擬植物

```
Brand UV Resistant Artificial Flowers for Outdoors, 12 Bundles Realistic Faux Plants for Patio Garden Porch Planters, Fade Resistant Outdoor Decor
```

拆解：
- Brand = 品牌
- UV Resistant = 關鍵差異化屬性（L2 功能詞）
- Artificial Flowers = 核心品類詞（L1）
- for Outdoors = 主使用場景（L3）
- 12 Bundles = 規格（L5）
- Realistic Faux Plants = 同義詞擴充套件（L1 變體）
- for Patio Garden Porch Planters = 詳細場景（L3）
- Fade Resistant = 差異化價值（L2）
- Outdoor Decor = 類目定位（L1）

---

## 二、三大原則

### 原則 1：主詞靠前
系統從左到右理解權重，核心品類詞必須在前 5 個詞內出現。

✅ `Brand UV Resistant Artificial Flowers for Outdoors`
❌ `Brand Premium Quality Decor for Home Garden Patio - 12 Bundles UV Resistant Artificial Flowers`

### 原則 2：差異化屬性明確
不要用通用形容詞（premium / high quality / best），用具體功能詞（UV resistant / fade resistant / realistic）。

### 原則 3：場景精準，不要全塞
你的主場景是 patio / garden / porch，標題就講這三個，**不要把 cemetery / wedding / office / home 全塞進去**。

---

## 三、生成 3 個版本對比

| 版本 | 特點 | 適用場景 |
|------|------|---------|
| 關鍵詞覆蓋版 | 多埋詞，結構緊湊 | 廣告冷啟動、強競價品類 |
| 轉化表達版 | 可讀性優先，價值前置 | 自然排名沉澱、移動端 |
| 簡潔合規版 | 字數剋制，無誇大表達 | 高合規風險品類、新賬號 |

### 案例（抗 UV 戶外模擬植物）

| 版本 | 標題 | 優缺點 |
|------|------|--------|
| 關鍵詞覆蓋版 | Brand UV Resistant Artificial Flowers for Outdoors, 12 Bundles Realistic Faux Plants for Patio Garden Porch Planters, Fade Resistant Outdoor Decor | ✅ 核心詞全覆蓋；❌ 字數偏長 |
| 轉化表達版 | Brand 12-Bundle UV Resistant Artificial Flowers — Fade-Proof Outdoor Faux Plants for Patio & Porch Planters | ✅ 移動端友好；❌ 犧牲了 garden 場景 |
| 簡潔合規版 | Brand UV Resistant Artificial Flowers, 12 Bundles Faux Plants for Outdoor Patio Garden Planters | ✅ 安全合規；❌ 差異化弱 |

---

## 四、字數與字元規範

| 站點 | 字元上限 | 建議範圍 |
|------|---------|---------|
| 美國站（US） | 200 | 150-180（移動端友好） |
| 歐洲站（UK/DE/FR/IT/ES） | 200 | 150-180 |
| 日本站（JP） | 100（位元組） | 80-100 |
| 加拿大站（CA） | 200 | 150-180 |

> ⚠️ 移動端通常只展示前 80 字元，**前 80 字元必須包含核心詞 + 主賣點**。

---

## 五、給 Codex 的提示詞（本步專用）

詳見 `prompts/master-prompt.md` 第 5 步。精簡版：

> 輸入：詞庫（L1-L5）、痛點證據對映表、品牌名、規格、合規限制。
>
> 任務：
> 1. 生成 3 版標題（關鍵詞覆蓋版 / 轉化表達版 / 簡潔合規版）
> 2. 每版都遵循"品牌 + 核心詞 + 差異化屬性 + 主場景 + 規格"結構
> 3. 字元控制在 150-180
> 4. 前 80 字元必須包含核心詞 + 主賣點
> 5. 標註每版埋入的關鍵詞清單（對照詞庫）
> 6. 列出優缺點 + 適用場景
> 7. 推薦一版作為基礎版，並說明理由

---

## 六、常見錯誤（必須避免）

| 錯誤 | 示例 | 修正 |
|------|------|------|
| 通用形容詞堆砌 | Premium Quality Beautiful Artificial Flowers | 用功能詞替代 |
| 主詞靠後 | Brand Outdoor Decor for Home Garden - UV Resistant Artificial Flowers 12 Bundles | 主詞前置 |
| 全場景塞滿 | for Patio Garden Porch Cemetery Wedding Office Home Balcony | 只放主場景 |
| 重複關鍵詞 | Artificial Flowers UV Resistant Artificial Plants Outdoor Faux Flowers | 同義詞去重 |
| 包含競品品牌 | Better Than [Other Brand] Artificial Flowers | 移除競品詞 |
| 絕對化表達 | 100% No Fade Lifetime Warranty | 改穩健表達 |

---

## 七、輸出模板

```markdown
# 標題草稿對比 — {產品名}

## 版本 1：關鍵詞覆蓋版
**標題**：Brand UV Resistant Artificial Flowers for Outdoors, 12 Bundles Realistic Faux Plants for Patio Garden Porch Planters, Fade Resistant Outdoor Decor
**字元數**：178
**前 80 字元**：Brand UV Resistant Artificial Flowers for Outdoors, 12 Bundles Real
**埋入關鍵詞**：
- L1：artificial flowers, faux plants
- L2：UV resistant, fade resistant
- L3：outdoors, patio, garden, porch, planters
- L5：12 bundles

**優點**：核心詞全覆蓋，符合系統索引
**缺點**：字數偏長，移動端可能截斷
**適用**：廣告冷啟動

## 版本 2：轉化表達版
...

## 版本 3：簡潔合規版
...

## 推薦基礎版
**選擇**：版本 1
**理由**：[根據品類、賬號階段、廣告策略選擇]
```

---

## 八、檢查清單

- [ ] 3 個版本已生成
- [ ] 每版都遵循黃金結構
- [ ] 字元數在 150-180 之間
- [ ] 前 80 字元含核心詞 + 主賣點
- [ ] 無通用形容詞堆砌
- [ ] 無競品品牌詞
- [ ] 無絕對化表達
- [ ] 優缺點對比清晰，推薦理由合理
