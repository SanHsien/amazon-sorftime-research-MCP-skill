# 第四步：標題 + 商品亮點分層設計（Item Name + Item Highlights）

> **2026-07-27 起美國站前臺標題結構已改為雙欄位**（圖書/音樂/影音等媒介類目除外）：Item Name（75 字元）+ Item Highlights（125 字元）。合計仍是 200 字元，資訊量沒砍，只是重新分層：**標題管身份識別，亮點管比較輔助**。標題不是越長越好，也不是關鍵詞越多越好。

## 🚨 本步不調 MCP

本步基於**第一步詞庫 + 第三步賣點證據庫**生成 3 版"標題 + 亮點"組合對比，不再呼叫 MCP 工具。

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

## 一、2026 新規：75 + 125 = 200 雙欄位結構

| 欄位 | 字元上限 | 定位 | 前臺位置 | API 欄位 |
|------|---------|------|---------|---------|
| **Item Name（標題）** | 75（含空格） | 身份識別：品牌 + 品類 + 核心差異 | 主標題 | `item_name` |
| **Item Highlights（商品亮點）** | 125 | 比較輔助：材質 / 場景 / 相容 / 規格 / 限制 | 移動端：標題正下方單獨一行淺色小字；桌面端：用豎線 `\|` 與標題拼接成一行 | `title_differentiation` |

### 關鍵屬性（必須記住）

1. **可搜尋索引**：官方明確 Item Highlights 內容會被搜尋抓取，放進去的關鍵詞能帶來曝光（具體 ranking 權重官方只確認"可索引"，仍在觀察期）
2. **格式**：逗號分隔的短語，**不是完整句子**，也不是五點描述（Bullet Points 仍獨立存在，互不替代）
3. **API 提交**：`title_differentiation` 透過 Listings Items API 或 JSON_LISTINGS_FEED 提交；先調 `getDefinitionsProductType` 確認該類目已開放該屬性
4. **存量 Listing 不強制立刻改**：超 75 字元的老標題 7-27 後不會被下架；亞馬遜 AI 會自動拆分到 `item_name` + `title_differentiation`，品牌所有者有 **14 天稽核視窗**（Manage All Inventory → Edit → View enhancements）可駁回/修改再批准
5. **批次遷移**：下載 Category Listings Report，表內已帶 Item Highlights 列，填完傳回通常 8 小時內生效
6. **提交口徑注意**：提交超 75 字元的 `item_name` 時目錄會自動拆分；`getListingsItem` 返回的是你的原始提交值，前臺展示的是拆分後版本

> ⚠️ 大賣家長尾詞如果原來全壓在標題裡，現在必須主動重新分配到 Highlights——否則 AI 自動拆分可能把轉化詞切掉。

---

## 二、雙欄位黃金結構

```
Item Name（≤75 字元）:
[品牌] + [核心品類詞] + [關鍵差異化屬性] + [規格/數量]

Item Highlights（≤125 字元，逗號分隔短語）:
[材質/工藝], [主場景], [相容/適用物件], [包裝內容], [限制條件]
```

### 案例 1：抗 UV 戶外模擬植物

**舊寫法（200 字元長標題，已過時）**：

```
Brand UV Resistant Artificial Flowers for Outdoors, 12 Bundles Realistic Faux Plants for Patio Garden Porch Planters, Fade Resistant Outdoor Decor
```

**新寫法**：

- Item Name（49 字元）：`Brand UV Resistant Artificial Flowers, 12 Bundles`
- Item Highlights（約 104 字元）：`UV & Fade Resistant, Realistic Faux Plants, for Patio Garden Porch Planters, Outdoor Decor, No Watering Needed`

拆解：
- Item Name = 品牌（Brand）+ 核心品類詞（Artificial Flowers，L1）+ 關鍵差異（UV Resistant，L2）+ 規格（12 Bundles，L5）→ 身份識別，75 字元內完成
- Item Highlights = 功能（UV & Fade Resistant，L2）+ 同義詞（Realistic Faux Plants，L1 變體）+ 詳細場景（Patio Garden Porch Planters，L3）+ 類目定位（Outdoor Decor，L1）+ 差異價值（No Watering Needed，L4）→ 幫助比較的資訊

### 案例 2：官方風格示例（USB-C 充電器）

舊標題：USB-C 快充介面卡，支援 PPS，適用 MacBook/iPhone/Galaxy…不含線

- 標題只留：`USB-C PPS Charger`
- Highlight：`USB-C, Supports PPS, Cable Not Included, Travel & Office`

---

## 三、雙欄位三大原則

### 原則 1：主詞靠前（Item Name）
系統從左到右理解權重，核心品類詞必須在前 5 個詞內出現。Item Name 只有 75 字元，就是移動端完整可見的主標題，**必須獨立完成身份識別**，不能依賴 Highlights 補詞。

✅ `Brand UV Resistant Artificial Flowers, 12 Bundles`
❌ `Brand Premium Quality Decor, 12 Bundles`（核心品類詞缺失）

### 原則 2：差異化屬性具體，亮點不重複標題
不要用通用形容詞（premium / high quality / best），用具體功能詞（UV resistant / fade resistant / realistic）。**Highlights 不搬運標題已有的詞繼續堆**——同一個詞寫兩遍不增加索引價值，浪費 125 字元配額。

### 原則 3：亮點是短語清單，不是第二標題
Highlights 放"幫助比較"的資訊：材質、適用場景、相容型號、包裝內容、限制條件。不放促銷語（Free Shipping / Best Price / Sale），不寫成完整句子，不把五點描述複製進來。

---

## 四、生成 3 個版本對比

| 版本 | 特點 | 適用場景 |
|------|------|---------|
| 關鍵詞覆蓋版 | 標題+亮點合計埋詞最多，結構緊湊 | 廣告冷啟動、強競價品類 |
| 轉化表達版 | 可讀性優先，價值前置 | 自然排名沉澱、移動端 |
| 簡潔合規版 | 字數剋制，無誇大表達 | 高合規風險品類、新賬號 |

### 案例（抗 UV 戶外模擬植物）

| 版本 | Item Name | Item Highlights | 優缺點 |
|------|-----------|-----------------|--------|
| 關鍵詞覆蓋版 | Brand UV Resistant Artificial Flowers, 12 Bundles | UV & Fade Resistant, Realistic Faux Plants, for Patio Garden Porch Planters, Outdoor Decor, No Watering Needed | ✅ 核心詞全覆蓋；❌ 亮點接近滿配，後續加詞空間小 |
| 轉化表達版 | Brand 12-Bundle UV Resistant Fake Plants That Look Real | UV & Fade Proof, Lush & Realistic, for Patio & Porch Planters, Zero Maintenance Outdoor Decor | ✅ 移動端友好；❌ 犧牲了 garden 場景詞 |
| 簡潔合規版 | Brand UV Resistant Artificial Flowers, 12 Bundles | Fade Resistant, for Outdoor Planters, Plastic Stems, No Watering | ✅ 安全合規、留白多；❌ 差異化弱 |

---

## 五、字數與字元規範

| 站點 | Item Name 上限 | Item Highlights 上限 | 建議組合 |
|------|--------------|---------------------|---------|
| 美國站（US） | 75 字元 | 125 字元 | 標題 60-75 + 亮點 90-125 |
| 歐洲站（UK/DE/FR/IT/ES） | 75 字元 | 125 字元 | 同美國站 |
| 日本站（JP） | 按站點公告執行 | 按站點公告執行 | 以類目 schema 為準 |
| 加拿大站（CA） | 75 字元 | 125 字元 | 同美國站 |

> ⚠️ 本 Skill 以美國站為基準。其他站點上線前先調 `getDefinitionsProductType` 拿 schema，確認該類目 `title_differentiation` 屬性與字元上限。
> ⚠️ 媒介類目（圖書/音樂/影音）不適用本次改革，仍按原 200 字元單標題處理。

---

## 六、給 Codex 的提示詞（本步專用）

詳見 `prompts/master-prompt.md` 第 4 步。精簡版：

> 輸入：詞庫（L1-L5）、痛點證據對映表、品牌名、規格、合規限制。
>
> 任務：
> 1. 生成 3 版"Item Name + Item Highlights"組合（關鍵詞覆蓋版 / 轉化表達版 / 簡潔合規版）
> 2. Item Name 遵循"品牌 + 核心詞 + 差異化屬性 + 規格"結構，≤75 字元
> 3. Item Highlights 為逗號分隔短語（材質/場景/相容/包裝/限制），≤125 字元，**不重複 Item Name 已有詞**
> 4. 分別標註兩欄位的字元數與埋入關鍵詞清單（對照詞庫）
> 5. 列出優缺點 + 適用場景
> 6. 推薦一版作為基礎版，並說明理由

---

## 七、常見錯誤（必須避免）

| 錯誤 | 示例 | 修正 |
|------|------|------|
| 通用形容詞堆砌 | Premium Quality Beautiful Artificial Flowers | 用功能詞替代 |
| 主詞靠後 | Brand Outdoor Decor - UV Resistant Artificial Flowers 12 Bundles | 主詞前置 |
| 標題超 75 字元仍按舊 200 字元寫 | 沿用舊長標題不拆分 | 按 75+125 雙欄位重寫 |
| 亮點重複標題詞 | 標題已有 UV Resistant，亮點再寫 UV Resistant | 亮點只放標題未覆蓋的比較資訊 |
| 亮點寫成完整句子 / 促銷語 | These flowers will never fade! Buy now! | 改逗號分隔短語 |
| 全場景塞滿 | for Patio Garden Porch Cemetery Wedding Office Home | 只放主場景（次場景留給五點/A+/QA） |
| 重複關鍵詞 | Artificial Flowers UV Resistant Artificial Plants Outdoor Faux Flowers | 同義詞去重 |
| 包含競品品牌 | Better Than [Other Brand] Artificial Flowers | 移除競品詞 |
| 絕對化表達 | 100% No Fade Lifetime Warranty | 改穩健表達 |

---

## 八、輸出模板

```markdown
# 標題 + 亮點草稿對比 — {產品名}

## 版本 1：關鍵詞覆蓋版
**Item Name**：Brand UV Resistant Artificial Flowers, 12 Bundles
**Item Name 字元數**：49
**Item Highlights**：UV & Fade Resistant, Realistic Faux Plants, for Patio Garden Porch Planters, Outdoor Decor, No Watering Needed
**Item Highlights 字元數**：111
**埋入關鍵詞**：
- L1：artificial flowers（標題）, faux plants（亮點）
- L2：UV resistant（標題）, fade resistant / no watering（亮點）
- L3：patio, garden, porch, planters, outdoor（亮點）
- L5：12 bundles（標題）

**優點**：核心詞全覆蓋，標題+亮點兩層索引
**缺點**：亮點接近滿配，加詞空間小
**適用**：廣告冷啟動

## 版本 2：轉化表達版
...

## 版本 3：簡潔合規版
...

## 推薦基礎版
**選擇**：版本 1
**理由**：[根據品類、賬號階段、廣告策略選擇]

## 存量 Listing 遷移提示（如適用）
- 舊標題是否超 75 字元：是/否
- 建議動作：主動按雙欄位重寫 / 等 AI 自動拆分後 14 天內人工稽核
```

---

## 九、檢查清單

- [ ] 3 個"標題 + 亮點"組合已生成
- [ ] Item Name ≤ 75 字元，含品牌 + 核心品類詞 + 關鍵差異 + 規格
- [ ] Item Highlights ≤ 125 字元，逗號分隔短語，非完整句子
- [ ] Highlights 不重複 Item Name 已有詞
- [ ] Highlights 無促銷語、無絕對化表達
- [ ] 核心品類詞在 Item Name 前 5 個詞內
- [ ] 無通用形容詞堆砌
- [ ] 無競品品牌詞
- [ ] 兩欄位字元數已分別標註
- [ ] 優缺點對比清晰，推薦理由合理
- [ ] （存量 Listing）已給出遷移建議（主動改 / AI 拆分 + 14 天人工稽核）
