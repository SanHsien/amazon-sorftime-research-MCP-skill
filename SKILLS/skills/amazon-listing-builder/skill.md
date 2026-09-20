---
name: amazon-listing-builder
description: 亞馬遜爆款 Listing 打造助手（基於 Cosmo 語義演算法 + Alexa/Rufus 對話式購物趨勢）。透過"先分析、再生成、最後校驗"的 AI 工程化流程，把 Listing 從"關鍵詞堆砌"升級為"語義覆蓋 + 需求證據 + 答案型內容"。提供八步工作流（關鍵詞分層詞庫 → 使用者問題庫 → 賣點證據庫 → 標題 → 五點 → 描述A+ → Search Terms → QA）、給 Codex 的可複用提示詞、真實案例（抗 UV 戶外模擬植物、down filled pillows QA）以及五大常見誤區檢查。觸發場景：(1) 使用者說"幫我寫 Listing / 寫標題 / 寫五點 / 寫描述 / 寫 A+ / 寫 QA / 寫 Search Terms"(2) 使用者輸入 /listing-builder, /build-listing, /cosmo-listing, /alexa-qa, /listing-title, /listing-bullets, /listing-aplus, /listing-st, /listing-qa(3) 使用者提及 Cosmo 演算法、Alexa 演算法、Rufus、對話式購物、語義搜尋、答案型 Listing(4) 使用者希望結合賣家精靈 MCP 資料做關鍵詞分層與痛點對映。適用於亞馬遜美國站等站點的運營、Listing 最佳化師、產品開發、跨境營銷人員。
---

# 亞馬遜爆款 Listing 打造助手（Cosmo / Alexa 新演算法版）

---

## 🚨 鐵律 0：資料來源優先順序（必須先讀）

> **MCP（賣家精靈）> 瀏覽器**
>
> 核心資料必須走 MCP；瀏覽器僅作為 MCP 沒有覆蓋的資料的補充來源。

### 必須使用 MCP 的場景（禁止瀏覽器抓 Amazon）

| 資料型別 | MCP 工具 |
|---------|---------|
| 關鍵詞搜尋量 / PPC / 趨勢 | `mcp__sellersprite__keyword_miner` / `keyword_research_trends` |
| 競品 ASIN 詳情（標題/五點/價格/評分） | `mcp__sellersprite__asin_detail` |
| 競品關鍵詞反查 | `mcp__sellersprite__traffic_keyword` / `keyword_order` |
| **競品評論（含差評）** | `mcp__sellersprite__review` ⚠️ **禁止抓 `amazon.com/product-reviews/`** |
| 競品流量結構 | `mcp__sellersprite__traffic_listing` / `traffic_keyword_stat` |
| 價格 / BSR 歷史 | `mcp__sellersprite__keepa_info` |
| 市場價格分佈 | `mcp__sellersprite__market_price_distribution` |
| 類目節點 | `mcp__sellersprite__product_node` |

### 允許使用瀏覽器的場景（MCP 無對應資料）

| 資料型別 | 瀏覽器來源 |
|---------|----------|
| 站外買家反饋 | Reddit / TikTok / Pinterest |
| 亞馬遜前臺 QA 板塊 | `amazon.com/ask-questions/...`（MCP 無 QA 工具） |
| 自己的廣告報表 / 客服 / 退貨 | 賣家後臺匯出 |
| 認證查詢 | FDA / CPSIA / RoHS 官網 |
| 品牌官網 | 驗證品牌定位 |

> 詳細協議、呼叫順序、引數模板見 `reference/mcp-mandatory-protocol.md`。
> MCP 呼叫失敗的欄位標 `DATA_MISSING`，**禁止用瀏覽器湊 Amazon 資料**。

---

## 一、為什麼需要這個 Skill

舊 Listing 方法正在失效：找詞 → 標題埋大詞 → 五點寫功能 → ST 填同義詞 → 跑廣告。這套邏輯只解決"被檢索"，沒解決"被系統理解、被買家相信、被轉化"。

新語境（Cosmo 語義演算法 + Alexa/Rufus 對話式購物）要求 Listing 同時回答三類問題：
- 系統問：你的產品屬於什麼品類、解決什麼需求、適合什麼場景？
- 買家問：會不會褪色？尺寸多大？能不能用在 XX 場景？包裝會不會壞？
- AI 助手問：使用者用自然語言問"適合全日照戶外花盆的模擬花"，你的 Listing 是不是最強匹配？

本 Skill 的目標：**把關鍵詞背後的"使用者任務、使用場景、痛點問題、產品證據、購買疑慮"全部講清楚**。

---

## 二、核心方法論：先分析、再生成、最後校驗

| 階段 | 動作 | 輸出 |
|------|------|------|
| **準備階段** | 建詞庫 + 問題庫 + 賣點證據庫 | 三份結構化資料 |
| **生成階段** | 多版本標題/五點/描述/ST/QA | 至少 3 版可對比草稿 |
| **校驗階段** | 合規 + 關鍵詞覆蓋 + 語義覆蓋 + 轉化邏輯 | 4 項檢查報告 |

> ⚠️ 不要讓 AI 直接寫。先有詞庫、痛點庫、問題庫、證據庫，再寫才有根。

---

## 三、八步工作流總覽

| 步驟 | 名稱 | 關鍵產出 | 詳見 |
|------|------|----------|------|
| 1 | 關鍵詞分層詞庫 | 5 層詞表（核心/功能/場景/問題/規格） | `workflow/step-1-keyword-library.md` |
| 2 | 使用者問題庫 | 真實買家疑慮清單（來自評論/QA/Reddit/TikTok） | `workflow/step-2-question-library.md` |
| 3 | 賣點證據庫 | 每個賣點對應材料/資料/圖片證據 | `workflow/step-3-evidence-library.md` |
| 4 | 標題結構設計 | 品牌+核心詞+差異屬性+主場景+規格 | `workflow/step-4-title-design.md` |
| 5 | 五點描述 | 5 點對應 5 個決策環節（不堆詞） | `workflow/step-5-bullet-points.md` |
| 6 | 描述 + A+ 內容 | 痛點 → 場景 → 方案 → 細節 → 對比 → 注意 | `workflow/step-6-description-aplus.md` |
| 7 | Search Terms | 只放補充索引詞，不重複、不堆砌 | `workflow/step-7-search-terms.md` |
| 8 | QA 設計 | 答案型內容，對應自然語言搜尋 | `workflow/step-8-qa-design.md` |

---

## 四、給 Codex / Claude 的主提示詞（直接複用）

詳見 `prompts/master-prompt.md`。精簡版：

> 你是一名亞馬遜美國站資深 Listing 策略顧問，熟悉 Cosmo 語義搜尋、Alexa/Rufus 對話式購物、關鍵詞索引、轉化文案和合規表達。
>
> 接下來我會提供：產品資訊、競品 Listing、關鍵詞資料、廣告搜尋詞、評論痛點、QA 問題、供應鏈賣點和合規限制。
>
> **請你先不要直接寫 Listing**，而是先完成以下分析：
> 1. 關鍵詞分層詞庫（核心 / 功能 / 場景 / 屬性 / 問題 / 同義詞 / 後臺補充）
> 2. 每個詞標註：搜尋意圖、建議位置、是否必須前臺、是否進 ST
> 3. 評論痛點 + 使用者問題 → 輸出"痛點-解決方案-證據-關鍵詞-圖片模組"對映表
> 4. 基於 Cosmo + 對話式購物邏輯，列出必須覆蓋的使用者任務和自然語言問題
> 5. 生成 3 版標題（關鍵詞覆蓋版 / 轉化表達版 / 簡潔合規版）+ 優缺點對比
> 6. 五點描述：每點對應一個使用者疑慮 + 一個核心賣點，禁用空泛詞
> 7. 產品描述 + A+ 模組結構（使用場景 → 產品結構 → 痛點解決 → 信任證明）
> 8. Search Terms 建議（只放前臺未覆蓋但有索引價值的詞）
> 9. 10 個 QA：問題來自真實疑慮，答案穩健不誇大
> 10. 最後做：合規檢查 + 關鍵詞覆蓋檢查 + 語義覆蓋檢查 + 轉化邏輯檢查

---

## 五、子命令

| 命令 | 用途 |
|------|------|
| `/listing-builder` | 完整八步流程，端到端生成全套 Listing |
| `/listing-title` | 僅生成多版本標題（含優缺點對比） |
| `/listing-bullets` | 僅生成五點描述（按決策鏈） |
| `/listing-aplus` | 僅生成描述 + A+ 模組結構 |
| `/listing-st` | 僅生成 Search Terms（補充索引策略） |
| `/alexa-qa` | 僅生成對話式 QA（針對 Alexa/Rufus） |
| `/listing-audit` | 對現有 Listing 做合規 + 語義 + 轉化四項校驗 |

---

## 六、與賣家精靈 MCP 整合（必須使用，本專案已配置）

本專案 `.mcp.json` 已配置 sellersprite MCP，**核心資料必須走 MCP**，詳見頂部"鐵律 0"和 `reference/mcp-mandatory-protocol.md`。

### 八步工作流的 MCP 呼叫清單

| 步驟 | 必須呼叫的 MCP 工具 | 瀏覽器補充 |
|------|------------------|----------|
| 1 關鍵詞分層 | `keyword_miner` + `keyword_research_trends` + `traffic_keyword` + `keyword_order` | 無 |
| 2 使用者問題庫 | `review`（差評主題）+ `asin_detail`（競品結構） | Reddit / TikTok / 競品 QA 板塊 |
| 3 賣點證據庫 | `review`（好評證據） | 品牌官網 + 認證官網 |
| 4 標題 | 不調（基於 1-3 步資料） | 無 |
| 5 五點 | 不調 | 無 |
| 6 描述+A+ | 不調 | 品牌官網（參考定位） |
| 7 Search Terms | 不調（基於第 1 步 + 第 4 步做差集） | 無 |
| 8 QA | 不調 | 競品 QA 板塊（補充問題） |

### 瀏覽器使用紅線

| 場景 | ❌ 錯誤做法 | ✅ 正確做法 |
|------|-----------|-----------|
| 抓競品評論 | `webReader(amazon.com/product-reviews/...)` | `mcp__sellersprite__review` |
| 抓競品標題 | `webReader(amazon.com/dp/...)` | `mcp__sellersprite__asin_detail` |
| 拿關鍵詞 | `webReader(Amazon 搜尋建議)` | `mcp__sellersprite__keyword_miner` |
| 看 Reddit | ✅ `webReader(reddit.com/r/...)` | MCP 無此資料 |
| 看競品 QA | ✅ `webReader(amazon.com/ask-questions/...)` | MCP 無 QA 工具 |
| 驗證 FDA | ✅ `webReader(fda.gov)` | MCP 無認證查詢 |

> 完整呼叫順序、引數模板見 `reference/mcp-mandatory-protocol.md`。MCP 資料缺失時，必須列出需要人工補充的資料欄位，**禁止用瀏覽器湊 Amazon 資料**。

---

## 七、五大常見誤區（必須主動檢查）

1. **把 Cosmo / Alexa 講成玄學** — 沒有隱藏規則，最終都是"更相關、更清楚、更可信、更能轉化"
2. **認為關鍵詞不重要** — 關鍵詞仍是地基，區別在於要分層
3. **只最佳化標題** — Listing 是整體，標題/主圖/五點/描述/ST/QA/評論/A+ 必須協同
4. **直接讓 AI 寫一版就上線** — 沒有詞庫和證據庫，AI 只會寫漂亮廢話
5. **用一個 Listing 承接所有人群** — 主圖主場景，其他場景放五點/A+/QA 承接

詳見 `reference/common-mistakes.md`。

---

## 八、真實案例參考

| 案例 | 詳見 |
|------|------|
| 抗 UV 戶外模擬植物（端到端 7 步） | `examples/uv-outdoor-plants-fullcase.md` |
| down filled pillows QA（Alexa 風格示例） | `examples/down-pillows-qa-example.md` |
| 關鍵詞分層詞庫填寫模板 | `examples/layered-keyword-template.md` |

---

## 九、輸出格式規範

| 檔案 | 命名規則 | 必存 |
|------|----------|:----:|
| 完整 Listing 包 | `{產品名}/listing_package.md` | ✅ |
| 關鍵詞分層詞庫 | `{產品名}/keyword_library.md` | ✅ |
| 痛點-證據對映表 | `{產品名}/painpoint_evidence_map.md` | ✅ |
| 多版本草稿對比 | `{產品名}/drafts_comparison.md` | ✅ |
| 合規與語義校驗報告 | `{產品名}/audit_report.md` | ✅ |
| 原始輸入資料 | `{產品名}/input_data.json` | ✅ |

**所有報告必須儲存為檔案**，禁止只列印到控制檯。詳見 `reference/output-format-spec.md`。

---

## 十、執行流程

收到"幫我做 Listing"類請求時：

1. **澄清輸入** — 產品資訊（標題/類目/規格）、是否提供競品 ASIN、是否啟用賣家精靈 MCP、目標站點
2. **跑八步工作流** — 按步驟執行，每步儲存產出
3. **生成草稿** — 至少 3 版標題 + 1 套五點 + 描述/A+/ST/QA
4. **跑校驗** — 合規 + 關鍵詞覆蓋 + 語義覆蓋 + 轉化邏輯
5. **打包交付** — `listing_package.md` 彙總，附 HTML 視覺化版本（可選）

---

## 十一、關鍵原則（每次都要回顧）

- **標題不是堆詞**，是讓系統和買家快速定位
- **五點不是賣點羅列**，是購買決策鏈
- **描述和 A+ 不是重複資訊**，是場景和信任構建
- **ST 不是垃圾桶**，是補充索引池
- **QA 不是可有可無**，是對話式搜尋和轉化疑慮的補丁
- **先分析、再生成、最後校驗** — 永遠不要讓 AI 直接寫
