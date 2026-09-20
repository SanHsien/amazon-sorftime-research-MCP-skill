# Amazon Listing Builder Skill

> **AI 驅動的亞馬遜爆款 Listing 打造助手** — 基於 Cosmo 語義演算法 + Alexa/Rufus 對話式購物趨勢，透過"先分析、再生成、最後校驗"的工程化流程，把 Listing 從"關鍵詞堆砌"升級為"語義覆蓋 + 需求證據 + 答案型內容"。

---

## 一、Overview（這個 Skill 是幹什麼的）

傳統 Listing 方法（找詞 → 標題埋大詞 → 五點寫功能 → ST 填同義詞 → 跑廣告）正在失效。

**新語境要求 Listing 同時回答三類問題**：

| 系統問 | 買家問 | AI 購物助手問 |
|-------|-------|--------------|
| 你的產品屬於什麼品類？解決什麼需求？適合什麼場景？ | 會不會褪色？尺寸多大？能不能用在 XX 場景？包裝會不會壞？ | "適合全日照戶外花盆的模擬花有哪些？" |

本 Skill 把這些要求落地為可執行的**八步工作流**，配套 7 個給 AI 的提示詞模板、3 個真實案例和 4 份背景參考知識。

> **核心方法論**：先分析（詞庫 + 痛點庫 + 證據庫）→ 再生成（多版本對比）→ 最後校驗（合規 + 語義 + 轉化）。

---

## 二、Features（核心特性）

- **關鍵詞分層詞庫** — 把關鍵詞按 5 層（核心/功能/場景/問題/規格）組織，決定每個詞放哪裡
- **使用者問題庫** — 從評論、QA、客服、Reddit/TikTok 提取真實買家疑慮
- **賣點證據庫** — 每個賣點必須有材料/工藝/資料證據，杜絕"漂亮廢話"
- **3 版標題對比** — 關鍵詞覆蓋版 / 轉化表達版 / 簡潔合規版，列出優缺點再由人決策
- **五點決策鏈** — 每點對應一個使用者決策環節（核心價值 → 痛點 → 場景 → 規格 → 信任）
- **A+ 7 屏模組結構** — 每屏對應一個語義關係，承接 Cosmo 演算法
- **Search Terms 策略** — 只放補充索引詞，不重複、不堆砌、不超位元組
- **Alexa 風格 QA** — 答案型內容，承接對話式購物搜尋
- **四項校驗** — 合規 + 關鍵詞覆蓋 + 語義覆蓋 + 轉化邏輯
- **資料迭代** — 上線後用廣告/轉化/差評資料持續最佳化

---

## 三、Prerequisites（前置條件）

- [Claude Code](https://claude.ai/code) CLI
- **賣家精靈 MCP 金鑰（必須）** — 本 Skill 核心資料全部依賴 MCP，禁止用瀏覽器抓 Amazon 湊資料
- 專案根目錄的 `.mcp.json` 已正確配置（本專案已配好）

---

## 🚨 鐵律：資料來源優先順序

> **MCP（賣家精靈）> 瀏覽器**
>
> 核心資料必須走 MCP；瀏覽器僅作為 MCP 沒有覆蓋的資料的必要補充。

### 必須使用 MCP 的資料（禁止瀏覽器抓 Amazon）

| 資料 | MCP 工具 |
|------|---------|
| 關鍵詞搜尋量 / PPC / 趨勢 | `mcp__sellersprite__keyword_miner` / `keyword_research_trends` |
| 競品 ASIN 詳情（標題/五點/價格） | `mcp__sellersprite__asin_detail` |
| 競品關鍵詞反查 | `mcp__sellersprite__traffic_keyword` / `keyword_order` |
| **競品評論（含差評）** | `mcp__sellersprite__review` ⚠️ **嚴禁**抓 `amazon.com/product-reviews/` |
| 價格 / BSR 歷史 | `mcp__sellersprite__keepa_info` |
| 市場價格分佈 | `mcp__sellersprite__market_price_distribution` |
| 流量結構 | `mcp__sellersprite__traffic_listing` / `traffic_keyword_stat` |

### 允許使用瀏覽器的場景（MCP 無對應資料）

| 資料 | 瀏覽器來源 |
|------|----------|
| 站外買家反饋 | Reddit / TikTok / Pinterest |
| 亞馬遜前臺 QA 板塊 | `amazon.com/ask-questions/...` |
| 自己的廣告報表 | 賣家後臺（Reports → Advertising） |
| 自己的客服記錄 | 賣家後臺 |
| 認證查詢 | FDA / CPSIA / RoHS 官網 |
| 品牌官網 | 驗證品牌定位 |

詳見 `reference/mcp-mandatory-protocol.md`。

---

## 四、Quick Start（快速開始）

### 場景 A：完整打造一個新 Listing

直接對話告訴 Claude：

> "我要為抗 UV 戶外模擬植物打造 Listing，價格 $24.99-$29.99，主打 patio/porch/花盆場景，請用 amazon-listing-builder skill 跑完整八步流程。"

或使用子命令：

```
/listing-builder
```

Claude 會按八步工作流順序執行：詞庫 → 問題庫 → 證據庫 → 標題 → 五點 → 描述A+ → ST → QA → 校驗，最終輸出完整 Listing 包到 `{產品名}/` 目錄。

### 場景 B：只最佳化某一模組

```
/listing-title   → 只生成 3 版標題對比
/listing-bullets → 只生成五點描述
/listing-aplus   → 只生成描述 + A+ 模組結構
/listing-st      → 只生成 Search Terms
/alexa-qa        → 只生成 Alexa 風格 QA
```

### 場景 C：稽核已有 Listing

```
/listing-audit
```

對現有 Listing 跑四項校驗（合規 + 關鍵詞覆蓋 + 語義覆蓋 + 轉化邏輯），輸出問題清單和整改優先順序。

### 場景 D：基於關鍵詞列表寫 QA（參考需求文件示例）

> "我是亞馬遜美國站賣家，產品 down filled pillows，特性 24x24/bulk/fluffy，核心賣點 24x24，關鍵詞：down filled pillows / feather down pillow / down feather pillow / goose down pillows。請模擬 Alexa 演算法下的 QA 問答。"

Claude 會呼叫 `examples/down-pillows-qa-example.md` 的模板風格生成。

---

## 五、Command Reference（子命令清單）

| 命令 | 用途 | 主要產出檔案 |
|------|------|------------|
| `/listing-builder` | 完整八步流程端到端生成 | `listing_package.md` + 全部中間產出 |
| `/listing-title` | 多版本標題對比 | `drafts_comparison.md` |
| `/listing-bullets` | 五點描述（按決策鏈） | `drafts_comparison.md` |
| `/listing-aplus` | 描述 + A+ 模組結構 | `drafts_comparison.md` |
| `/listing-st` | Search Terms 補充索引策略 | `listing_package.md` |
| `/alexa-qa` | 對話式 QA（Alexa/Rufus 風格） | `listing_package.md` |
| `/listing-audit` | 對現有 Listing 做四項校驗 | `audit_report.md` |

---

## 六、八步工作流總覽

| 步驟 | 名稱 | 關鍵產出 | 詳見 |
|------|------|----------|------|
| 1 | 關鍵詞分層詞庫 | 5 層詞表（核心/功能/場景/問題/規格） | `workflow/step-1-keyword-library.md` |
| 2 | 使用者問題庫 | 真實買家疑慮清單 | `workflow/step-2-question-library.md` |
| 3 | 賣點證據庫 | 每個賣點對應材料/資料/圖片證據 | `workflow/step-3-evidence-library.md` |
| 4 | 標題結構設計 | 品牌+核心詞+差異屬性+主場景+規格 | `workflow/step-4-title-design.md` |
| 5 | 五點描述 | 5 點對應 5 個決策環節 | `workflow/step-5-bullet-points.md` |
| 6 | 描述 + A+ 內容 | 痛點 → 場景 → 方案 → 細節 → 對比 → 注意 | `workflow/step-6-description-aplus.md` |
| 7 | Search Terms | 只放補充索引詞，不堆砌 | `workflow/step-7-search-terms.md` |
| 8 | QA 設計 | 答案型內容，對應自然語言搜尋 | `workflow/step-8-qa-design.md` |

---

## 七、Directory Structure（目錄結構）

```
.claude/skills/amazon-listing-builder/
├── skill.md                          # 主入口（必讀）
├── README.md                         # 本檔案
├── workflow/                         # 八步工作流分冊
│   ├── step-1-keyword-library.md
│   ├── step-2-question-library.md
│   ├── step-3-evidence-library.md
│   ├── step-4-title-design.md
│   ├── step-5-bullet-points.md
│   ├── step-6-description-aplus.md
│   ├── step-7-search-terms.md
│   └── step-8-qa-design.md
├── prompts/                          # 給 AI 的提示詞模板
│   ├── master-prompt.md              # 主提示詞（可直接複製使用）
│   ├── layered-keyword-prompt.md     # 關鍵詞分層
│   ├── painpoint-mapping-prompt.md   # 痛點-證據對映
│   ├── multiversion-prompt.md        # 多版本生成
│   ├── compliance-check-prompt.md    # 合規檢查
│   ├── semantic-coverage-prompt.md   # 語義覆蓋檢查
│   └── data-iteration-prompt.md      # 上線後資料迭代
├── examples/                         # 真實案例
│   ├── uv-outdoor-plants-fullcase.md      # 抗 UV 戶外模擬植物端到端
│   ├── down-pillows-qa-example.md         # down filled pillows QA 示例
│   └── layered-keyword-template.md        # 關鍵詞分層填寫模板
└── reference/                        # 背景知識
    ├── cosmo-alexa-algorithm.md           # COSMO + Alexa 演算法理解
    ├── common-mistakes.md                 # 五大常見誤區
    ├── sellersprite-mcp-integration.md    # 賣家精靈 MCP 整合
    └── output-format-spec.md              # 輸出格式規範
```

---

## 八、給 Codex / Claude 的提示詞清單

每個提示詞檔案可直接複製貼上使用：

| 提示詞檔案 | 用途 |
|----------|------|
| `prompts/master-prompt.md` | 完整端到端生成全套 Listing |
| `prompts/layered-keyword-prompt.md` | 只跑第一步：把關鍵詞分層 |
| `prompts/painpoint-mapping-prompt.md` | 只跑第三步：建立痛點-證據對映 |
| `prompts/multiversion-prompt.md` | 生成 3 版標題 / 2 版五點對比 |
| `prompts/compliance-check-prompt.md` | 跑合規檢查（絕對化、醫療、環保、安全等） |
| `prompts/semantic-coverage-prompt.md` | 跑語義覆蓋檢查（含 Alexa 模擬） |
| `prompts/data-iteration-prompt.md` | 上線後用真實資料迭代最佳化 |

---

## 九、Real Examples（真實案例參考）

### 案例 1：抗 UV 戶外模擬植物（端到端 9 步完整演示）
**檔案**：`examples/uv-outdoor-plants-fullcase.md`

包含完整的詞庫拆解、痛點證據對映、3 版標題對比、五點描述、7 段式描述、A+ 7 屏結構、ST 最佳化、10 題 QA、上線後資料迭代示例。

### 案例 2：down filled pillows QA（Alexa 風格示例）
**檔案**：`examples/down-pillows-qa-example.md`

基於需求文件中"down filled pillows"產品（24x24/bulk/fluffy），生成 10 題 Alexa 風格 QA，覆蓋 4 個維度（場景/功能/人群/使用），自然埋入 4 個核心關鍵詞。

### 案例 3：關鍵詞分層填寫模板
**檔案**：`examples/layered-keyword-template.md`

空白模板，可直接複製用於任何產品的關鍵詞分層。

---

## 十、與 SellerSprite MCP 整合

本 Skill 與同專案的 `sellersprite-amazon-research` skill 形成互補：

| Skill | 用途 |
|-------|------|
| **sellersprite-amazon-research** | 選品 / 市場分析 / 競品調研 / 評論洞察（提供資料） |
| **amazon-listing-builder**（本 skill） | Listing 文案生成 / 最佳化 / 校驗（消費資料） |

### 資料流

```
sellersprite-amazon-research（提供資料）
    ↓
keyword_miner / traffic_keyword / asin_detail / review 等
    ↓
amazon-listing-builder（消費資料）
    ↓
詞庫 → 問題庫 → 證據庫 → 標題/五點/A+/ST/QA → 校驗
```

### 常用 MCP 工具對映

| 本 Skill 步驟 | 呼叫的賣家精靈工具 |
|------------|-----------------|
| 第 1 步：關鍵詞分層 | `keyword_miner` / `keyword_research_trends` / `traffic_keyword` / `keyword_order` |
| 第 2 步：使用者問題庫 | `review`（差評主題）/ `asin_detail`（競品結構） |
| 第 3 步：賣點證據庫 | 主要靠人工（供應鏈/測試/認證） |
| 第 4-8 步 | 基於前三步資料，不再直接調 MCP |
| 上線後迭代 | `traffic_listing` / `keyword_order` / `market_price_distribution` |

> 詳細呼叫方式、欄位對映和已知陷阱見 `reference/sellersprite-mcp-integration.md`。

---

## 十一、Output Files（輸出檔案結構）

每次完整跑完八步工作流，會在當前目錄生成：

```
{產品名}/
├── listing_package.md           # 完整 Listing 包（彙總交付）
├── keyword_library.md           # 關鍵詞分層詞庫（第一步）
├── question_library.md          # 使用者問題庫（第二步）
├── evidence_library.md          # 賣點證據庫（第三步）
├── drafts_comparison.md         # 多版本草稿對比（第四五六步）
├── audit_report.md              # 合規 + 語義 + 轉化校驗報告
├── input_data.json              # 原始輸入資料
└── listing_package.html         # HTML 視覺化版本（可選，推薦生成）
```

> 詳細規範見 `reference/output-format-spec.md`。

---

## 十二、Common Mistakes（五大常見誤區）

1. **把 Cosmo / Alexa 講成玄學** — 沒有隱藏規則，最終都是"更相關、更清楚、更可信、更能轉化"
2. **認為關鍵詞不重要** — 關鍵詞仍是地基，區別在於要分層
3. **只最佳化標題** — Listing 是整體，標題/主圖/五點/描述/ST/QA/評論/A+ 必須協同
4. **直接讓 AI 寫一版就上線** — 沒有詞庫和證據庫，AI 只會寫漂亮廢話
5. **用一個 Listing 承接所有人群** — 主圖主場景，其他場景放五點/A+/QA 承接

詳見 `reference/common-mistakes.md`。

---

## 十三、Compliance Red Lines（合規紅線詞清單）

| 紅線詞 | 安全替代 |
|--------|---------|
| 100% / never / always | help / support / designed to |
| lifetime / forever | long-term use |
| best / #1 / top rated | popular / favored |
| cheap / lowest price | affordable / value |
| cures / treats / heals | supports / may help |
| 100% eco-friendly | made with recyclable materials |
| FDA approved（無認證） | meets [actual standard] |
| organic（無認證） | natural materials |
| guaranteed | designed for / backed by [policy] |
| fireproof（無測試） | fire-resistant（如有測試） |

完整檢查項見 `prompts/compliance-check-prompt.md`。

---

## 十四、Known Limitations（已知限制）

- **賣家精靈 review 取樣限制** — 每次最多返回 20 條評論，是樣本資料，評分分佈不代表總體
- **`keyword_research` 忽略 keyword 引數** — 該工具會返回全球熱詞，使用 `keyword_miner` 替代
- **`traffic_source` 資料不可靠** — 可能返回無關產品的流量，建議用 `traffic_keyword` + `traffic_keyword_stat` 組合替代
- **`keyword_research_trends` 欄位名差異** — 實際欄位是 `time` / `search` / `chainGrowth` / `yearlyGrowth`，不是文件描述的 `month` / `searches` / `growth`
- **COSMO / Alexa 演算法非官方評分規則** — 不要把它神化，本 Skill 把它理解為"語義搜尋 + 對話式購物趨勢"即可
- **AI 生成內容必須人工稽核** — AI 容易寫過頭（誇大承諾、絕對化表達），合規風險需人工把關

---

## 十五、Recommended Workflow（推薦組合鏈路）

### 鏈路 A：從零打造爆款 Listing

```
1. 呼叫 sellersprite-amazon-research 做選品
   ↓ 輸出：目標 ASIN + 競品列表 + 市場資料
2. 呼叫 amazon-listing-builder /listing-builder
   ↓ 輸入：競品 ASIN + 產品規格 + 賣點
   ↓ 輸出：完整 Listing 包
3. 上線後 2-4 周呼叫 /listing-audit + data-iteration-prompt
   ↓ 輸出：迭代最佳化建議
4. 每月迭代一次
```

### 鏈路 B：最佳化現有 Listing

```
1. /listing-audit（先做診斷）
   ↓ 輸出：合規 + 語義 + 轉化四項報告
2. 根據報告選擇子命令
   - 標題問題 → /listing-title
   - 五點問題 → /listing-bullets
   - QA 不足 → /alexa-qa
3. 上線新版後跟蹤 2-4 周
```

### 鏈路 C：只補 QA（最小成本上線）

```
1. /alexa-qa
   ↓ 輸入：產品規格 + 必須埋入的關鍵詞
   ↓ 輸出：10 題 Alexa 風格 QA
```

---

## 十六、FAQ（常見問題）

### Q1：必須用賣家精靈 MCP 才能用這個 Skill 嗎？
**A**：不必須。Skill 可以基於使用者提供的產品資訊和關鍵詞列表工作。但有 MCP 資料更精準，能避免編造。

### Q2：生成的 Listing 可以直接上線嗎？
**A**：**不能**。必須人工稽核：
- 合規風險（絕對化、醫療、環保承諾）
- 證據真實性（材料/工藝/認證是否真的有）
- 關鍵詞相關性（是否真的匹配產品）
- 欄位長度（標題/五點/描述字元數）

### Q3：3 版標題應該選哪個？
**A**：看場景：
- 廣告冷啟動 / 強競價品類 → 關鍵詞覆蓋版
- 移動端流量為主 / 自然排名沉澱 → 轉化表達版
- 高合規風險品類 / 新賬號 → 簡潔合規版

### Q4：Skill 支援哪些站點？
**A**：方法論支援所有站點。字元限制差異：
- 美國站：標題 200 字元、ST 250 位元組
- 歐洲站：同美國
- 日本站：標題 100 位元組、ST 100 位元組

### Q5：上線後多久迭代一次？
**A**：
- 上線第 1 周：每天看 CTR
- 上線 2-4 周：每週一次詞效分析
- 上線 1-3 個月：每月一次全面最佳化
- 上線 3 個月後：季度精修

### Q6：能不能跳過八步直接寫 Listing？
**A**：技術上可以，但**不推薦**。沒有詞庫和證據庫，AI 寫出來的就是漂亮廢話（premium / perfect / easy to use / great gift）。八步的"先分析"階段就是為了避免這個問題。

---

## 十七、Core Philosophy（核心理念）

> **Listing 不是文案工作，而是流量效率工程。**

- 標題不是堆詞，是讓系統和買家快速定位
- 五點不是賣點羅列，是購買決策鏈
- 描述和 A+ 不是重複資訊，是場景和信任構建
- ST 不是垃圾桶，是補充索引池
- QA 不是可有可無，是對話式搜尋和轉化疑慮的補丁

**一句話總結**：

> 把關鍵詞背後的"使用者任務、使用場景、痛點問題、產品證據、購買疑慮"全部講清楚，讓系統能理解，讓買家能相信，讓資料能持續正反饋。

---

## License

MIT

特別緻謝靈感來源： https://mp.weixin.qq.com/s/6AUEMvyjPb1C_cqpEERklQ?click_id=1881462166