---
name: "category-selection"
description: "亞馬遜品類自動化選品分析技能。透過五維評分模型對亞馬遜品類進行深度市場調研，生成Markdown分析報告。當使用者使用 /category-selection 命令或提出'分析XX品類'、'XX品類市場調研'、'XX品類選品'等需求時觸發此技能。支援配置分析數量，預設Top20。"
---

## 快速參考

### 一鍵執行工作流 (推薦)

```bash
# 使用品類名稱
python .claude/skills/category-selection/scripts/workflow.py "Sofas" US 20

# 直接使用 NodeID (推薦，避免類目搜尋問題)
python .claude/skills/category-selection/scripts/workflow.py 679394011 US 20

# 指定分析數量
python .claude/skills/category-selection/scripts/workflow.py "Kitchen" US 50
```

**重要更新 (v4.0)**:
- ✅ **自動讀取 API Key**: 無需設定環境變數，自動從 `.mcp.json` 讀取
- ✅ **修復控制字元**: 自動處理 JSON 字串值中的未轉義換行符、製表符
- ✅ **改進類目搜尋**: 支援模糊匹配和關鍵詞變體
- ✅ **詳細日誌**: 執行日誌儲存到 `execution.log`

### 核心 API 工具

| 步驟 | 工具/操作 | 用途 | 返回資料大小 |
|------|----------|------|-------------|
| 1. 搜尋類目 | `category_name_search` | 獲取類目 nodeId | 小 |
| 2. 類目報告 | `category_report` | 獲取 Top 產品列表和統計資料 | **大 (>25KB)** |
| 3. 產品詳情 | `product_detail` | 獲取單個產品詳情 | 小 |
| 4. 類目關鍵詞 | `category_keywords` | 獲取類目核心關鍵詞 | **大 (>25KB)** |
| 5. 類目趨勢 | `category_trend` | 獲取25個月曆史趨勢 | 中 |
| 6. 1688採購 | `products_1688` | 獲取採購成本資料 | 小 |

### 呼叫格式
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":N,"method":"tools/call","params":{"name":"TOOL_NAME","arguments":{"amzSite":"US","nodeId":"NODE_ID"}}}'
```

---

## 觸發條件

當使用者使用以下方式請求時，啟動此分析流程：
- **命令**: `/category-selection {品類名稱} {站點} [--limit N]`
- **示例**: `/category-selection "Sofas" US --limit 20`
- **自然語言**: "分析Amazon美國站的Sofas品類"、"Sofas品類市場調研"、"Sofas品類選品"

---

## 角色設定

你是一位擁有10年經驗的"亞馬遜選品專家"和"市場分析師"。你精通品類分析方法論，能夠透過資料洞察市場機會、競爭格局和進入壁壘，為使用者提供可執行的選品建議。

---

## 五維評分模型 (標準版)

**評分標準詳解**:

| 維度 | 分值 | 評分標準 | 資料來源 |
|------|------|----------|----------|
| **市場規模** | 20 分 | >$10M=20分, >$5M=17分, >$1M=14分, 其他=10分 | 類目月銷額 (top100產品月銷額) |
| **增長潛力** | 25 分 | 低評論產品佔比>40%=22分, >20%=18分, 其他=14分 | 評論數<100的產品佔比 |
| **競爭烈度** | 20 分 | Top3品牌佔比<30%=18分, <50%=14分, 其他=8分 | CR3 品牌集中度 |
| **進入壁壘** | 20 分 | Amazon佔比<20%且新品>40%=20分, 其他組合6-18分 | Amazon自營佔比 + 低評論佔比 |
| **利潤空間** | 15 分 | 均價>$300=12分, >$150=10分, >$50=7分, 其他=4分 | Top100產品平均價格 |

**評級標準**:

| 總分 | 評級 | 建議 |
|------|------|------|
| 80-100 | 優秀 | 強烈推薦進入 |
| 70-79 | 良好 | 可以考慮進入 |
| 50-69 | 一般 | 謹慎進入 |
| 0-49 | 較差 | 不建議進入 |

**完整標準請參考**: [scoring-standard.md](references/scoring-standard.md)

---

## 完整分析流程

### 階段一: 資料收集

#### 步驟 1: 搜尋類目獲取 nodeId

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"category_name_search","arguments":{"amzSite":"US","searchName":"品類關鍵詞"}}}'
```

**處理多個類目結果時**：
- 大類目（如 "Clothing, Shoes & Jewelry"）通常只返回子類目列表
- 展示給使用者讓其選擇最匹配的類目
- 或使用具體的子類目 NodeID 直接查詢

**常見類目 NodeID 參考**:
```
Traditional Laptop Computers: 13896615011
2 in 1 Laptop Computers: 13896609011
Women's Fashion Sneakers: 679394011
Women's Road Running Shoes: 14210388011
Men's Fashion Sneakers: 679312011
Kitchen Storage Accessories: 3744031
```

#### 步驟 2: 獲取類目報告 (Top100 + 統計)

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"category_report","arguments":{"amzSite":"US","nodeId":"NODE_ID"}}}'
```

**關鍵**: `category_report` 返回資料通常>25KB，會儲存到臨時檔案

**響應處理**:
```bash
# 使用 workflow.py 自動處理 (推薦)
python .claude/skills/category-selection/scripts/workflow.py "Sofas" US 20

# 或手動解碼 SSE 響應
python .claude/skills/category-selection/scripts/sse_decoder.py {temp_file} {output_dir} 20
```

#### 步驟 3: 獲取 Top N 產品詳情 (併發)

```bash
# 併發獲取 Top3 產品詳情
curl ... '{"id":3,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"ASIN1"}}}' &
curl ... '{"id":4,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"ASIN2"}}}' &
curl ... '{"id":5,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"ASIN3"}}}' &
wait
```

#### 步驟 4: 獲取類目關鍵詞 (可選)

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"category_keywords","arguments":{"amzSite":"US","nodeId":"NODE_ID","page":1}}}'
```

**處理關鍵詞資料**:
```bash
python .claude/skills/category-selection/scripts/keywords_parser.py \
  {temp_file} \
  {output_dir} \
  20
```

#### 步驟 5: 獲取歷史趨勢資料 (可選)

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"category_trend","arguments":{"amzSite":"US","nodeId":"NODE_ID"}}}'
```

**趨勢資料型別**:
- 類目月銷量趨勢 (25個月)
- 平均售價趨勢
- 平均星級趨勢
- 品牌數量趨勢

### 階段二: 資料分析

#### 核心分析指標

**1. 市場集中度分析**
```python
# HHI 指數 (赫芬達爾-赫希曼指數)
# 計算: 各品牌市場份額平方和 × 10000
# 解讀: <1500=低集中度, 1500-2500=中等, >2500=高集中度

# CR3/CR5 (前N品牌集中度)
# 計算: 前N大品牌銷量佔比
# 解讀: <30%=分散, 30-50%=中等, >50%=集中
```

**2. 品牌分析**
```python
# 品牌分佈: 按銷量/銷額排序
# 品牌數量: 統計獨立品牌數
# 品牌多樣性: HHI 指數評估
```

**3. 賣家來源分析**
```python
# Amazon 自營佔比
# 中國賣家佔比
# 美國本土賣家佔比
# 其他國際賣家佔比
```

**4. 價格分析**
```python
# 價格區間分佈
# 平均價格
# 價格中位數
# 價格標準差
```

**5. 新品分析**
```python
# 新產品定義: 上架時間 < 90天
# 新品佔比: 新品數量 / 總數量
# 新品表現: 新品平均銷量、評論數
```

### 階段三: 報告生成

#### 生成完整報告

```bash
# 一鍵生成所有報告格式
python .claude/skills/category-selection/scripts/workflow.py "Sofas" US 20

# 或分步驟生成
python .claude/skills/category-selection/scripts/generate_reports.py {data_json}
```

**輸出檔案結構**:
```
category-reports/
└── {Category}_{Site}_{YYYYMMDD}/
    ├── report.md                      # Markdown 分析報告
    ├── data.json                      # 完整解碼資料 (中文鍵)
    ├── top_products.json              # Top N 產品列表
    ├── scores.json                    # 五維評分結果
    ├── execution.log                  # 執行日誌 (v4.0 新增)
    ├── keywords.json                  # 類目關鍵詞
    ├── trend_data.json                # 25個月趨勢資料
    ├── adapted_data.json              # Excel 適配資料 (英文鍵)
    ├── category_analysis_report.xlsx  # Excel 報告
    ├── dashboard.html                 # HTML 視覺化儀表板
    ├── data/                          # 原始資料目錄
    │   ├── statistics.csv             # 統計資料
    │   ├── products.csv               # 產品列表
    │   └── scores.csv                 # 評分詳情
    └── *_raw.txt                      # 原始 SSE 響應
```

---

## 資料處理工具

### 核心工具指令碼

| 指令碼 | 用途 | 版本 |
|------|------|------|
| `workflow.py` | 一鍵執行完整分析流程 | **v4.0** |
| `sse_decoder.py` | 解碼 category_report SSE 響應 | v6.0 |
| `keywords_parser.py` | 解碼 category_keywords 響應 | v3.0 |
| `trend_parser.py` | 解析趨勢資料 | v1.0 |
| `data_adapter.py` | 資料格式轉換 (中文→英文鍵) | v1.0 |
| `data_utils.py` | 資料處理工具類 | v2.0 |
| `generate_reports.py` | 統一報告生成器 | v3.0 |
| `generate_excel_report.py` | Excel 報告生成 | v2.0 |
| `generate_markdown_report.py` | Markdown 報告生成 | v2.0 |
| `fix_encoding.py` | 編碼修復工具 | v1.0 |

### 資料欄位對映

**API 響應欄位 → 標準化欄位**:

| API 欄位 | 標準化欄位 | 說明 |
|----------|-----------|------|
| ASIN | asin | 產品唯一標識 |
| 標題/title | title | 產品標題 |
| 價格/price | price | 當前售價 |
| 月銷量/monthlySales | monthly_sales | 月銷量 |
| 月銷額/monthlyRevenue | monthly_revenue | 月銷售額 |
| 評論數/reviews | review_count | 評論數量 |
| 星級/rating | rating | 平均評分 |
| 品牌/brand | brand | 品牌名稱 |
| 賣家/seller | seller | 賣家名稱 |
| 上架時間/daysOnline | days_online | 上架天數 |

---

## HTML 視覺化儀表板

### 特性
- 基於 ECharts 的互動式圖表
- 五維評分視覺化進度條
- KPI 指標卡片展示
- 7 個動態圖表：銷量趨勢、價格趨勢、價格分佈、評分分佈、品牌份額、賣家來源、品牌評分趨勢
- Top50 產品詳細表格
- 關鍵發現智慧分析

### 模板變數支援

| 變數型別 | 示例變數 | 說明 |
|---------|---------|------|
| 基礎資訊 | `{{CATEGORY_NAME}}`, `{{SITE}}`, `{{DATA_DATE}}` | 報告基本資訊 |
| 五維評分 | `{{MARKET_SIZE_SCORE}}`, `{{MARKET_SIZE_PERCENT}}` | 各維度得分和進度條百分比 |
| KPI指標 | `{{TOTAL_PRODUCTS}}`, `{{AVG_PRICE}}`, `{{CR3}}` | 關鍵指標資料 |
| 圖表資料 | `{{SALES_TREND_DATA}}`, `{{BRAND_SHARE_DATA}}` | JavaScript JSON 資料 |
| 分析結論 | `{{CONCENTRATION_LEVEL}}`, `{{RECOMMENDATION}}` | 智慧分析文字 |

---

## 故障排查

### 常見問題與解決方案 (v4.0 更新)

#### 1. API Key 未設定
**問題**: `❌ API Key 未設定` 或 `Authentication required`

**原因**:
1. 環境變數 `SORFTIME_API_KEY` 未設定
2. `.mcp.json` 檔案不存在或格式錯誤

**解決方案** (v4.0 已修復):
- workflow.py v4.0 會自動從 `.mcp.json` 讀取 API Key
- 確保專案根目錄存在 `.mcp.json` 檔案，格式如下：
```json
{
  "mcpServers": {
    "sorftime": {
      "url": "https://mcp.sorftime.com?key=YOUR_API_KEY"
    }
  }
}
```

**手動設定環境變數 (備用)**:
```bash
# Windows PowerShell
$env:SORFTIME_API_KEY="your_api_key"

```

#### 2. JSON 解析失敗 - 未轉義的控制字元
**問題**: `JSONDecodeError: Invalid control character at: line 1 column 3401`

**原因**: API 返回的 JSON 字串值中包含原始的換行符（\n）、製表符（\t）等控制字元，這些控制字元沒有被正確轉義

**示例**:
```json
// 錯誤格式（API 返回的原始格式）
{"標題": "類目：Renewed Laptops，排名:2
類目：Traditional Laptops，排名:11"}

// 正確格式
{"標題": "類目：Renewed Laptops，排名:2\\n類目：Traditional Laptops，排名:11"}
```

**解決方案** (v4.0 已修復):
- `escape_control_chars_in_json_strings()` 函式自動跳脫字元串值內的控制字元
- 該函式只處理字串值內部的控制字元，不影響 JSON 結構

#### 3. 類目未找到
**問題**: 搜尋類目時返回"未查詢到對應類目"

**原因**:
1. 大類目（如 "Computers & Accessories"）可能只返回子類目列表
2. 類目名稱不準確

**解決方案** (v4.0 已改進):
1. workflow.py v4.0 會自動嘗試多種搜尋變體
2. 使用更具體的子類目名稱
3. **推薦**: 直接使用類目 NodeID 查詢

**獲取 NodeID 的方法**:
```bash
# 先用大類目搜尋，檢視返回的子類目列表
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"category_name_search","arguments":{"amzSite":"US","searchName":"Laptop"}}}'
```

#### 4. 資料解析失敗 (Mojibake 編碼問題)
**問題**: data.json 中的中文顯示為 "Top100äº§å" 等亂碼

**原因**: API 返回 Unicode-escape 格式 (\u4ea7\u54c1)，解碼後產生 Mojibake

**解決方案** (v4.0 已自動修復):
- `fix_mojibake()` 函式自動修復編碼問題
- 在 Unicode-escape 解碼後立即應用 `.encode('latin-1').decode('utf-8')`

#### 5. Python dict 格式問題
**問題**: "Expecting property name enclosed in double quotes"

**原因**: API 返回 Python dict 格式（單引號），不是標準 JSON

**解決方案** (v4.0 已修復):
- `python_dict_to_json()` 函式正確處理單引號轉換
- 同時處理 True/False/None 字面量

#### 6. 大類目搜尋失敗
**問題**: "Computers & Accessories" 等大類目搜尋無結果

**解決方案**:
1. 使用子類目名稱（如 "Laptops", "Computer Accessories"）
2. 先搜尋大類目獲取子類目列表，讓使用者選擇
3. 直接使用已知 NodeID

### 版本更新記錄

| 指令碼 | 版本 | 更新內容 |
|------|------|----------|
| `workflow.py` | **v4.0** | ✅ 從 .mcp.json 自動讀取 API Key<br>✅ 修復 JSON 字串中未轉義的控制字元<br>✅ 改進類目搜尋策略<br>✅ 新增執行日誌<br>✅ 更詳細的錯誤資訊 |
| `sse_decoder.py` | v6.0 | Mojibake 自動修復、括號匹配、Python dict 轉換 |
| `generate_reports.py` | v3.0 | 完整變數替換、分析文字生成 |

### 除錯技巧

1. **檢視執行日誌**:
```bash
# workflow.py v4.0 會自動儲存執行日誌
cat category-reports/{Category}_{Site}_{YYYYMMDD}/execution.log
```

2. **檢視原始響應**:
```bash
# workflow.py 會自動儲存原始 SSE 響應
cat category-reports/{Category}_{Site}_{YYYYMMDD}/category_report_raw.txt
```

3. **檢查編碼問題**:
```python
# 檢查檔案位元組
with open('data.json', 'rb') as f:
    print(f.read(100))
```

4. **驗證 JSON 格式**:
```bash
# 使用 Python 驗證 JSON
python -m json.tool data.json
```

5. **測試 API 連線**:
```bash
curl -s -X POST "https://mcp.sorftime.com?key={YOUR_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"category_name_search","arguments":{"amzSite":"US","searchName":"Kitchen"}}}'
```

---

## 支援的站點

**Amazon**: US, GB, DE, FR, IN, CA, JP, ES, IT, MX, AE, AU, BR, SA
**TikTok**: US, GB, MY, PH, VN, ID
**1688**: 中國批發平臺

---

## 注意事項

1. **API Key 配置**:
   - 推薦在 `.mcp.json` 中配置（v4.0 自動讀取）
   - 也可以使用環境變數 `SORFTIME_API_KEY`
2. **引數名稱**: 使用 `amzSite` 而非 `site`
3. **id 遞增**: 每個請求的 `id` 欄位必須遞增 (1, 2, 3...)
4. **併發限制**: 建議最多 3-5 個併發請求
5. **資料時效**: 資料可能有 1-7 天延遲
6. **報告命名**: 使用 `{Category}_{Site}_{YYYYMMDD}` 格式

---

## 參考文件

- [評分標準詳解](references/scoring-standard.md)
- [API 快速參考](references/api-quick-reference.md)
- [Sorftime MCP API 文件](references/sorftime-mcp-api.md)
- [類目 API 參考](references/category-api-reference.md)

---

*本 Skill 由 Claude Code 維護 | 最後更新: 2026-03-05 (v4.0)*
