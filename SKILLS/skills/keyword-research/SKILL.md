---
name: "keyword-research"
description: "亞馬遜關鍵詞深度調研與智慧分類分析。基於 Sorftime MCP 資料採集 2000+ 關鍵詞，透過 LLM Agent 按 8 維度智慧分類（否定詞、品牌詞、材質詞、場景詞、屬性詞、功能詞、核心詞、其他），生成 Markdown 報告、CSV 詞庫和 HTML 儀表板。觸發方式：/keyword-research {ASIN} {SITE}"
---

# 關鍵詞調研分析 Skill

## 快速參考

| 步驟 | Sorftime API | 用途 | 資料量 |
|------|--------------|------|--------|
| 1 | `product_traffic_terms` | 產品流量關鍵詞 | 50-200 |
| 2 | `competitor_product_keywords` | 競品佈局關鍵詞 | 100-500 |
| 3 | `category_keywords` | 類目核心關鍵詞 | 100-500 |
| 4 | `keyword_related_words` | 長尾詞擴充套件 | 1000-2000 |
| 5 | **LLM Agent** | 8 維智慧分類 | 全量 |

**一鍵執行**:
```bash
# 在 Claude Code 環境中執行（自動觸發 LLM 分類）
python .claude/skills/keyword-research/scripts/workflow.py B07PWTJ4H1 US --claude-code-env
```

**其他選項**:
```bash
# 跳過分類，僅採集資料（後續可手動LLM分類）
python .claude/skills/keyword-research/scripts/workflow.py B07PWTJ4H1 US --skip-classification

# 禁用LLM分類，使用規則分類
python .claude/skills/keyword-research/scripts/workflow.py B07PWTJ4H1 US --disable-llm-classification
```

## 觸發條件

當使用者使用以下方式請求時啟動此分析流程：
- **命令**: `/keyword-research {ASIN} {站點}`
- **示例**: `/keyword-research B07PWTJ4H1 US`
- **自然語言**: "分析這個產品的關鍵詞詞庫"、"調研 B07PWTJ4H1 的關鍵詞"

---

## 角色設定

你是一位擁有 10 年經驗的"亞馬遜 PPC 廣告專家"和"關鍵詞策略分析師"。你精通亞馬遜 A9 演算法和關鍵詞佈局策略，能夠從海量關鍵詞中識別出高價值詞和需要排除的詞。

---

## 資料採集策略：方案 A（基於 ASIN 的深度分析）

```
輸入: ASIN + 站點 + (可選) 產品資訊
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 1: 基礎資料採集                                         │
├─────────────────────────────────────────────────────────────┤
│ 1. product_traffic_terms      → 產品流量詞 (50-200個)       │
│ 2. competitor_product_keywords → 競品佈局詞 (100-500個)     │
│ 3. category_keywords           → 類目核心詞 (100-500個)      │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: 長尾詞擴充套件                                          │
├─────────────────────────────────────────────────────────────┤
│ 從基礎詞中選擇 Top 30 核心詞                                 │
│ → 對每個呼叫 keyword_related_words (50-100個延伸詞)         │
│ → 預計獲取 1000-2000 個長尾詞                               │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: 資料清洗                                            │
├─────────────────────────────────────────────────────────────┤
│ 1. 去重（歸一化：小寫、去除特殊字元）                        │
│ 2. 過濾無效詞（過短、非英文、亂碼）                          │
│ 3. 合併搜尋量/CPC 等指標                                    │
└─────────────────────────────────────────────────────────────┘
  ↓
最終詞庫: 2000+ 關鍵詞
```

---

## 關鍵詞分類：8 維智慧分類模型

### 分類維度

| 維度 | 標識 | 識別規則 | 應用策略 |
|------|------|----------|----------|
| **否定/敏感詞** | NEGATIVE | 與產品不相關、描述不符的詞 | 直接新增為否定關鍵詞 |
| **品牌詞** | BRAND | 競品品牌名稱 | 競品打法或否定 |
| **材質詞** | MATERIAL | 產品材質相關詞 | 精準片語匹配 |
| **場景詞** | SCENARIO | 使用場景/位置詞 | 按場景拆分廣告組 |
| **屬性修飾詞** | ATTRIBUTE | 產品屬性/特性詞 | 長尾精準匹配 |
| **功能詞** | FUNCTION | 產品功能相關詞 | 廣泛匹配擴流 |
| **核心產品詞** | CORE | 產品核心名稱 | 大詞投放佔領坑位 |
| **其他** | OTHER | 未分類、拼寫錯誤、其他語言 | 補充埋詞 |

### 分類識別示例（以 Coat Rack 為例）

```
產品資訊: Coat Rack Wall Mount, Wood, 5 Hooks, Entryway

否定詞: freestanding, over door, floor, tree, shoe
品牌詞: umbra, simplehuman, mDesign, household essentials
材質詞: wood, wooden, metal, aluminum, bamboo
場景詞: entryway, bathroom, mudroom, garage, bedroom
屬性詞: wall mount, heavy duty, rustic, vintage, expandable, 5 hook
功能詞: hanging, storage, organizer, display
核心詞: coat rack, hook, hanger, hat rack, towel rack
其他: coatrac (拼寫錯誤), perchero (西語)
```

---

## 執行流程

### 階段一：資料採集

#### Step 1.1: 獲取產品流量詞

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"product_traffic_terms","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

**返回資料**: 關鍵詞列表，包含搜尋量、CPC 等指標

#### Step 1.2: 獲取競品佈局詞

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"competitor_product_keywords","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

**返回資料**: 競品在各關鍵詞下的排名位置

#### Step 1.3: 獲取類目核心詞

```bash
# 首先獲取產品詳情以獲取 NodeID
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"ASIN"}}}'

# 然後獲取類目關鍵詞
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"category_keywords","arguments":{"amzSite":"US","nodeId":"NODE_ID"}}}'
```

#### Step 1.4: 長尾詞擴充套件

從基礎詞中選擇 Top 30 核心，對每個呼叫：

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":N,"method":"tools/call","params":{"name":"keyword_related_words","arguments":{"amzSite":"US","searchKeyword":"KEYWORD"}}}'
```

---

### 階段二：LLM 智慧分類

#### 分類提示詞模板

```
你是一位亞馬遜關鍵詞分類專家。請根據以下產品資訊，將關鍵詞列表按 8 個維度分類。

【產品資訊】
產品名稱: {product_name}
材質: {material}
核心屬性: {features}
使用場景: {use_cases}
否定特徵: {negative_features}

【分類維度】
1. NEGATIVE: 不相關的詞，需直接否定
2. BRAND: 競品品牌名稱
3. MATERIAL: 材質相關詞 (wood, metal, aluminum...)
4. SCENARIO: 使用場景詞 (entryway, bathroom...)
5. ATTRIBUTE: 屬性修飾詞 (wall mount, heavy duty...)
6. FUNCTION: 功能詞 (hanging, storage...)
7. CORE: 核心產品詞 (coat rack, hook...)
8. OTHER: 其他（拼寫錯誤、其他語言等）

【待分類關鍵詞】
{keywords_json}

【輸出格式】
請以 JSON 格式輸出：
{
  "NEGATIVE": ["word1", "word2", ...],
  "BRAND": [...],
  ...
}
```

#### 批次處理策略

- **批次大小**: 每批 150 個關鍵詞
- **並行處理**: 可併發多個批次
- **結果合併**: 統計各分類數量，彙總關鍵詞

---

### 階段三：報告生成

#### 輸出檔案結構

```
keyword-reports/
└── {ASIN}_{Site}_{YYYYMMDD}/
    ├── report.md                    # Markdown 分析報告
    ├── keywords.csv                 # 完整關鍵詞詞庫（分類後）
    ├── negative_words.txt           # 否定詞清單
    ├── brand_words.txt              # 品牌詞清單
    ├── categorized_summary.json     # 分類統計
    └── dashboard.html               # HTML 視覺化儀表板
```

#### keywords.csv 格式

```csv
keyword,category,search_volume,cpc,competition,application,relevance_score
coat rack,CORE,54000,1.85,high,廣泛匹配,1.00
wooden coat rack,MATERIAL,12000,1.25,medium,精準匹配,0.95
freestanding coat rack,NEGATIVE,4500,0.85,low,直接否定,0.00
...
```

---

## 產品資訊支援（可選）

為提高分類準確性，支援使用者提供產品資訊：

### 輸入方式

**方式 1**: 命令列引數
```bash
python workflow.py B07PWTJ4H1 US --product-info product.json
```

**方式 2**: 互動式收集
```bash
請輸入產品核心屬性（用逗號分隔）:
> Wall Mount, 5 Hooks, 16.5 inches, Heavy Duty
```

### 產品資訊 JSON 格式

```json
{
  "product_name": "Coat Rack Wall Mount",
  "material": "Wood",
  "features": ["Wall Mount", "5 Hooks", "16.5 inches", "Heavy Duty"],
  "use_cases": ["Entryway", "Bathroom", "Mudroom", "Garage"],
  "negative_features": ["Freestanding", "Over Door", "Floor"]
}
```

---

## Sorftime API 參考

### 關鍵詞相關介面

| 介面 | 呼叫消耗 | 引數 | 返回 |
|------|----------|------|------|
| `product_traffic_terms` | 1 | asin, site | 產品流量詞 |
| `competitor_product_keywords` | 1 | asin, site | 競品佈局詞 |
| `category_keywords` | 1 | nodeId, site | 類目核心詞 |
| `keyword_related_words` | 1 | searchKeyword, site | 延伸長尾詞 |
| `keyword_detail` | 1 | keyword, site | 關鍵詞詳情 |
| `product_detail` | 1 | asin, site | 產品詳情 |

### 呼叫格式

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":N,"method":"tools/call","params":{"name":"TOOL_NAME","arguments":{"amzSite":"US","KEY":"VALUE"}}}'
```

---

## 支援的站點

**Amazon**: US, GB, DE, FR, IN, CA, JP, ES, IT, MX, AE, AU, BR, SA

---

## 注意事項

1. **API Key 配置**: 自動從 `.mcp.json` 讀取
2. **資料去重**: 歸一化處理（小寫、去除特殊字元）
3. **LLM 分類**: 批次處理，每批 150 個關鍵詞
4. **輸出編碼**: UTF-8，支援中文和特殊字元
5. **報告命名**: `{ASIN}_{Site}_{YYYYMMDD}` 格式

---

## 故障排查

### 問題 1: API 返回 "未查詢到對應產品"
**原因**: ASIN 不存在於 Sorftime 資料庫
**解決**:
1. 使用 `product_search` 驗證 ASIN
2. 檢查站點是否正確

### 問題 2: 分類結果不準確
**原因**: 缺少產品資訊上下文或使用了規則分類
**解決**:
1. 提供產品資訊 JSON 檔案
2. 在 Claude Code 環境中執行以使用 LLM 分類
3. 手動執行 LLM 分類後儲存到 `categorized_result.json`

### 問題 3: 長尾詞擴充套件數量不足
**原因**: 核心詞選擇不準確或 API 限流
**解決**:
1. 調整核心詞選擇策略，增加搜尋量權重
2. 降低 `--long-tail-limit` 數量避免 API 限流
3. 使用 `--skip-long-tail` 跳過長尾擴充套件

### 問題 4: 分類顯示 "分類失敗或未提供結果" 或 使用了規則分類
**原因**: 在命令列環境中執行，沒有觸發 LLM 分類
**解決**:
1. 使用 `--claude-code-env` 引數強制啟用 LLM 分類模式：
   ```bash
   python workflow.py B07PWTJ4H1 US --claude-code-env
   ```
2. 系統會輸出分類提示詞，複製提示詞傳送給 Claude 執行分類
3. 將分類結果儲存為 `categorized_result.json`
4. 重新執行 workflow.py 會自動載入分類結果並重新生成報告

### 問題 5: 如何手動進行 LLM 分類
**場景**: 採集了資料但分類不準確
**解決**:
1. 檢視輸出目錄中的 `classification_prompt.txt`
2. 將提示詞傳送給 Claude 執行分類
3. 將分類結果儲存為 `categorized_result.json`
4. 執行報告重新生成指令碼

---

## 參考文件

- [Sorftime API 文件](references/sorftime-keyword-api.md)
- [分類規則說明](references/classification-rules.md)

---

## 手動 LLM 分類流程

如果規則分類結果不準確，可以手動執行 LLM 分類：

### 步驟 1: 檢視分類提示詞
```bash
cat keyword-reports/{ASIN}_{Site}_{YYYYMMDD}/classification_prompt.txt
```

### 步驟 2: 將提示詞傳送給 Claude
複製整個提示詞內容，傳送給 Claude 執行分類

### 步驟 3: 儲存分類結果
將 Claude 返回的 JSON 儲存到：
```bash
keyword-reports/{ASIN}_{Site}_{YYYYMMDD}/categorized_result.json
```

### 步驟 4: 重新生成報告

`regenerate_reports.py` 支援多種使用方式：

#### 方式 1: 從報告目錄內執行（自動檢測）
```bash
cd keyword-reports/{ASIN}_{Site}_{YYYYMMDD}/
python ../../.claude/skills/keyword-research/scripts/regenerate_reports.py
```

#### 方式 2: 指定 ASIN 和站點
```bash
python .claude/skills/keyword-research/scripts/regenerate_reports.py --asin B0FG6QG8C8 --site US
```

#### 方式 3: 指定完整輸出目錄
```bash
python .claude/skills/keyword-research/scripts/regenerate_reports.py --dir "keyword-reports\B0FG6QG8C8_US_20260314"
```

#### 方式 4: 列出所有可用的報告目錄
```bash
python .claude/skills/keyword-research/scripts/regenerate_reports.py --list
```

---

## 版本更新記錄

### v1.3 (2026-03-14)
- ✅ **最佳化 regenerate_reports.py**: 移除硬編碼 ASIN
- ✅ **支援多種使用方式**:
  - 從報告目錄內執行（自動檢測）
  - 使用 `--asis` 和 `--site` 引數指定
  - 使用 `--dir` 引數指定完整目錄
  - 使用 `--list` 列出所有可用報告
- ✅ **改進錯誤提示**: 更友好的錯誤資訊和幫助文件

### v1.2 (2026-03-14)
- ✅ 修復 LLM 分類觸發問題
- ✅ 新增 `--claude-code-env` 引數強制啟用 LLM 分類
- ✅ 改進環境檢測邏輯
- ✅ 在 Claude Code 環境中自動觸發 LLM 分類
- ✅ 分類完成後自動使用 LLM 結果重新生成報告

### v1.1 (2026-03-14)
- ✅ 新增 Claude Code 環境檢測
- ✅ 新增 `--skip-classification` 選項
- ✅ 改進規則分類：擴充套件 IP 品牌詞識別
- ✅ 改進規則分類：新增主題屬性詞
- ✅ 更新故障排查文件

### v1.0 (2026-03-13)
- 初始版本
- 支援 Sorftime API 資料採集
- 支援 8 維智慧分類
- 生成 Markdown/CSV/HTML 報告

---

*本技能版本: v1.3 | 最後更新: 2026-03-14*
