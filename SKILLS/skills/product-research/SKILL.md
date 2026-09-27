---
name: product-research
description: 基於Sorftime MCP的深度選品調研。透過LLM Agent執行多維度分析：資料採集→屬性標註→交叉分析→競品VOC→壁壘評估→選品決策評估。互動式執行，輸出Markdown報告和Dashboard看板。
argument-hint: "[產品/類目關鍵詞] [站點]"
user-invocable: true
---

# 選品分析器 (Product Research - LLM Agent 驅動版)

## 定位

基於 **Sorftime MCP + LLM Agent** 的深度選品調研。LLM 直接執行分析邏輯，指令碼僅負責資料採集和報告渲染。

**核心特點**：
- **LLM 驅動**：分析、洞察、決策全部由 LLM 完成
- **互動式執行**：逐步推進，使用者可中途干預
- **輕量指令碼**：僅用於 API 呼叫和 Dashboard 渲染

---

## Script Directory

| 指令碼 | 用途 | 何時呼叫 |
|------|------|---------|
| `run_analysis.py` | **主入口指令碼**：整合資料採集、分析、報告生成 | 推薦使用 |
| `collect_data.py` | Sorftime 資料採集（類目、Top100、關鍵詞、趨勢） | Step 1 |
| `get_reviews.py` | 競品差評資料採集 | Step 4 |
| `api_client.py` | Sorftime API 呼叫 + SSE 解析 + 編碼修復 | 每次 API 呼叫 |
| `render_dashboard.py` | 生成 Dashboard 視覺化看板（v3.1 修復版） | 報告生成階段 |
| `fix_data_json.py` | **資料驗證和修復指令碼**：校驗並自動修復 data.json | Dashboard 生成前 |
| `validate_data.py` | **資料驗證指令碼**：校驗 data.json 欄位命名和資料一致性 | 報告生成前 |

**指令碼職責**：
- **不做分析判斷**：所有分析由 LLM 完成
- **不做複雜計算**：交叉分析讓 LLM 從資料中發現
- **僅做資料搬運**：API → 結構化資料

**推薦使用方式**：

```bash
# 階段1：資料採集（基礎版 Dashboard）
python scripts/run_analysis.py "earbuds" US

# 階段2：LLM 分析完成後，生成最終版報告
python scripts/run_analysis.py "earbuds" US --final

# 其他選項
python scripts/run_analysis.py "earbuds" US --collect-only  # 僅資料採集
python scripts/run_analysis.py "earbuds" US --no-reviews     # 跳過差評採集
```

---

## 執行流程（兩階段）

**重要**：選品分析分為兩個階段，資料採集由指令碼自動完成，LLM 分析需要人工參與。

### 階段1：資料採集（指令碼自動）

```bash
python scripts/run_analysis.py "keyword" US
```

**輸出**：
- `data.json` - 基礎資料結構（不含分析結論）
- `dashboard.html` - 基礎版看板（不含決策評分、VOC 等）
- `raw/` - 原始資料檔案

**指令碼自動完成**：
1. 類目搜尋 → 獲取 nodeId
2. Top100 產品資料採集
3. 關鍵詞資料採集
4. 類目趨勢資料採集
5. 競品差評採集
6. 市場分析（價格區間、品牌分佈）

### 階段2：LLM 分析（互動式）

**必須完成的 LLM 分析任務**：

| 步驟 | 任務 | 輸出到 data.json |
|------|------|------------------|
| 1 | 屬性標註 | `product_types`、`dimensions_analysis` |
| 2 | 交叉分析 | `cross_analysis` |
| 3 | VOC 分析 | `voc_analysis.dimensions` |
| 4 | 壁壘評估 | `barriers` |
| 5 | 決策評估 | `decision` (overall_score, verdict) |

**完成後執行**：

```bash
python scripts/run_analysis.py "keyword" US --final
```

`--final` 引數會：
1. ✅ 驗證分析資料完整性
2. ✅ 更新 data.json
3. ✅ 生成完整版 Dashboard（含決策評分、VOC 等）
4. ✅ 如果資料不完整，會提示缺失的欄位

### 資料完整性檢查

也可以單獨檢查資料完整性：

```bash
python scripts/render_dashboard.py data.json --check
```

輸出示例：
```
✓ 資料完整，可以渲染完整版 Dashboard
  包含: decision.overall_score, voc_analysis.dimensions, barriers, cross_analysis
```

或

```
⚠️ 資料不完整，缺少以下欄位:
  - decision.overall_score
  - voc_analysis.dimensions

ℹ️ 請先完成 LLM 分析，然後重新執行渲染
```

---

## 執行流程（互動式）

### Step 0: 資訊收集

```
📋 選品分析 - 資訊確認

1. 產品/類目關鍵詞：[使用者提供]
2. 目標站點：[US/GB/DE/FR/IT/ES/CA/JP，預設US]
3. 選品場景：[新手入門/藍海發現/季節性/品牌打造/定向品類]
4. 約束條件（可選）：
   - 價格區間：如 $10-40
   - 月銷量：如 > 1000
   - 預算：如 10萬人民幣
```

### Step 1: 資料採集（增強版 v3.0）

**API 呼叫順序**：

| 步驟 | API | 輸出 | 說明 | 優先順序 |
|------|-----|------|------|----------|
| 0.5 | `search_categories_broadly` | blue_ocean_categories.json | **【新增】藍海市場發現** | 📋 按需 |
| 1.1 | `category_name_search` | category_info.json | 按產品名搜尋類目（使用 searchName 引數） | ⛔ 必調 |
| 1.2 | `category_report` | top100.json | Top100 產品資料 | ⛔ 必調 |
| 1.3 | `keyword_detail` × 3+ | keywords.json | 多維度關鍵詞對比 | ⛔ 必調 |
| 1.4 | `category_trend` | trend.json | 新品佔比趨勢 | ⛔ 必調 |
| 1.5 | `keyword_extends` | keyword_extends.json | **【新增】關鍵詞延伸詞（維度發現）** | 📋 推薦 |
| 1.6 | `potential_product` | potential_products.json | **【新增】潛力產品發現** | 📋 推薦 |
| 1.7 | `product_detail` × 6-10 | products.json | 競品詳情（按需） | 📋 按需 |
| 1.8 | `product_reviews` × 6-10 | reviews.json | 競品差評（按需） | 📋 按需 |

**⚠️ 重要：API 引數說明（v3.0）**

- `category_name_search` 引數：`{"amzSite": "US", "searchName": "bluetooth speaker"}`
  - **正確的類目搜尋 API，引數名是 searchName**
- `search_categories_broadly` 引數（藍海發現）：`{"amzSite": "US", "top3Product_sales_share": 0.4}`
- `potential_product` 引數（潛力產品）：`{"amzSite": "US", "monthlySales_min": 500}`
- `keyword_extends` 引數（延伸詞）：`{"amzSite": "US", "keyword": "bluetooth speaker"}`
- `category_report` 引數：`{"amzSite": "US", "nodeId": "7073956011"}`
  - **nodeId 是字串型別**

**指令碼呼叫方式**：

```python
# 方法1: 使用 collect_data.py (推薦)
from scripts.collect_data import collect_data
result = collect_data("bluetooth speaker", "US")

# 方法2: 使用 api_client.py
from scripts.api_client import SorftimeClient

client = SorftimeClient()

# 獲取類目ID（正確的方式）
category = client.search_category_by_product_name("US", "bluetooth speaker")
node_id = category[0]['nodeId']

# 獲取Top100
top100 = client.get_category_report("US", node_id)

# 獲取關鍵詞詳情
keywords = client.get_keyword_detail("US", "bluetooth speaker")
```

### Step 2: 屬性標註（LLM 驅動）

**LLM 任務**：從 Top100 標題中提取關鍵差異化維度

```markdown
## 屬性標註任務

基於以下 Top100 產品標題，提取 3-6 個關鍵差異化維度：

### 標題樣本
[提供 Top20-30 標題作為樣本]

### 提取要求
1. 識別差異化維度（如：功率、防水、續航、形態等）
2. 為每個產品標註維度值
3. 標註置信度（高/中/低）

### 輸出格式
| ASIN | 功率 | 防水 | 續航 | ... | 置信度 |
```

**對低置信度產品**：呼叫 `product_detail` 補充驗證

### Step 3: 交叉分析（LLM 直接發現）

**LLM 任務**：從標註資料中發現供需缺口

```markdown
## 交叉分析任務

基於以下已標註的 Top100 產品資料，執行交叉分析：

### 資料
[提供標註後的產品資料]

### 分析要求
1. 選擇 2-3 對有意義的維度組合（如：功率×價格、防水×場景）
2. 識別：空白點（0產品）、薄供給（≤2產品）、高需求低供給
3. 分析每個缺口的原因（技術限制？需求不存在？被忽視？）
4. 按機會價值排序

### 輸出格式
| 維度組合 | 狀態 | 產品數 | 月銷量 | 原因分析 | 機會評級 |
```

**關鍵點**：讓 LLM 直接從資料中發現規律，而不是用 Python 指令碼計算

### Step 4: 競品與 VOC 分析

**競品選擇邏輯表**（LLM 按細分段選擇）：

| ASIN | 品牌 | 選擇理由 | 型別 | 覆蓋維度 |
|------|------|----------|------|----------|
| [LLM 選擇 6-10 個代表性競品] |

**⛔ 差評維度歸類（關鍵步驟）**

**必須按維度歸類，禁止按 ASIN 組織**

**LLM 任務**：將競品差評按屬性維度歸類，並對映到品牌能力和產品方案

**輸入**：`competitor_reviews.json`（按 ASIN 組織的原始差評）
**輸出**：`data.json` 中的 `voc_analysis` 欄位（按維度歸類）

**歸類要求**：
1. **識別主要維度**（3-6 個）- 基於差評內容提取痛點類別
2. **每個維度包含**：
   - `dimension`: 維度名稱（如：音質/音量、舒適度、續航）
   - `pain_point`: 痛點描述
   - `frequency`: 提及頻次
   - `percentage`: 佔比（如 "32%"）
   - `affected_brands`: 涉及品牌列表
   - `brand_opportunity`: 品牌/供應鏈能力如何解決
   - `product_solution`: 具體產品改進方向

**輸出格式示例**：

```json
{
  "voc_analysis": {
    "dimensions": [
      {
        "dimension": "音質/音量",
        "pain_point": "音量太小，戶外聽不清",
        "frequency": 45,
        "percentage": "32%",
        "affected_brands": ["SHOKZ", "JLab"],
        "brand_opportunity": "有14.2mm大動圈供應鏈",
        "product_solution": "14.2mm動圈+音量增強模式"
      }
    ],
    "summary": "主要痛點集中在音質(32%)、舒適度(28%)、續航(18%)"
  }
}
```

**禁止的輸出方式**：
- ❌ 按 ASIN 組織：`{"B0XXX": {"reviews": [...]}}`
- ❌ 缺少頻次/佔比資料
- ❌ 缺少品牌機會和產品方案對映

### Step 5: 評估與決策

**進入壁壘評估**：

| 壁壘型別 | 等級 | 資料錨點 | 預估成本 | 緩解方案 |
|----------|------|----------|----------|----------|
| Review 壁壘 | 中/高 | Top10 均值 XXX 評論 | $XXX | Vine + PPC |
| 資金壁壘 | 中/高 | 首批備貨 + 廣告 | ¥XX | 控制首批 MOQ |
| ... | ... | ... | ... | ... |

**選品決策評估（五維評分）**：

| 維度 | 權重 | 評分(1-10) | 加權分 | 依據 |
|------|------|-----------|--------|------|
| 市場規模 | 20% | [LLM 評分] | X.X | [資料依據] |
| 競爭格局 | 25% | [LLM 評分] | X.X | [資料依據] |
| ... | ... | ... | ... | ... |
| **總分** | 100% | - | **X.XX** | **決策結論** |

**決策結論對映**：
- 7.5-10分 → **建議進入** (優先推進)
- 6.0-7.4分 → **謹慎進入** (需精準定位，明確准入條件)
- 4.0-5.9分 → **暫緩觀望** (需更多資料驗證)
- 0-3.9分 → **不建議進入** (風險大於機會)

**產品矩陣**（Tier 1 必填具體規格）：

```markdown
### Tier 1: [產品定位]

**目標市場**：[維度組合空白/機會]
**決策理由**：[資料依據]

| 維度 | 規格 | 決策依據 |
|------|------|----------|
| [維度1] | [具體值] | [為什麼] |
| [維度2] | [具體值] | [為什麼] |

**目標定價**：$XX.XX
**差異化主張**：[一句話]
**對標競品**：[ASIN] — [我們的優勢]
**預估月銷潛力**：XX-XX 件
```

### Step 6: 報告輸出

**輸出檔案**：

```
product-research-reports/
└── {category}_{site}_{YYYYMMDD}/
    ├── report.md              # Markdown 完整報告（LLM 直接輸出）
    ├── data.json              # 結構化資料（供 Dashboard 使用）
    ├── dashboard.html         # 視覺化看板（指令碼渲染）
    └── raw/                   # 資料檔案
        ├── category_info.json # 類目資訊
        ├── top100.json        # Top100 產品資料
        ├── trend.json         # 趨勢資料
        └── keywords.json      # 關鍵詞資料
```

**data.json 結構**（簡化版）：

```json
{
  "metadata": {
    "category": "bluetooth speaker",
    "site": "US",
    "date": "20260319"
  },
  "market_overview": {
    "top100_monthly_sales": 55000,
    "top100_monthly_revenue": 5200000,
    "avg_price": 95,
    "top3_product_concentration": 0.2578,
    "top3_brand_concentration": 0.5058,
    "top10_brand_concentration": 0.8234
  },
  "dimensions": [...],
  "cross_analysis": [...],
  "competitors": [...],
  "voc_analysis": {
    "dimensions": [
      {
        "dimension": "音質/音量",
        "pain_point": "音量太小，戶外聽不清",
        "frequency": 45,
        "percentage": "32%",
        "affected_brands": ["SHOKZ", "JLab"],
        "brand_opportunity": "採用更大驅動單元",
        "product_solution": "14.2mm動圈+音量增強模式"
      }
    ],
    "summary": "主要痛點集中在音質(32%)、舒適度(28%)、續航(18%)"
  },
  "barriers": [...],
  "go_nogo": {...}
}
```

**⛔ 重要：資料欄位命名規範**

| 欄位名 | 說明 | 示例 |
|--------|------|------|
| `top3_product_concentration` | Top3 **產品**銷量佔 Top100 總銷量的比例 | 0.2578 = 25.78% |
| `top3_brand_concentration` | Top3 **品牌**銷量佔 Top100 總銷量的比例 | 0.5058 = 50.58% |
| `top10_brand_concentration` | Top10 **品牌**銷量佔 Top100 總銷量的比例 | 0.8234 = 82.34% |
| `new_product_share` | 新品（上架<6個月）銷量佔比 | 0.26 = 26% |

**禁止模糊命名**：
- ❌ `top3_concentration`（不明確是產品還是品牌）
- ✅ `top3_product_concentration` 或 `top3_brand_concentration`

**⛔ 重要：VOC 分析資料結構**

`voc_analysis` 欄位必須包含按**維度歸類**的差評分析，而非按 ASIN 組織：

| 欄位 | 型別 | 說明 |
|------|------|------|
| `dimension` | string | 痛點維度（如：音質/音量、舒適度、續航等） |
| `pain_point` | string | 痛點描述 |
| `frequency` | number | 提及頻次 |
| `percentage` | string | 佔比（如 "32%"）|
| `affected_brands` | array | 涉及的品牌列表 |
| `brand_opportunity` | string | 品牌/供應鏈能力如何解決 |
| `product_solution` | string | 具體產品改進方案 |

---

## Dashboard 渲染規範

`render_dashboard.py` 負責將 `data.json` 渲染為視覺化看板。關鍵渲染規則：

### 產品維度分佈
- **必須使用表格形式**，禁止使用柱狀圖
- 雙欄佈局：左側價格區間分佈，右側產品形態分佈
- 每行顯示：維度值、產品數、佔比（帶顏色標籤）
- 佔比標籤顏色規則：≥30%藍色、≥20%綠色、≥10%黃色、<10%灰色

### 交叉分析（價格區間 × 產品形態）
- **必須使用矩陣表格形式**，禁止使用圖表
- 行：價格區間（$0-30 到 $200+）
- 列：產品形態（骨傳導、夾耳式、開放式掛耳、入耳式）
- 單元格：產品數量
- 特殊標記：
  - 競爭激烈（≥15款）：紅色"紅海"標籤
  - 市場空白（0款）且為機會點：綠色"機會"標籤
- 底部必須有洞察提示框，說明紅海和機會區域

### 示例輸出
```html
<!-- 維度分佈：雙表格佈局 -->
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
  <!-- 價格區間表格 -->
  <!-- 產品形態表格 -->
</div>

<!-- 交叉分析：矩陣表格 -->
<table>
  <thead><!-- 表頭：產品形態 --></thead>
  <tbody><!-- 行：價格區間，列：產品數 --></tbody>
</table>
<div class="insight-box">洞察：...</div>
```

---

## LLM Prompt 模板庫

詳細 Prompt 模板請參考：`references/prompt_templates.md`

包含 6 個模板：
1. 屬性標註 - 從產品標題提取差異化維度
2. 交叉分析 - 發現供需缺口
3. 競品選擇 - 選擇代表性競品
4. 差評歸類 - 按屬性維度歸類痛點
5. 選品決策評估 - 五維加權決策
6. 產品矩陣規劃 - Tier 1/2/3 具體規格

---

## 硬性規則（⛔ 不可省略）

1. ⛔ Top100 必須完整 100 條
2. ⛔ 關鍵詞至少 3 個維度對比
3. ⛔ 競品選擇 6-10 個，覆蓋量級標杆/功能差異/價格帶/痛點
4. ⛔ **差評必須按維度歸類**（非按 ASIN 歸類），輸出到 `data.json` 的 `voc_analysis` 欄位
5. ⛔ VOC 分析必須包含：頻次、佔比、涉及品牌、品牌機會、產品方案
6. ⛔ 選品決策評估必須量化評分
7. ⛔ Tier 1 產品必須具體到規格（禁止"待確認"佔位）
8. ⛔ 每個資料表後有"關鍵洞察"段落
9. ⛔ 空白/薄供給必須附帶原因分析
10. ⛔ **資料欄位命名必須清晰**：使用 `top3_product_concentration` / `top3_brand_concentration`，禁止模糊的 `top3_concentration`
11. ⛔ **資料一致性校驗**：報告生成前必須校驗 `data.json` 中的數值與報告文字一致

---

## 常見場景策略

### 場景1：新手入門（預算<15萬）
- 價格 $10-20
- 輕小件
- 無售後風險
- 中國賣家佔比 > 70%

### 場景2：藍海發現
- Top3 集中度 < 30%
- 新品佔比 > 15%
- 關鍵詞首頁評論 < 500

### 場景3：定向品類分析（使用者已指定）
- 跳過類目掃描，直接進入資料採集
- ⛔ 必須執行屬性標註
- ⛔ 必須執行交叉分析
- ⛔ 必須執行選品決策評估（五維評分）

---

## 與其他 Skills 的關係

```
category-selection (品類篩選五維評分)
        ↓
product-research (深度選品調研) ← 本 Skill
        ↓
amazon-analyse (競品 Listing 深挖)
        ↓
review-analysis (評論深度分析)
```

**區別**：
- `category-selection`：品類級別的快速篩選，五維評分
- `product-research`：指定品類的深度調研，多維度分析 + 選品決策評估
- `amazon-analyse`：單個競品 Listing 的詳細分析
- `review-analysis`：評論的深度痛點分析

---

## 支援的站點

US, GB, DE, FR, IT, ES, CA, JP, MX, AE, AU, BR, SA

---

## 注意事項

1. **API Key**：自動從 `.mcp.json` 讀取
2. **資料時效**：Sorftime 資料可能有 1-7 天延遲
3. **API 限流**：每批最多 8 個併發請求
4. **編碼問題**：指令碼自動處理 Unicode-escape 和 Mojibake
5. **原始資料**：所有 API 響應儲存在 `raw/` 目錄供驗證

---

## 故障排查

### 常見錯誤及解決方案

| 錯誤資訊 | 原因 | 解決方案 |
|----------|------|----------|
| `HTTP Error 406: Not Acceptable` | API引數錯誤 | 檢查引數名是否為 `searchName` 而非 `productName` |
| `An error occurred invoking 'xxx'` | API工具不存在 | 檢查 TOOLS 對映表中的工具名稱 |
| `未查詢到對應產品` | ASIN無效或站點錯誤 | 驗證ASIN格式, 確認產品在該站點銷售 |
| `Authentication required` | API Key錯誤 | 檢查 `.mcp.json` 中的 key 引數 |
| 中文亂碼 | Mojibake編碼 | 指令碼自動修復, 或執行 `fix_encoding.py` |
| `IndentationError: unexpected indent` | Windows 命令列問題 | 使用指令碼檔案而非 `python -c` |
| `輸出目錄路徑錯誤` | 相對路徑問題 | 使用 `run_analysis.py`，自動處理路徑 |
| `NameError: name 'xxx' is not defined` | 缺少 datetime 匯入 | 檢查指令碼 import 語句 |
| **Dashboard 渲染問題** | | |
| Dashboard 顯示空白 | data.json 結構不匹配 | **v3.5 已修復**：`run_analysis.py` 自動渲染 Dashboard |
| Dashboard 未自動生成 | 舊版本未整合渲染 | **v3.5 已修復**：資料採集完成後自動渲染 |
| `PermissionError: [Errno 13]` | 傳遞目錄路徑而非檔案路徑 | 使用絕對路徑呼叫：`python render_dashboard.py -o output.html data.json` |
| `unrecognized arguments` | 引數順序錯誤 | 正確格式：`python render_dashboard.py -o dashboard.html data.json` |
| Dashboard 缺少 VOC 資料 | LLM 未生成完整 voc_analysis | 確保 LLM 生成包含 voc_analysis.dimensions 的完整 data.json |
| Dashboard 交叉分析為空 | price_type_matrix 資料缺失 | 確保資料採集包含價格區間分析 |
| `KeyError: 'xxx'` | 欄位名不一致 | **v3.4 已修復**：支援新舊欄位名相容 |
| `AttributeError: 'str' object has no attribute 'get'` | data.json 格式問題 | **v3.4 已修復**：自動轉換為列表格式 |

### Dashboard 手動渲染方法

如果自動渲染失敗，可以手動呼叫：

```bash
# 從輸出目錄呼叫
python .claude/skills/product-research/scripts/render_dashboard.py \
    -o product-research-reports/{keyword}_{site}_{date}/dashboard.html \
    product-research-reports/{keyword}_{site}_{date}/data.json

# 或者使用絕對路徑
python "D:\amazon-mcp\.claude\skills\product-research\scripts\render_dashboard.py" \
    -o "D:\amazon-mcp\product-research-reports\{keyword}_{site}_{date}\dashboard.html" \
    "D:\amazon-mcp\product-research-reports\{keyword}_{site}_{date}\data.json"
```

### API 工具名稱對照表

| 功能 | 工具名稱 | 引數 |
|------|----------|------|
| 類目搜尋 | `category_name_search` | `amzSite`, `searchName` |
| 類目報告 | `category_report` | `amzSite`, `nodeId` |
| 類目趨勢 | `category_trend` | `amzSite`, `nodeId`, `trendIndex` |
| 關鍵詞詳情 | `keyword_detail` | `amzSite`, `keyword` |
| 產品詳情 | `product_detail` | `amzSite`, `asin` |
| 產品評論 | `product_reviews` | `amzSite`, `asin`, `reviewType` |

### 除錯技巧

1. **啟用詳細輸出**: 在指令碼中新增 `print()` 除錯資訊
2. **檢查原始響應**: 檢視 SSE 響應的實際內容
3. **分步執行**: 使用 Python 互動式環境逐行除錯
4. **驗證API Key**: `curl "https://mcp.sorftime.com?key=YOUR_KEY" -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'`

---

*版本: v3.6 (兩階段工作流 + 資料驗證) | 最後更新: 2026-03-19*
