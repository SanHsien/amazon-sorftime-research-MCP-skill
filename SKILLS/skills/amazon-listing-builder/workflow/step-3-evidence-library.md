# 第三步：賣點證據庫

> **每一個賣點都要有證據**。否則 AI 寫出來的全是空話："premium quality / perfect for any occasion / easy to use / great gift"。

## 🚨 MCP 呼叫 + 瀏覽器補充

本步主資料來自**人工供應鏈資訊**（MCP 不提供產品內部資料），但可透過 MCP 拿到**競品好評中的客戶認可證據**。

### 必須呼叫的 MCP 工具

```python
# 1. 競品好評（提取客戶認可的賣點 = 可信證據）
for asin in competitor_asins:
  mcp__sellersprite__review({
    "marketplace":"US", "asin":asin
  })
  # 用好評主題作為"客戶認可的證據"

# 2. 自己 ASIN 的好評（如有）
mcp__sellersprite__review({
  "marketplace":"US", "asin":"<自己的ASIN>"
})
```

### ✅ 瀏覽器補充（驗證材料 / 認證）

```javascript
// 1. 認證機構官網（驗證 CPSIA / FDA / RoHS 等證書真實性）
mcp__web_reader__webReader({url:"https://www.fda.gov/..."})
mcp__web_reader__webReader({url:"https://www.cpsc.gov/..."})

// 2. 品牌官網（拿品牌定位語言）
mcp__web_reader__webReader({url:"https://brand.com/about"})
```

### ❌ 禁止行為

不能用瀏覽器抓 Amazon 商品頁湊"證據"，所有競品資料必須走 MCP。

詳見 `reference/mcp-mandatory-protocol.md`。

---

## 一、為什麼需要證據庫

| 賣點（空話版） | 賣點（證據版） |
|--------------|--------------|
| UV resistant | Made with UV-resistant materials to help reduce fading during outdoor sunlight exposure |
| Realistic | Natural color variation and fuller flower heads create a lifelike look from a distance |
| Easy to use | Flexible stems can be directly inserted into planters, baskets and porch boxes |
| Durable | Reinforced plastic stems resist bending and shedding during shipping |

證據庫的本質：**讓 AI 寫出來的每一句話都有事實支撐，避免合規風險和差評反噬**。

---

## 二、證據型別

| 證據型別 | 示例 | 可信度 |
|---------|------|--------|
| 材料證據 | "Made with UV-resistant PE plastic" | ⭐⭐⭐ |
| 工藝證據 | "Reinforced stems resist bending" | ⭐⭐⭐ |
| 規格證據 | "12 bundles, 16 inches tall" | ⭐⭐⭐ |
| 場景證據 | "Tested for patio and porch use" | ⭐⭐ |
| 對比證據 | "Compared with standard faux flowers" | ⭐⭐ |
| 客戶反饋證據 | "Buyers praise the natural look"（來自好評） | ⭐⭐ |
| 資料證據 | "Tested for 200+ hours UV exposure"（如有） | ⭐⭐⭐ |
| 認證證據 | "Meets CPSIA / RoHS / FDA standard"（如有） | ⭐⭐⭐ |

> ⚠️ **關鍵原則**：沒有的證據不要寫。AI 很會編，必須人工稽核，否則違規風險。

---

## 三、痛點 → 解決方案 → 證據 → 關鍵詞 → 圖片 對映表

這是核心產出。每個痛點都要拉成一條完整的鏈：

| 痛點 | 解決方案 | 證據 | 對應關鍵詞 | 對應圖片 | Listing 位置 |
|------|---------|------|----------|---------|------------|
| 會褪色 | 抗 UV 材料 | "UV-resistant materials, suitable for outdoor sun" | UV resistant / fade resistant / won't fade | 戶外暴曬場景圖 | 五點 1 + A+ 第 2 屏 |
| 看起來假 | 自然色差 + 層次花瓣 | "Natural color variation + layered petals" | realistic / lifelike / natural look | 近景細節圖 + 遠景佈置圖 | 五點 2 + A+ 第 3 屏 |
| 不會用 | 直接插入花盆 | "Flexible stems for direct insertion" | easy to use / for planters | 花盆使用圖 | 五點 3 + A+ 第 4 屏 |
| 收到變形 | 加固包裝 | "Protective packaging to reduce transit damage" | protective packaging | 包裝示意圖 | 五點 5 + A+ 第 5 屏 |
| 不知道買多少 | 數量建議 | "12 bundles fill a medium planter" | 12 bundles / for planters | 數量對照圖 | 五點 4 + QA |

---

## 四、欄位定義（賣點證據庫）

| 欄位 | 說明 |
|------|------|
| `feature` | 賣點名稱（如 "UV Resistant"） |
| `painpoint` | 對應使用者痛點 |
| `evidence` | 證據描述（具體材料/工藝/資料） |
| `keywords` | 對應關鍵詞列表 |
| `image_brief` | 圖片需求簡述（給美工的需求文件） |
| `aplus_module` | A+ 模組對應位置 |
| `bullet_point_n` | 五點第幾條 |
| `qa_n` | QA 第幾題 |
| `compliance_risk` | 合規風險（high/medium/low） |
| `verification_status` | 驗證狀態（已驗證/待驗證/無證據） |

---

## 五、給 Codex 的提示詞（本步專用）

詳見 `prompts/painpoint-mapping-prompt.md`。精簡版：

> 輸入：產品規格、供應鏈資訊（材料/工藝/認證）、產品功能列表、問題庫（來自第二步）、關鍵詞分層詞庫（來自第一步）。
>
> 任務：
> 1. 列出產品所有可能的賣點（不少於 10 個）
> 2. 為每個賣點找到 1-3 條具體證據（材料/工藝/資料）
> 3. 建立痛點 → 解決方案 → 證據 → 關鍵詞 → 圖片 的完整對映表
> 4. 標註無證據支撐的賣點（這些必須從 Listing 刪除或補證據）
> 5. 標註合規風險（醫療/環保/絕對化用語風險）
> 6. 輸出圖片需求清單（給美工）

---

## 六、輸出模板

```markdown
# 賣點證據庫 — {產品名}

## 賣點 1: UV Resistant Design
- **痛點**：戶外暴曬容易褪色
- **證據**：採用抗 UV 處理的 PE 塑膠花瓣，適合戶外長時間擺放
- **對應關鍵詞**：UV resistant / fade resistant / outdoor sunlight
- **圖片需求**：戶外陽光下場景圖，標註 "UV Resistant"
- **A+ 位置**：第 2 屏（材料示意）
- **五點位置**：第 1 點
- **QA 位置**：Q1
- **合規風險**：低（不寫 "100% no fade"，用 "help reduce fading"）
- **驗證狀態**：已驗證（供應鏈確認）

## 賣點 2: Realistic Look
...

## 待補充證據的賣點（不要寫進 Listing）
- 賣點 X：[某承諾]，但當前無證據支撐，建議刪除或補充測試資料
```

---

## 七、合規紅線（必須人工稽核）

| 型別 | 禁用表達 | 安全表達 |
|------|---------|---------|
| 絕對化 | 100% no fade / never fades | Help reduce fading |
| 醫療 | Cures / treats / heals | Supports / may help |
| 環保 | 100% eco-friendly | Made with recyclable materials |
| 安全 | FDA approved（如無認證） | Meets CPSIA standard（如有認證） |
| 持久 | Lifetime warranty / lasts forever | Designed for long-term outdoor use |

---

## 八、檢查清單

- [ ] 每個核心賣點都有至少 1 條證據
- [ ] 無證據支撐的賣點已剔除或標註待補
- [ ] 痛點 → 證據對映完整（5 條以上）
- [ ] 圖片需求清單已生成
- [ ] 合規紅線詞已替換為安全表達
- [ ] 驗證狀態已標註（供應鏈/測試/客戶反饋來源）
