# 痛點-證據對映提示詞

> 用於第三步：把產品賣點拆解成"痛點 → 解決方案 → 證據 → 關鍵詞 → 圖片"完整鏈。

## 🚨 資料來源鐵律

**使用者痛點主來源必須走 MCP**：競品差評用 `mcp__sellersprite__review`，**嚴禁**用瀏覽器抓 `amazon.com/product-reviews/`。

```python
# 必須呼叫（拿競品差評作為痛點真相）
for asin in competitor_asins:
    mcp__sellersprite__review({"marketplace":"US","asin":asin})
    # ⚠️ 每次最多 20 條，需多 ASIN 取並集
```

✅ **瀏覽器補充**（僅 MCP 無對應資料）：
- 競品 QA 板塊：`amazon.com/ask-questions/...`（MCP 無 QA 工具）
- Reddit / TikTok 站外反饋
- 認證官網：FDA / CPSIA / RoHS（驗證證書真實性）

❌ **嚴禁**：`webReader(amazon.com/product-reviews/B07X...)` 抓評論

---

## 提示詞

```
你是一名亞馬遜產品證據工程師。請基於以下輸入，建立"痛點-證據對映表"。

## 輸入
- 產品規格：[貼上]
- 供應鏈資訊（材料/工藝/認證）：[貼上]
- 產品功能列表：[貼上]
- 使用者問題庫（來自第二步）：[貼上]
- 關鍵詞分層詞庫（來自第一步）：[貼上]
- 競品差評主題：[貼上]

## 任務

### 1. 列出產品所有可能的賣點
不少於 10 個，按主次排序。

### 2. 為每個賣點找到證據
證據型別：
- 材料證據（如 PE plastic / stainless steel）
- 工藝證據（如 reinforced stitching / double-stitched）
- 規格證據（如 12 bundles / 16 inches / 24 x 24）
- 場景證據（如 tested for outdoor use）
- 對比證據（如 vs standard faux flowers）
- 客戶反饋證據（來自好評）
- 資料證據（如 200+ hours UV test）
- 認證證據（如 CPSIA / RoHS）

每個賣點至少 1 條證據，無證據的賣點必須標註"待補充證據"，不能進 Listing。

### 3. 建立對映表

每個賣點拉成一條完整鏈：

| 欄位 | 說明 |
|------|------|
| feature | 賣點名稱 |
| painpoint | 對應使用者痛點 |
| evidence | 證據描述（材料/工藝/資料） |
| keywords | 對應關鍵詞（來自詞庫） |
| image_brief | 圖片需求簡述 |
| aplus_module | A+ 模組位置 |
| bullet_point_n | 五點第幾條 |
| qa_n | QA 第幾題 |
| compliance_risk | high / medium / low |
| verification_status | 已驗證 / 待驗證 / 無證據 |

### 4. 合規風險檢查
對每個賣點檢查：
- 是否含絕對化表達（100% / never / always）
- 是否含醫療承諾（cures / treats / heals）
- 是否含環保絕對詞（100% eco-friendly）
- 是否含安全承諾（FDA approved 如無認證）
- 是否含持久承諾（lifetime / forever）

如發現，標註合規風險等級並給出替代建議。

### 5. 輸出圖片需求清單
列出所有需要的圖片素材，給美工：
| 圖片編號 | 用途 | A+ 位置 | 需求簡述 |
|---------|------|---------|---------|

## 輸出格式

# 賣點證據庫 — {產品名}

## 核心賣點（前 5 個，必進 Listing）

### 賣點 1: UV Resistant Design
- 痛點：戶外暴曬容易褪色
- 證據：採用抗 UV 處理 PE 塑膠花瓣
- 對應關鍵詞：UV resistant / fade resistant / outdoor sunlight
- 圖片需求：戶外陽光下場景圖
- A+ 位置：第 2 屏
- 五點位置：第 1 點
- QA 位置：Q1
- 合規風險：低
- 驗證狀態：已驗證（供應鏈確認）

### 賣點 2-5: ...

## 次核心賣點（6-10）

## 待補充證據的賣點（不要進 Listing）
- 賣點 X：[描述]，但無 [證據型別] 支撐，建議補充 [測試/認證] 或從 Listing 刪除

## 圖片需求清單
| 編號 | 用途 | 需求簡述 |
|------|------|---------|
| IMG-01 | A+ 第 1 屏主圖 | 戶外門廊場景 |
| IMG-02 | A+ 第 2 屏 | 抗 UV 材料示意 |
| ...  | ...  | ...     |

## 合規風險彙總
- 賣點 X：原表達 "100% no fade"，建議改為 "help reduce fading"
- 賣點 Y：原表達 "lifetime warranty"，建議改為 "designed for long-term use"
```

---

## 關鍵原則

1. **沒證據的賣點必須剔除** — 不能讓 AI 寫漂亮廢話
2. **合規風險必須標註** — AI 容易寫過頭
3. **圖片需求必須列清單** — 給美工明確指引
4. **驗證狀態必須真實** — 供應鏈/測試/客戶反饋來源要清晰
